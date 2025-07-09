import anthropic
import subprocess
import tempfile
import os
import json
import time
import re
import glob
import shutil

def cleanup_workspace():
    """Clean up workspace before running vectorizer"""
    print("Starting cleanup...")
    
    # 1. Delete all .o files in workspace
    workspace_dir = os.path.expanduser("~/workspace")
    o_files = glob.glob(os.path.join(workspace_dir, "**/*.o"), recursive=True)
    for o_file in o_files:
        try:
            os.remove(o_file)
            print(f"Deleted: {o_file}")
        except OSError as e:
            print(f"Error deleting {o_file}: {e}")
    
    # 2. Clean tsvc_results directory
    tsvc_results_dir = os.path.join(workspace_dir, "tsvc_results")
    if os.path.exists(tsvc_results_dir):
        try:
            shutil.rmtree(tsvc_results_dir)
            os.makedirs(tsvc_results_dir)
            print(f"Cleaned directory: {tsvc_results_dir}")
        except OSError as e:
            print(f"Error cleaning {tsvc_results_dir}: {e}")
    
    # 3. Clean tsvc_vectorized_attempts directory
    tsvc_attempts_dir = os.path.join(workspace_dir, "tsvc_vectorized_attempts")
    if os.path.exists(tsvc_attempts_dir):
        try:
            shutil.rmtree(tsvc_attempts_dir)
            os.makedirs(tsvc_attempts_dir)
            print(f"Cleaned directory: {tsvc_attempts_dir}")
        except OSError as e:
            print(f"Error cleaning {tsvc_attempts_dir}: {e}")
    
    # 4. Delete tsvc_vectorization_results.json file
    results_file = os.path.join(workspace_dir, "tsvc_vectorization_results.json")
    if os.path.exists(results_file):
        try:
            os.remove(results_file)
            print(f"Deleted: {results_file}")
        except OSError as e:
            print(f"Error deleting {results_file}: {e}")
    
    print("Cleanup completed.\n")

class TSVCVectorizerExperiment:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 3
        self.temperature = 0.2  # Lower temperature for more consistent code generation
        self.results = {}
        
        # Extract test functions - will be populated by run_experiment
        self.test_functions = {}
    
    def extract_tsvc_functions(self, function_names=None):
        """Extract function code from tsvc.c file"""
        if function_names is None:
            function_names = ['s114']  # Default to s114 only
        
        functions = {}
        
        # Read tsvc.c file
        tsvc_content = None
        try:
            # Try current directory first
            with open('tsvc.c', 'r') as f:
                tsvc_content = f.read()
        except FileNotFoundError:
            try:
                # Try relative path from workspace
                with open('TSVC_2/src/tsvc.c', 'r') as f:
                    tsvc_content = f.read()
            except FileNotFoundError:
                print("Error: tsvc.c not found in current directory or TSVC_2/src/")
                raise FileNotFoundError("tsvc.c file is required for function extraction")
        
        import re
        
        for func_name in function_names:
            # Extract function definition
            func_pattern = rf'real_t {func_name}\(struct args_t \* func_args\)\s*\{{(.*?)\n\}}'
            func_match = re.search(func_pattern, tsvc_content, re.DOTALL)
            
            if func_match:
                full_function = f"real_t {func_name}(struct args_t * func_args)\n{{\n{func_match.group(1)}\n}}"
                func_body = func_match.group(1)
                
                # Debug: print function body
                print(f"\nDEBUG: Function body for {func_name}:")
                print("=" * 50)
                print(func_body[:500] + "..." if len(func_body) > 500 else func_body)
                print("=" * 50)
                
                # Find ALL for loops, including nested ones
                # Use regex to find all for loop headers - handle nested parentheses
                all_for_headers = []
                
                # Find all 'for' keywords first
                for_positions = []
                for match in re.finditer(r'\bfor\s*\(', func_body):
                    for_positions.append(match.start())
                
                # For each 'for' position, find the complete header by counting parentheses
                for start_pos in for_positions:
                    # Find the opening parenthesis
                    paren_start = func_body.find('(', start_pos)
                    if paren_start == -1:
                        continue
                    
                    # Count parentheses to find the matching closing one
                    paren_count = 0
                    pos = paren_start
                    while pos < len(func_body):
                        if func_body[pos] == '(':
                            paren_count += 1
                        elif func_body[pos] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                # Found the complete for header
                                header = func_body[start_pos:pos+1]
                                all_for_headers.append({
                                    'header': header,
                                    'start': start_pos,
                                    'end': pos+1
                                })
                                break
                        pos += 1
                
                print(f"\nDEBUG: Found {len(all_for_headers)} for loop headers:")
                for h in all_for_headers:
                    print(f"  {h['header']}")
                
                # Now extract complete loops
                loops = []
                for header_info in all_for_headers:
                    # Find the opening brace after this for statement
                    pos = header_info['end']
                    while pos < len(func_body) and func_body[pos] in ' \t\n':
                        pos += 1
                    
                    if pos < len(func_body) and func_body[pos] == '{':
                        # Extract the complete loop by counting braces
                        brace_count = 0
                        start_pos = header_info['start']
                        i = pos
                        
                        while i < len(func_body):
                            if func_body[i] == '{':
                                brace_count += 1
                            elif func_body[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    loop_text = func_body[start_pos:i+1]
                                    loops.append({
                                        'text': loop_text,
                                        'header': header_info['header'],
                                        'start': start_pos,
                                        'end': i+1,
                                        'depth': func_body[:start_pos].count('for')  # Rough depth estimate
                                    })
                                    break
                            i += 1
                
                print(f"\nDEBUG: Extracted {len(loops)} complete loops")
                
                # Now find the computational loop
                # For nested structures (like s114), we want the complete nested structure
                # For single loops (like s1113), we want just that loop
                
                core_loop = None
                
                # Sort loops by depth (outermost first)
                loops.sort(key=lambda x: x['depth'])
                
                # Look for computational loops
                computational_loops = []
                for loop in loops:
                    # Skip benchmark loops (outer loops with 'nl' variable)
                    if 'nl' in loop['header']:
                        continue
                    
                    # Check if it has array operations (this is the main criteria)
                    if re.search(r'\w+\[[^\]]+\]', loop['text']):
                        # Don't skip loops that contain dummy calls - they might still be computational
                        # The dummy call is typically at the end and doesn't affect the core computation
                        computational_loops.append(loop)
                
                print(f"\nDEBUG: Found {len(computational_loops)} computational loops")
                
                if computational_loops:
                    # For nested loops, we want the outermost computational loop
                    # that contains all the nested computational loops
                    if len(computational_loops) > 1:
                        # Check if loops are nested
                        outermost = computational_loops[0]
                        all_nested = True
                        for other in computational_loops[1:]:
                            if not (other['start'] > outermost['start'] and other['end'] < outermost['end']):
                                all_nested = False
                                break
                        
                        if all_nested:
                            # Use the outermost computational loop (contains all nested ones)
                            core_loop = outermost['text']
                            print(f"\nDEBUG: Selected outermost computational loop (nested structure)")
                        else:
                            # Not all nested, pick the last one (likely the innermost)
                            core_loop = computational_loops[-1]['text']
                            print(f"\nDEBUG: Selected last computational loop")
                    else:
                        # Single computational loop
                        core_loop = computational_loops[0]['text']
                        print(f"\nDEBUG: Selected single computational loop")
                
                if not core_loop:
                    core_loop = "// No computational loop found"
                    print("\nDEBUG: No computational loop found!")
                
                # Add missing variable declarations to the core loop
                if core_loop and core_loop != "// No computational loop found":
                    core_loop = self.add_missing_declarations(core_loop, func_body)
                
                # Clean up the loop
                if core_loop and core_loop != "// No computational loop found":
                    # Normalize whitespace
                    lines = core_loop.split('\n')
                    cleaned_lines = []
                    indent_level = 0
                    for line in lines:
                        stripped = line.strip()
                        if stripped:
                            if '}' in stripped and '{' not in stripped:
                                # Line with closing brace(s)
                                closes = stripped.count('}')
                                indent_level -= closes
                                cleaned_lines.append('    ' * indent_level + stripped)
                            elif '{' in stripped and '}' not in stripped:
                                # Line with opening brace(s)
                                cleaned_lines.append('    ' * indent_level + stripped)
                                opens = stripped.count('{')
                                indent_level += opens
                            elif '{' in stripped and '}' in stripped:
                                # Line with both
                                cleaned_lines.append('    ' * indent_level + stripped)
                                indent_level += stripped.count('{') - stripped.count('}')
                            else:
                                # Regular line
                                cleaned_lines.append('    ' * indent_level + stripped)
                    
                    core_loop = '\n'.join(cleaned_lines)
                
                # Determine category based on comments and code patterns
                category = 'unknown'
                if 'nonlinear dependence' in func_body:
                    category = 'nonlinear_dependence'
                elif 'linear dependence' in func_body:
                    category = 'linear_dependence'
                elif 'induction variable' in func_body:
                    category = 'induction variable recognition'
                elif 'control flow' in func_body:
                    category = 'control_flow'
                elif 'statement reordering' in func_body:
                    category = 'statement_reordering'
                elif 'loop distribution' in func_body:
                    category = 'loop_distribution'
                elif 'recurrences' in func_body:
                    category = 'recurrences'
                elif 'if (' in func_body or 'condition' in func_body.lower():
                    category = 'condition'
                
                functions[func_name] = {
                    'code': full_function,
                    'core_loop': core_loop,
                    'category': category
                }
                
                # Final output
                print(f"\nExtracted core loop for {func_name}:")
                print(core_loop)
                print()
                
            else:
                print(f"Function {func_name} not found in tsvc.c")
        
        return functions
    
    def add_missing_declarations(self, core_loop, func_body):
        """Add missing variable declarations to the extracted loop"""
        import re
        
        # Find variables used in the core loop
        used_vars = set()
        used_arrays = set()
        
        # Look for variable usage patterns (assignments, array indices, etc.)
        var_patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\+\+',  # k++
            r'\+\+\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',  # ++k
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*--',    # k--
            r'--\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',    # --k
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=',     # k =
            r'=\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',     # = k
            r'\[\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\]', # [k]
            r'\[\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[-+]', # [k-1] or [k+1]
        ]
        
        # Look for array usage patterns
        array_patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\[',    # array[index]
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, core_loop)
            for match in matches:
                # Skip common array names and loop variables that are typically declared in for loops
                # But be smarter about 'i' and 'j' - only skip them if they're actually declared in for loops
                if match in ['a', 'b', 'c', 'd', 'e', 'aa', 'bb', 'cc', 'nl']:
                    continue
                elif match in ['i', 'j']:
                    # Check if this variable is declared in a for loop in the core loop
                    for_loop_pattern = rf'for\s*\([^)]*\b{match}\s*='
                    if not re.search(for_loop_pattern, core_loop):
                        # Not declared in a for loop, so it needs declaration
                        used_vars.add(match)
                else:
                    used_vars.add(match)
        
        for pattern in array_patterns:
            matches = re.findall(pattern, core_loop)
            for match in matches:
                # Check if this might be a global array (not a simple variable)
                if '_' in match or len(match) > 2:  # Likely global arrays like flat_2d_array
                    used_arrays.add(match)
        
        print(f"DEBUG: Variables used in core loop: {used_vars}")
        print(f"DEBUG: Arrays used in core loop: {used_arrays}")
        
        # Find declarations of these variables in the function body
        declarations = []
        
        # Handle regular variables
        for var in used_vars:
            # Look for variable declarations or initializations
            # Pattern 1: int k; or int k = value;
            decl_pattern1 = rf'\b(int|real_t|float)\s+{var}\s*(?:=\s*[^;]+)?;'
            # Pattern 2: k = value; (initialization without declaration)
            decl_pattern2 = rf'\b{var}\s*=\s*([^;]+);'
            
            # First, search in the entire function body for declaration
            func_decl_match = re.search(decl_pattern1, func_body)
            if func_decl_match:
                print(f"DEBUG: Found declaration for {var}: {func_decl_match.group(0)}")
                
                # Look for initialization in the function body
                # Find all assignments to this variable (but exclude increment/decrement)
                init_matches = re.findall(rf'\b{var}\s*=\s*([^;]+);', func_body)
                if init_matches:
                    # Filter out increment/decrement operations
                    valid_inits = []
                    for init in init_matches:
                        init = init.strip()
                        # Skip if it's an increment/decrement or complex expression
                        if not re.match(r'^.*[\+\-]{2}.*$', init) and not re.match(r'^.*[\+\-]\s*\d+$', init):
                            valid_inits.append(init)
                    
                    if valid_inits:
                        # Use the first valid initialization value found
                        init_value = valid_inits[0]
                        declarations.append(f"    int {var} = {init_value};")
                        print(f"DEBUG: Found initialization for {var} = {init_value}")
                    else:
                        # No valid initialization found, use default
                        declarations.append(f"    int {var} = 1;")
                        print(f"DEBUG: No valid initialization found for {var}, using default")
                else:
                    # No initialization found, use default
                    declarations.append(f"    int {var} = 1;")
                    print(f"DEBUG: No initialization found for {var}, using default")
            else:
                # No declaration found, check if it's just initialized
                init_matches = re.findall(rf'\b{var}\s*=\s*([^;]+);', func_body)
                if init_matches:
                    # Filter out increment/decrement operations
                    valid_inits = []
                    for init in init_matches:
                        init = init.strip()
                        # Skip if it's an increment/decrement or complex expression
                        if not re.match(r'^.*[\+\-]{2}.*$', init) and not re.match(r'^.*[\+\-]\s*\d+$', init):
                            valid_inits.append(init)
                    
                    if valid_inits:
                        # Use the first valid initialization value found
                        init_value = valid_inits[0]
                        declarations.append(f"    int {var} = {init_value};")
                        print(f"DEBUG: Found initialization without declaration for {var} = {init_value}")
                    else:
                        # Variable not found anywhere, add default declaration
                        declarations.append(f"    int {var} = 1;")
                        print(f"DEBUG: Variable {var} not found, adding default declaration")
                else:
                    # Variable not found anywhere, add default declaration
                    declarations.append(f"    int {var} = 1;")
                    print(f"DEBUG: Variable {var} not found, adding default declaration")
        
        # Handle global arrays - these don't need declarations but we should note them
        for array in used_arrays:
            print(f"DEBUG: Global array {array} detected - no declaration needed")
        
        # Add declarations before the core loop (not inside it)
        if declarations:
            print(f"DEBUG: Adding declarations: {declarations}")
            # Prepend declarations before the loop
            core_loop = '\n'.join(declarations) + '\n' + core_loop
        
        return core_loop
    
    def get_clang_vectorization_report(self, func_name, source_code):
        """Get Clang's vectorization analysis report"""
        import re
        
        # Extract just the core loop for analysis
        core_loop = self.test_functions[func_name]['core_loop']
        
        # Check if the loop has dependencies on outer variables (like 'i' in inner loops)
        # Look for common patterns like "j < i" or array accesses with 'i'
        has_outer_dependency = False
        if re.search(r'\b[ij]\s*<\s*[ij]\b', core_loop) and 'for' in core_loop:
            # This looks like an inner loop depending on outer loop variable
            has_outer_dependency = True
        
        # Check if flat_2d_array is used
        uses_flat_array = 'flat_2d_array' in core_loop
        
        # Add flat_2d_array declaration if needed
        flat_array_decl = ""
        if uses_flat_array:
            flat_array_decl = "real_t flat_2d_array[LEN_2D*LEN_2D];"
        
        # Build test program
        if has_outer_dependency:
            # Wrap in a dummy outer loop
            test_program = f"""
#include <stdio.h>

#define LEN_1D 32000
#define LEN_2D 256
typedef float real_t;

// Global arrays
real_t a[LEN_1D], b[LEN_1D];
real_t aa[LEN_2D][LEN_2D], bb[LEN_2D][LEN_2D], cc[LEN_2D][LEN_2D];
{flat_array_decl}

void test_function() {{
    // Dummy outer loop for context
    for (int i = 0; i < LEN_2D; i++) {{
        {core_loop}
    }}
}}

int main() {{
    return 0;
}}
"""
        else:
            # Single loop or self-contained nested loop
            test_program = f"""
#include <stdio.h>

#define LEN_1D 32000
#define LEN_2D 256
typedef float real_t;

// Global arrays
real_t a[LEN_1D], b[LEN_1D], c[LEN_1D], d[LEN_1D], e[LEN_1D];
real_t aa[LEN_2D][LEN_2D], bb[LEN_2D][LEN_2D], cc[LEN_2D][LEN_2D];
{flat_array_decl}

void test_function() {{
    {core_loop}
}}

int main() {{
    return 0;
}}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_program)
            temp_file = f.name
        
        try:
            # Run Clang with vectorization report flags
            result = subprocess.run([
                'clang',
                '-O3',
                '-mavx2',
                '-Rpass-analysis=loop-vectorize',
                '-Rpass-missed=loop-vectorize',
                '-fvectorize',
                '-c',
                temp_file
            ], capture_output=True, text=True)
            
            # Get the report
            report = result.stderr
            
            # If compilation failed, return simple analysis
            if result.returncode != 0:
                print(f"Clang compilation failed:\n{report}")
                return self.simple_dependency_analysis(func_name)
            
            # Just return the full report - let the LLM parse it
            return report
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def simple_dependency_analysis(self, func_name):
        """Simple fallback analysis when Clang fails"""
        return f"Clang analysis failed for {func_name} - unable to determine vectorization status"
    
    def get_system_prompt(self, func_name, loop_description):
        """Generate the system prompt for vectorization"""
        return f"""You are an expert in SIMD vectorization using AVX2 intrinsics.

Please eliminate any dependencies and generate optimized vectorized C code that:

Uses AVX2 intrinsics (mm256* functions)
Targets 8-element vectors for float arrays
Handles the identified dependencies correctly
Ensures semantic equivalence with original code

Generate a complete C function named `{func_name}_vectorized` that vectorizes this {loop_description} using AVX2 intrinsics. The function should:
- Take no parameters (uses global arrays aa, bb, cc for 2D arrays or a, b, c, d, e for 1D arrays)
- Include any necessary headers like #include <immintrin.h>
- If it's a nested loop, vectorize the appropriate loop level

Always generate only the vectorized function implementation.

When doing vectorization analysis, follow these steps:
1. Simplify the case by setting the loop iterations to a small number. 
2. Enumerate the process as the code written, identify which variable is refered as its original value and which one is refered as its updated value.
3. Variables that use original values load operand directly from memory, then compute, then store the values. 
   After that, variables that use updated value load from memory, then compute, finally store the values.
4. Making necessary unlooping/loop interchanging/statement reordering based on step 3.
5. Understand the pattern, then generate the actual vectorized code for the full loop range."""
    
    def vectorizer_agent(self, source_code, func_name, clang_analysis, feedback=None):
        """Generate vectorized code using Anthropic API"""
        
        # Check if this is a nested loop that needs context
        needs_outer_context = 'j < i' in source_code or ('i' in source_code and 'for' in source_code and 'int i' not in source_code)
        
        if needs_outer_context:
            # Provide the nested loop context
            source_with_context = f"""for (int i = 0; i < LEN_2D; i++) {{
    {source_code}
}}"""
            loop_description = f"nested loop where the inner loop is:\n{source_code}\nand it's inside an outer loop over i"
        else:
            source_with_context = source_code
            loop_description = f"loop:\n{source_code}"
        
        # Create generic prompts without function-specific logic
        if feedback is None:
            # Initial attempt
            user_message = f"""
```c
{source_with_context}
```
"""
        else:
            # Repair attempt - include all relevant error information
            if feedback['error_type'] == 'compilation':
                user_message = f"""
{feedback['error_message']}
"""
            elif feedback['error_type'] == 'correctness':
                user_message = f"""
{feedback['test_output']}
"""
            elif feedback['error_type'] == 'not_vectorized':
                user_message = f"""Previous attempt failed to understand that the code can be vectorized.

Here's what you tried before:
{feedback['previous_code']}
"""
            else:
                # Generic fallback
                user_message = f"""The previous vectorized function had this error:
{feedback.get('error_message', 'Unknown error')}
{feedback.get('test_output', '')}
{feedback.get('hint', '')}

Generate a corrected `{func_name}_vectorized` function that:
- Fixes the error
- Takes no parameters (uses global arrays)  
- Correctly vectorizes the {loop_description}

Output only the C function, no explanations."""
        
        system_prompt = self.get_system_prompt(func_name, loop_description)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"API error: {e}")
            return None
    
    def check_if_vectorized(self, code):
        """Check if the code actually contains vectorization"""
        vectorization_indicators = [
            '_mm256_',  # AVX2 intrinsics
            '_mm_',     # SSE intrinsics
            '__m256',   # AVX2 vector type
            '__m128',   # SSE vector type
            'vmovups',  # Assembly instructions
            'vaddps',
        ]
        
        # Check for presence of vector intrinsics
        for indicator in vectorization_indicators:
            if indicator in code:
                return True, "Found vector intrinsics"
        
        # Only if no intrinsics found, then it's not vectorized
        return False, "No vector intrinsics found"
    
    def create_test_harness(self, func_name):
        """Create generic test harness for any TSVC function"""
        # Check which arrays are used in the core loop
        core_loop = self.test_functions[func_name]['core_loop']
        
        # Debug print
        print(f"DEBUG: Creating test harness for {func_name}")
        print(f"Core loop: {core_loop[:100]}...")
        
        # Determine if we need 1D or 2D arrays based on what's in the loop
        uses_2d = 'aa[' in core_loop or 'bb[' in core_loop or 'cc[' in core_loop
        uses_1d = 'a[' in core_loop or 'b[' in core_loop or 'c[' in core_loop or 'd[' in core_loop or 'e[' in core_loop
        
        print(f"Uses 2D arrays: {uses_2d}, Uses 1D arrays: {uses_1d}")
        
        if uses_2d:
            # 2D array test harness (even if it also uses 1D arrays)
            return self._create_2d_test_harness(func_name)
        else:
            # 1D array test harness (default)
            return self._create_1d_test_harness()
    
    def _create_1d_test_harness(self):
        """Create test harness for functions using 1D arrays"""
        return """
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include <math.h>
#include <string.h>

#define LEN_1D 32
#define LEN_2D 16
#define real_t float

// Global arrays for testing
__attribute__((aligned(32))) real_t a[LEN_1D];
__attribute__((aligned(32))) real_t b[LEN_1D];
__attribute__((aligned(32))) real_t c[LEN_1D];
__attribute__((aligned(32))) real_t d[LEN_1D];
__attribute__((aligned(32))) real_t e[LEN_1D];

// Original implementation
void FUNC_NAME_original() {
    CORE_LOOP_PLACEHOLDER
}

// Vectorized function will be inserted here
__VECTORIZED_CODE__

int main() {
    // Initialize arrays with alternating positive/negative values
    for (int i = 0; i < LEN_1D; i++) {
        int sign = (i % 2 == 0) ? 1 : -1;
        a[i] = (real_t)(sign * i);
        b[i] = (real_t)(sign * (i + 1));
        c[i] = (real_t)(sign * (i + 2));
        d[i] = (real_t)(sign * (i + 3));
        e[i] = (real_t)(sign * (i + 4));
    }
    
    // Make copies for comparison
    real_t a_original[LEN_1D], b_original[LEN_1D], c_original[LEN_1D];
    real_t d_original[LEN_1D], e_original[LEN_1D];
    real_t a_vectorized[LEN_1D], b_vectorized[LEN_1D], c_vectorized[LEN_1D];
    real_t d_vectorized[LEN_1D], e_vectorized[LEN_1D];
    
    memcpy(a_original, a, sizeof(a));
    memcpy(b_original, b, sizeof(b));
    memcpy(c_original, c, sizeof(c));
    memcpy(d_original, d, sizeof(d));
    memcpy(e_original, e, sizeof(e));
    
    memcpy(a_vectorized, a, sizeof(a));
    memcpy(b_vectorized, b, sizeof(b));
    memcpy(c_vectorized, c, sizeof(c));
    memcpy(d_vectorized, d, sizeof(d));
    memcpy(e_vectorized, e, sizeof(e));
    
    // Run original
    memcpy(a, a_original, sizeof(a));
    memcpy(b, b_original, sizeof(b));
    memcpy(c, c_original, sizeof(c));
    memcpy(d, d_original, sizeof(d));
    memcpy(e, e_original, sizeof(e));
    FUNC_NAME_original();
    memcpy(a_original, a, sizeof(a));
    
    // Run vectorized
    memcpy(a, a_vectorized, sizeof(a));
    memcpy(b, b_vectorized, sizeof(b));
    memcpy(c, c_vectorized, sizeof(c));
    memcpy(d, d_vectorized, sizeof(d));
    memcpy(e, e_vectorized, sizeof(e));
    FUNC_NAME_vectorized();
    memcpy(a_vectorized, a, sizeof(a));
    
    // Compare results (only check array 'a' as it's typically the output)
    int match = 1;
    for (int i = 0; i < LEN_1D; i++) {
        if (fabs(a_original[i] - a_vectorized[i]) > 1e-5) {
            printf("Mismatch at a[%d]: original=%f, vectorized=%f\\n",
                   i, a_original[i], a_vectorized[i]);
            match = 0;
        }
    }
    
    if (match) {
        printf("SUCCESS\\n");
        return 0;
    } else {
        return 1;
    }
}
"""
    
    def _create_2d_test_harness(self, func_name):
        """Create test harness for functions using 2D arrays"""
        # Check if the core loop needs an outer loop context
        core_loop = self.test_functions.get(func_name, {}).get('core_loop', '')
        needs_outer_loop = 'j < i' in core_loop or ('i' in core_loop and 'for' in core_loop and 'int i' not in core_loop)
        
        # Check if flat_2d_array is used
        uses_flat_array = 'flat_2d_array' in core_loop
        
        if needs_outer_loop:
            loop_placeholder = """for (int i = 0; i < LEN_2D; i++) {
        CORE_LOOP_PLACEHOLDER
    }"""
        else:
            loop_placeholder = "CORE_LOOP_PLACEHOLDER"
        
        # Add flat_2d_array declaration if needed
        flat_array_decl = ""
        flat_array_init = ""
        flat_array_copy = ""
        flat_array_compare = ""
        
        if uses_flat_array:
            flat_array_decl = "__attribute__((aligned(32))) real_t flat_2d_array[LEN_2D*LEN_2D];"
            flat_array_init = """
    // Initialize flat 2D array
    for (int i = 0; i < LEN_2D*LEN_2D; i++) {
        flat_2d_array[i] = (real_t)(i + 10);
    }"""
            flat_array_copy = """
    // Make copies for flat array comparison
    real_t flat_2d_array_original[LEN_2D*LEN_2D];
    real_t flat_2d_array_vectorized[LEN_2D*LEN_2D];
    
    memcpy(flat_2d_array_original, flat_2d_array, sizeof(flat_2d_array));
    memcpy(flat_2d_array_vectorized, flat_2d_array, sizeof(flat_2d_array));
    
    // Run original with flat array
    memcpy(flat_2d_array, flat_2d_array_original, sizeof(flat_2d_array));"""
            
            flat_array_compare = """
    // Also compare flat array if it was modified
    for (int i = 0; i < LEN_2D*LEN_2D; i++) {
        if (fabs(flat_2d_array_original[i] - flat_2d_array_vectorized[i]) > 1e-5) {
            printf("Mismatch at flat_2d_array[%d]: original=%f, vectorized=%f\\n",
                   i, flat_2d_array_original[i], flat_2d_array_vectorized[i]);
            match = 0;
        }
    }"""
        
        return f"""
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include <math.h>
#include <string.h>

#define LEN_1D 32
#define LEN_2D 16
#define real_t float

// Global arrays for testing - both 1D and 2D
__attribute__((aligned(32))) real_t a[LEN_1D];
__attribute__((aligned(32))) real_t b[LEN_1D];
__attribute__((aligned(32))) real_t c[LEN_1D];
__attribute__((aligned(32))) real_t d[LEN_1D];
__attribute__((aligned(32))) real_t e[LEN_1D];
__attribute__((aligned(32))) real_t aa[LEN_2D][LEN_2D];
__attribute__((aligned(32))) real_t bb[LEN_2D][LEN_2D];
__attribute__((aligned(32))) real_t cc[LEN_2D][LEN_2D];
{flat_array_decl}

// Original implementation
void FUNC_NAME_original() {{
    {loop_placeholder}
}}

// Vectorized function will be inserted here
__VECTORIZED_CODE__

int main() {{
    // Initialize 1D arrays with alternating positive/negative values
    for (int i = 0; i < LEN_1D; i++) {{
        int sign = (i % 2 == 0) ? 1 : -1;
        a[i] = (real_t)(sign * i);
        b[i] = (real_t)(sign * (i + 1));
        c[i] = (real_t)(sign * (i + 2));
        d[i] = (real_t)(sign * (i + 3));
        e[i] = (real_t)(sign * (i + 4));
    }}
    
    // Initialize 2D arrays with alternating positive/negative values
    for (int i = 0; i < LEN_2D; i++) {{
        for (int j = 0; j < LEN_2D; j++) {{
            int sign = ((i + j) % 2 == 0) ? 1 : -1;
            aa[i][j] = (real_t)(sign * (i * LEN_2D + j));
            bb[i][j] = (real_t)(sign * (i + j * 2 + 1));
            cc[i][j] = (real_t)(sign * (i - j + 2));
        }}
    }}{flat_array_init}
    
    // Make copies for comparison (2D arrays)
    real_t bb_original[LEN_2D][LEN_2D];
    real_t bb_vectorized[LEN_2D][LEN_2D];
    
    memcpy(bb_original, bb, sizeof(bb));
    memcpy(bb_vectorized, bb, sizeof(bb));{flat_array_copy}
    
    // Run original
    memcpy(bb, bb_original, sizeof(bb));
    FUNC_NAME_original();
    memcpy(bb_original, bb, sizeof(bb));
    
    // Run vectorized
    memcpy(bb, bb_vectorized, sizeof(bb));
    FUNC_NAME_vectorized();
    memcpy(bb_vectorized, bb, sizeof(bb));
    
    // Compare results (bb array is typically the output for these functions)
    int match = 1;
    for (int i = 0; i < LEN_2D; i++) {{
        for (int j = 0; j < LEN_2D; j++) {{
            if (fabs(bb_original[i][j] - bb_vectorized[i][j]) > 1e-5) {{
                printf("Mismatch at bb[%d][%d]: original=%f, vectorized=%f\\n",
                       i, j, bb_original[i][j], bb_vectorized[i][j]);
                match = 0;
            }}
        }}
    }}{flat_array_compare}
    
    if (match) {{
        printf("SUCCESS\\n");
        return 0;
    }} else {{
        return 1;
    }}
}}
"""
    
    def extract_and_clean_function(self, vectorized_code):
        """Extract and clean the function from LLM response"""
        # Find all code blocks
        code_blocks = re.findall(r'```c?\n(.*?)\n```', vectorized_code, re.DOTALL)
        
        if code_blocks:
            # Look for the block that contains the actual vectorized function
            for block in reversed(code_blocks):  # Check from last to first
                # Check if this block contains vector intrinsics or the function signature
                if '_vectorized' in block or '_mm256_' in block or '__m256' in block:
                    vectorized_func = block
                    break
            else:
                # If no vectorized function found, take the last code block
                vectorized_func = code_blocks[-1]
        else:
            # No code blocks found, try to extract function directly
            func_pattern = r'((?:void|real_t)\s+\w+_vectorized.*?^\})'
            func_match = re.search(func_pattern, vectorized_code, re.DOTALL | re.MULTILINE)
            if func_match:
                vectorized_func = func_match.group(0)
            else:
                # As last resort, assume the whole response is the function
                vectorized_func = vectorized_code
        
        # Clean up common LLM mistakes
        lines = vectorized_func.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip enumeration examples
            if re.match(r'^\s*i\s*=\s*\d+\s*:', line):
                continue
            if re.match(r'^\s*\d+\s*:', line):
                continue
            # Skip lines that are just comments about execution
            if re.match(r'^\s*-\s*i=\d+:', line):
                continue
            cleaned_lines.append(line)
        
        # Fix common formatting issues in vector intrinsics
        vectorized_func = '\n'.join(cleaned_lines)
        # Fix asterisk issues with intrinsics (LLM sometimes uses *mm256* instead of _mm256_)
        vectorized_func = re.sub(r'\*mm256\*', '_mm256_', vectorized_func)
        
        return vectorized_func
    
    def compiler_tester_agent(self, func_name, func_data, vectorized_code, iteration=1):
        """Test the vectorized code for correctness"""
        
        # First check if the code is actually vectorized
        is_vectorized, vec_message = self.check_if_vectorized(vectorized_code)
        if not is_vectorized:
            return {
                'success': False,
                'error_type': 'not_vectorized',
                'error_message': vec_message,
                'test_output': None,
                'hint': 'The code does not contain vector intrinsics. Try to actually vectorize the loop.'
            }
        
        # Extract and clean the function
        vectorized_func = self.extract_and_clean_function(vectorized_code)
        
        # Ensure correct function name
        if f'{func_name}_vectorized' not in vectorized_func:
            vectorized_func = re.sub(r'void\s+\w+\s*\(', f'void {func_name}_vectorized(', vectorized_func)
        
        # Create test harness
        test_template = self.create_test_harness(func_name)
        
        # For nested loops, we need special handling
        core_loop = func_data['core_loop']
        if 'j < i' in core_loop or ('i' in core_loop and 'for' in core_loop and 'int i' not in core_loop):
            # This is an inner loop that needs outer context
            # The template already has the outer loop, so just replace the inner part
            test_code = test_template.replace('FUNC_NAME', func_name)
            test_code = test_code.replace('CORE_LOOP_PLACEHOLDER', core_loop.strip())
        else:
            # Normal replacement
            test_code = test_template.replace('FUNC_NAME', func_name)
            test_code = test_code.replace('CORE_LOOP_PLACEHOLDER', core_loop)
        
        test_code = test_code.replace('__VECTORIZED_CODE__', vectorized_func)
        
        # Save files for debugging
        os.makedirs(f"tsvc_vectorized_attempts/{func_name}", exist_ok=True)
        
        with open(f"tsvc_vectorized_attempts/{func_name}/test_harness.c", 'w') as f:
            f.write(test_code)
        
        with open(f"tsvc_vectorized_attempts/{func_name}/extracted_function_{iteration}.c", 'w') as f:
            f.write(vectorized_func)
        
        # Compile and test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Compile
            exe_file = temp_file.replace('.c', '')
            compile_result = subprocess.run(
                ['gcc', '-mavx2', '-mfma', '-lm', '-o', exe_file, temp_file],
                capture_output=True, text=True
            )
            
            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'error_type': 'compilation',
                    'error_message': compile_result.stderr,
                    'test_output': None,
                    'hint': 'Check syntax, missing headers, or incorrect intrinsic usage'
                }
            
            # Run test
            run_result = subprocess.run(
                [exe_file], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if run_result.returncode == 0:
                return {
                    'success': True,
                    'error_type': None,
                    'error_message': None,
                    'test_output': run_result.stdout
                }
            else:
                # Analyze the error
                hint = self.analyze_error(run_result.stdout, func_name)
                return {
                    'success': False,
                    'error_type': 'correctness',
                    'error_message': 'Output mismatch',
                    'test_output': run_result.stdout,
                    'hint': hint
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_type': 'timeout',
                'error_message': 'Execution timeout',
                'test_output': None,
                'hint': 'Possible infinite loop in vectorized code'
            }
        finally:
            # Cleanup
            for file_path in [temp_file, exe_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def analyze_error(self, error_output, func_name):
        """Analyze test output to provide hints"""
        # For correctness errors, the output shows mismatches
        if "Mismatch" in error_output:
            # Extract some mismatch details
            mismatch_lines = [line for line in error_output.split('\n') if 'Mismatch' in line][:3]
            mismatch_info = '\n'.join(mismatch_lines)
            return f"The vectorized version produces different results:\n{mismatch_info}"
        
        elif "Segmentation fault" in error_output:
            return "Memory access error. Check array bounds in vector operations."
        
        else:
            # Generic hint - just show what went wrong
            return f"Test failed with output:\n{error_output[:200]}"
    
    def save_iteration_data(self, func_name, iteration, vectorized_code, source_code, feedback, clang_report):
        """Save all data from this iteration for debugging"""
        os.makedirs(f"tsvc_vectorized_attempts/{func_name}", exist_ok=True)
        
        # Save LLM response
        with open(f"tsvc_vectorized_attempts/{func_name}/attempt_{iteration}.c", 'w') as f:
            f.write(vectorized_code)
        
        # Build the complete prompt that was sent to LLM
        # Determine loop description for the system prompt
        if feedback is None:
            loop_description = f"loop:\n{source_code}"
        else:
            # For repair attempts, we need to reconstruct the loop description
            # This is a simplified version since we don't have all the context here
            loop_description = "loop"
        
        system_prompt = self.get_system_prompt(func_name, loop_description)
        
        if feedback is None:
            user_prompt = f"""

```c
{source_code}
```

"""
        else:
            # Repair attempt - include all relevant error information
            if feedback['error_type'] == 'compilation':
                user_prompt = f"""
{feedback['error_message']}
"""
            elif feedback['error_type'] == 'correctness':
                user_prompt = f"""
{feedback['test_output']}
"""
            elif feedback['error_type'] == 'not_vectorized':
                user_prompt = f"""Previous attempt failed to understand that the code can be vectorized.

Here's what you tried before:
{feedback.get('previous_code', 'Code not available')}
"""
            else:
                # Generic fallback
                user_prompt = f"""The previous vectorized function had this error:
{feedback.get('error_message', 'Unknown error')}
{feedback.get('test_output', '')}
{feedback.get('hint', '')}
"""
        
        # Save the complete prompt
        with open(f"tsvc_vectorized_attempts/{func_name}/prompt_{iteration}.txt", 'w') as f:
            f.write(f"Iteration {iteration} Prompt\n{'='*50}\n\n")
            f.write(f"SYSTEM PROMPT:\n{'-'*50}\n{system_prompt}\n\n")
            f.write(f"USER PROMPT:\n{'-'*50}\n{user_prompt}\n")
    
    def run_vectorization_fsm(self, func_name, func_data):
        """Main FSM orchestration for a single function"""
        print(f"\n{'='*60}")
        print(f"Vectorizing {func_name} ({func_data['category']})")
        print(f"{'='*60}")
        
        # Get Clang analysis
        print("\nGetting Clang analysis...")
        clang_report = self.get_clang_vectorization_report(func_name, func_data['code'])
        
        # Just use the full report as is
        print(f"Clang analysis:\n{clang_report}")
        
        # Use core loop for vectorization
        source_to_vectorize = func_data['core_loop']
        
        attempts = []
        feedback = None
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\nIteration {iteration}:")
            
            # Generate/repair code
            print("  - Generating vectorized code...")
            vectorized_code = self.vectorizer_agent(
                source_to_vectorize, 
                func_name, 
                clang_report,
                feedback
            )
            
            if vectorized_code is None:
                print("  - API error, stopping")
                break
            
            # Save iteration data
            self.save_iteration_data(func_name, iteration, vectorized_code, source_to_vectorize, feedback, clang_report)
            
            # Test the code
            print("  - Testing vectorized code...")
            test_result = self.compiler_tester_agent(func_name, func_data, vectorized_code, iteration)
            
            attempts.append({
                'iteration': iteration,
                'success': test_result['success'],
                'error_type': test_result['error_type'],
                'vectorized_code': vectorized_code
            })
            
            if test_result['success']:
                print(f"  ✓ SUCCESS! Correct vectorization achieved.")
                break
            else:
                print(f"  ✗ FAILED: {test_result['error_type']}")
                if test_result['error_type'] == 'not_vectorized':
                    print(f"  - Reason: {test_result['error_message']}")
                elif test_result['error_message']:
                    print(f"  - Error: {test_result['error_message']}")
                if test_result['test_output']:
                    print(f"  - Test output: {test_result['test_output'][:200]}...")
                # For correctness errors, test_output and hint are repetitive, so only show test_output
                if test_result['error_type'] != 'correctness':
                    print(f"  - Hint: {test_result['hint']}")
                
                # Prepare feedback for next iteration
                feedback = test_result
                # Add the previous code attempt to feedback
                feedback['previous_code'] = vectorized_code
        
        return {
            'function': func_name,
            'category': func_data['category'],
            'clang_analysis': clang_report,
            'total_iterations': len(attempts),
            'success': attempts[-1]['success'] if attempts else False,
            'attempts': attempts
        }
    
    def run_experiment(self, functions_to_test=None):
        """Run the vectorization experiment"""
        
        if functions_to_test is None:
            functions_to_test = ['s114']
        
        # Extract the test functions first
        self.test_functions = self.extract_tsvc_functions(functions_to_test)
        
        results = []
        category_stats = {}
        
        for func_name in functions_to_test:
            if func_name not in self.test_functions:
                print(f"Function {func_name} not found in TSVC")
                continue
                
            func_data = self.test_functions[func_name]
            result = self.run_vectorization_fsm(func_name, func_data)
            results.append(result)
            
            # Update category statistics
            category = func_data['category']
            if category not in category_stats:
                category_stats[category] = {'success': 0, 'total': 0}
            category_stats[category]['total'] += 1
            if result['success']:
                category_stats[category]['success'] += 1
            
            # Save results
            os.makedirs('tsvc_results', exist_ok=True)
            with open(f'tsvc_results/{func_name}.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            time.sleep(1)  # Rate limiting
        
        # Print summary
        self.print_summary(results, category_stats)
        
        # Save all results
        with open('tsvc_vectorization_results.json', 'w') as f:
            json.dump({
                'experiment': 'TSVC_vectorization_with_anthropic',
                'model': self.model,
                'temperature': self.temperature,
                'max_iterations': self.max_iterations,
                'results': results,
                'category_stats': category_stats
            }, f, indent=2)
        
        return results
    
    def print_summary(self, results, category_stats):
        """Print experiment summary"""
        print(f"\n{'='*60}")
        print("TSVC VECTORIZATION SUMMARY")
        print(f"{'='*60}")
        
        # Overall results
        successful = sum(1 for r in results if r['success'])
        print(f"\nOverall: {successful}/{len(results)} functions successfully vectorized")
        
        # By function
        print("\nBy Function:")
        for result in results:
            status = "SUCCESS" if result['success'] else "FAILED"
            print(f"  {result['function']:6s} ({result['category']}): {status} after {result['total_iterations']} iterations")
        
        # By category
        print("\nBy Category:")
        for category, stats in category_stats.items():
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {category:20s}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")


def main():
    # Clean up workspace before running
    cleanup_workspace()
    
    # Use your Anthropic API key
    api_key = "key"
    
    experiment = TSVCVectorizerExperiment(api_key)
    
    # Test s126 function
    experiment.run_experiment(functions_to_test=['s222'])

if __name__ == "__main__":
    main()