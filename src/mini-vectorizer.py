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
    
    # Calculate workspace root relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(script_dir, '../..')
    workspace_dir = os.path.abspath(workspace_dir)
    
    # 1. Delete all .o files in workspace
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
        self.max_iterations = 2
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
            r'\+\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',    # + s1
            r'-\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',     # - s1
            r'\*\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',    # * s1
            r'/\s*([a-zA-Z_][a-zA-Z0-9_]*)\b',     # / s1
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
                    # Include all other variables (like s1, s2, etc.)
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
                    # Filter out increment/decrement operations and complex expressions
                    valid_inits = []
                    for init in init_matches:
                        init = init.strip()
                        # Skip if it's an increment/decrement or complex expression
                        if not re.match(r'^.*[\+\-]{2}.*$', init) and not re.match(r'^.*[\+\-]\s*\d+$', init):
                            # Also skip if it contains references to unavailable variables like 'x->'
                            if '->' not in init and 'func_args' not in init:
                                valid_inits.append(init)
                    
                    if valid_inits:
                        # Use the first valid initialization value found
                        init_value = valid_inits[0]
                        declarations.append(f"    int {var} = {init_value};")
                        print(f"DEBUG: Found initialization for {var} = {init_value}")
                    else:
                        # No valid initialization found, use test value
                        declarations.append(f"    int {var} = 1;")
                        print(f"DEBUG: No valid initialization found for {var}, using test value")
                else:
                    # No initialization found, use test value
                    declarations.append(f"    int {var} = 1;")
                    print(f"DEBUG: No initialization found for {var}, using test value")
            else:
                # No declaration found, check if it's just initialized
                init_matches = re.findall(rf'\b{var}\s*=\s*([^;]+);', func_body)
                if init_matches:
                    # Filter out increment/decrement operations and complex expressions
                    valid_inits = []
                    for init in init_matches:
                        init = init.strip()
                        # Skip if it's an increment/decrement or complex expression
                        if not re.match(r'^.*[\+\-]{2}.*$', init) and not re.match(r'^.*[\+\-]\s*\d+$', init):
                            # Also skip if it contains references to unavailable variables like 'x->'
                            if '->' not in init and 'func_args' not in init:
                                valid_inits.append(init)
                    
                    if valid_inits:
                        # Use the first valid initialization value found
                        init_value = valid_inits[0]
                        declarations.append(f"    int {var} = {init_value};")
                        print(f"DEBUG: Found initialization without declaration for {var} = {init_value}")
                    else:
                        # Variable not found anywhere, add test value declaration
                        declarations.append(f"    int {var} = 1;")
                        print(f"DEBUG: Variable {var} not found or has complex initialization, adding test value declaration")
                else:
                    # Variable not found anywhere, add test value declaration
                    declarations.append(f"    int {var} = 1;")
                    print(f"DEBUG: Variable {var} not found, adding test value declaration")
        
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
1. Simplify the case by setting the loop iterations to a small number and enumerate the process as the code written. 
2. When enumerating, recognize overwrittened assignments and calculations that cancled each other out, remove all these redundant operations,
   aware the edge cases at the beginning and the end.
3. For the rest of operations, identify which element is refered as its original value and which one is refered as its updated value.
4. Load original values(not updated if executing sequentially like a[i+1]) directly from memory first, then compute elements that use original values, then store these elements. 
   After that, load the updated values from memory, then compute elements that use updated values, finally store these elements.
5. Making necessary redundancy removing based on step 2, and necessary unlooping, loop distribution, loop interchanging, statement reordering based on step 3 & 4.
6. Understand the pattern, then generate the actual vectorized code for the full loop range."""
    
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
    
    def create_modified_tsvc(self, func_name, vectorized_func):
        """Create a modified tsvc.c that includes both original and vectorized versions"""
        print(f"DEBUG: Creating modified tsvc.c for {func_name}")
        
        # Read the original tsvc.c
        try:
            with open('TSVC_2/src/tsvc.c', 'r') as f:
                tsvc_content = f.read()
        except FileNotFoundError:
            try:
                with open('tsvc.c', 'r') as f:
                    tsvc_content = f.read()
            except FileNotFoundError:
                raise FileNotFoundError("tsvc.c file not found")
        
        # Read common.c for the dummy function
        try:
            with open('TSVC_2/src/common.c', 'r') as f:
                common_content = f.read()
        except FileNotFoundError:
            try:
                with open('common.c', 'r') as f:
                    common_content = f.read()
            except FileNotFoundError:
                common_content = ""
        
        # Extract the dummy function from common.c if it exists
        dummy_func = ""
        if common_content:
            import re
            dummy_match = re.search(r'int dummy\([^{]*\{[^}]*\}', common_content, re.DOTALL)
            if dummy_match:
                dummy_func = dummy_match.group(0)
        
        # If dummy function not found, create a simple one
        if not dummy_func:
            dummy_func = """int dummy(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], real_t d[LEN_1D], real_t e[LEN_1D],
                     real_t aa[LEN_2D][LEN_2D], real_t bb[LEN_2D][LEN_2D], real_t cc[LEN_2D][LEN_2D], real_t s) {
    return 0;
}"""
        
        # Extract only the target function and remove all other test functions
        original_func_pattern = rf'(real_t {func_name}\(struct args_t \* func_args\)\s*\{{.*?\n\}})'
        original_match = re.search(original_func_pattern, tsvc_content, re.DOTALL)
        
        if not original_match:
            raise ValueError(f"Original function {func_name} not found in tsvc.c")
        
        original_func = original_match.group(1)
        
        # Create vectorized wrapper that matches the original signature
        vectorized_wrapper = f"""
// Vectorized version of {func_name}
{vectorized_func}

real_t {func_name}_vectorized_wrapper(struct args_t * func_args)
{{
    initialise_arrays(__func__);
    gettimeofday(&func_args->t1, NULL);
    
    for (int nl = 0; nl < iterations; nl++) {{
        {func_name}_vectorized();
        dummy(a, b, c, d, e, aa, bb, cc, 0.);
    }}
    
    gettimeofday(&func_args->t2, NULL);
    return calc_checksum("{func_name}");
}}
"""
        
        # Create a minimal tsvc.c with only the necessary components
        minimal_tsvc = f"""
/*
 * This is an executable test containing a number of loops to measure
 * the performance of a compiler. Arrays' length is LEN_1D by default
 * and if you want a different array length, you should replace every
 * LEN_1D by your desired number which must be a multiple of 40. If you
 * want to increase the number of loop calls to have a longer run time
 * you have to manipulate the constant value iterations. There is a dummy
 * function called in each loop to make all computations appear required.
 * The time to execute this function is included in the time measurement
 * for the output but it is neglectable.
 *
 *  The output includes three columns:
 *    Loop:        The name of the loop
 *    Time(Sec):     The time in seconds to run the loop
 *    Checksum:    The checksum calculated when the test has run
 *
 * In this version of the codelets arrays are static type.
 *
 * All functions/loops are taken from "TEST SUITE FOR VECTORIZING COMPILERS"
 * by David Callahan, Jack Dongarra and David Levine except those whose
 * functions' name have 4 digits.
 */

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>

#include "common.h"
#include "array_defs.h"
#include <immintrin.h>


// array definitions
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t flat_2d_array[LEN_2D*LEN_2D];

__attribute__((aligned(ARRAY_ALIGNMENT))) real_t x[LEN_1D];

__attribute__((aligned(ARRAY_ALIGNMENT))) real_t a[LEN_1D],b[LEN_1D],c[LEN_1D],d[LEN_1D],e[LEN_1D],
                                   aa[LEN_2D][LEN_2D],bb[LEN_2D][LEN_2D],cc[LEN_2D][LEN_2D],tt[LEN_2D][LEN_2D];

__attribute__((aligned(ARRAY_ALIGNMENT))) int indx[LEN_1D];

real_t* __restrict__ xx;
real_t* yy;

{dummy_func}


{original_func}
{vectorized_wrapper}

typedef real_t(*test_function_t)(struct args_t *);

void time_function(test_function_t vector_func, void * arg_info)
{{
    struct args_t func_args = {{.arg_info=arg_info}};

    double result = vector_func(&func_args);

    double tic=func_args.t1.tv_sec+(func_args.t1.tv_usec/1000000.0);
    double toc=func_args.t2.tv_sec+(func_args.t2.tv_usec/1000000.0);

    double taken = toc-tic;

    printf("%10.3f\\t%f\\n", taken, result);
}}


// Test function to compare original vs vectorized
void test_{func_name}_comparison() {{
    struct args_t func_args_orig = {{0}};
    struct args_t func_args_vec = {{0}};
    
    printf("Testing {func_name}:\\n");
    printf("Function\\tTime(sec)\\tChecksum\\n");
    
    // Test original version
    real_t checksum_orig = {func_name}(&func_args_orig);
    double time_orig = (func_args_orig.t2.tv_sec - func_args_orig.t1.tv_sec) +
                      (func_args_orig.t2.tv_usec - func_args_orig.t1.tv_usec) / 1000000.0;
    printf("{func_name}_orig\\t%10.6f\\t%f\\n", time_orig, checksum_orig);
    
    // Test vectorized version
    real_t checksum_vec = {func_name}_vectorized_wrapper(&func_args_vec);
    double time_vec = (func_args_vec.t2.tv_sec - func_args_vec.t1.tv_sec) +
                     (func_args_vec.t2.tv_usec - func_args_vec.t1.tv_usec) / 1000000.0;
    printf("{func_name}_vec\\t%10.6f\\t%f\\n", time_vec, checksum_vec);
    
    // Compare results
    double checksum_diff = fabs(checksum_orig - checksum_vec);
    double speedup = time_orig / time_vec;
    
    printf("\\nComparison Results:\\n");
    printf("Checksum difference: %e\\n", checksum_diff);
    printf("Speedup: %.2fx\\n", speedup);
    
    if (checksum_diff < 1e-5) {{
        printf("CORRECTNESS: PASS\\n");
    }} else {{
        printf("CORRECTNESS: FAIL\\n");
    }}
    
    if (speedup > 1.0) {{
        printf("PERFORMANCE: IMPROVED\\n");
    }} else {{
        printf("PERFORMANCE: NO IMPROVEMENT\\n");
    }}
}}

int main(int argc, char ** argv){{
    int n1 = 1;
    int n3 = 1;
    int* ip;
    real_t s1,s2;
    init(&ip, &s1, &s2);
    
    test_{func_name}_comparison();
    
    return EXIT_SUCCESS;
}}
"""
        
        return minimal_tsvc
    
    def _detect_modified_arrays(self, func_name):
        """Detect which arrays are modified by analyzing the core loop"""
        if not func_name or func_name not in self.test_functions:
            return ['a']  # Default fallback
        
        core_loop = self.test_functions[func_name]['core_loop']
        modified_arrays = []
        
        # Look for assignment patterns: array[index] = ...
        import re
        assignment_patterns = [
            r'\b([a-e])\s*\[\s*[^\]]+\]\s*=',  # Single letter arrays: a[i] = ...
            r'\b(aa|bb|cc)\s*\[\s*[^\]]+\]\s*\[\s*[^\]]+\]\s*=',  # 2D arrays: aa[i][j] = ...
        ]
        
        for pattern in assignment_patterns:
            matches = re.findall(pattern, core_loop)
            for match in matches:
                if match not in modified_arrays:
                    modified_arrays.append(match)
        
        # If no arrays detected as modified, default to 'a'
        if not modified_arrays:
            modified_arrays = ['a']
        
        print(f"DEBUG: Detected modified arrays for {func_name}: {modified_arrays}")
        return modified_arrays
    
    # Removed old test harness creation methods - now using tsvc.c infrastructure
    
    # Removed old test harness creation methods - now using tsvc.c infrastructure
    
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
        """Test the vectorized code using the modified tsvc.c framework"""
        
        # Extract and clean the function first
        vectorized_func = self.extract_and_clean_function(vectorized_code)
        
        # Then check if the extracted function is actually vectorized
        is_vectorized, vec_message = self.check_if_vectorized(vectorized_func)
        if not is_vectorized:
            return {
                'success': False,
                'error_type': 'not_vectorized',
                'error_message': vec_message,
                'test_output': None,
                'hint': 'The code does not contain vector intrinsics. Try to actually vectorize the loop.',
                'performance_data': None
            }
        
        # Ensure correct function name
        if f'{func_name}_vectorized' not in vectorized_func:
            vectorized_func = re.sub(r'void\s+\w+\s*\(', f'void {func_name}_vectorized(', vectorized_func)
        
        # Create modified tsvc.c with both original and vectorized versions
        try:
            modified_tsvc_content = self.create_modified_tsvc(func_name, vectorized_func)
        except Exception as e:
            return {
                'success': False,
                'error_type': 'tsvc_modification',
                'error_message': f'Failed to create modified tsvc.c: {str(e)}',
                'test_output': None,
                'hint': 'Check if tsvc.c and common.c files are accessible',
                'performance_data': None
            }
        
        # Save files for debugging - create in workspace root directory
        # The script is in TSVC_2/src/, so workspace root is two levels up
        workspace_root = os.path.join(os.path.dirname(__file__), '../..')
        workspace_root = os.path.abspath(workspace_root)
        attempts_dir = os.path.join(workspace_root, f"tsvc_vectorized_attempts/{func_name}")
        os.makedirs(attempts_dir, exist_ok=True)
        
        # Save the modified tsvc.c
        modified_tsvc_path = os.path.join(attempts_dir, f"modified_tsvc_{iteration}.c")
        with open(modified_tsvc_path, 'w') as f:
            f.write(modified_tsvc_content)
        
        # Save the extracted vectorized function
        with open(os.path.join(attempts_dir, f"extracted_function_{iteration}.c"), 'w') as f:
            f.write(vectorized_func)
        
        # Don't copy files - use original ones from src directory
        test_dir = attempts_dir
        
        # Compile the modified tsvc.c using original files from src directory
        exe_file = os.path.join(attempts_dir, f"test_executable_{iteration}")
        # Get the absolute path to the src directory for headers and source files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = script_dir  # Script is in the src directory
        common_c_path = os.path.join(src_dir, 'common.c')
        
        compile_result = subprocess.run([
            'gcc',
            '-mavx2',
            '-mfma',
            '-lm',
            '-O2',
            '-I', src_dir,  # Use src directory for headers
            '-o', exe_file,
            modified_tsvc_path,
            common_c_path  # Full path to common.c
        ], capture_output=True, text=True, cwd=src_dir)
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'error_type': 'compilation',
                'error_message': compile_result.stderr,
                'test_output': None,
                'hint': 'Check syntax, missing headers, or incorrect intrinsic usage',
                'performance_data': None
            }
        
        # Run the test
        try:
            run_result = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=src_dir
            )
            
            # Parse the output to extract performance data
            performance_data = self.parse_performance_output(run_result.stdout)
            
            # Check if the test passed based on correctness
            if "CORRECTNESS: PASS" in run_result.stdout:
                return {
                    'success': True,
                    'error_type': None,
                    'error_message': None,
                    'test_output': run_result.stdout,
                    'performance_data': performance_data
                }
            elif "CORRECTNESS: FAIL" in run_result.stdout:
                return {
                    'success': False,
                    'error_type': 'correctness',
                    'error_message': 'Checksum mismatch between original and vectorized versions',
                    'test_output': run_result.stdout,
                    'hint': self.analyze_tsvc_error(run_result.stdout, func_name),
                    'performance_data': performance_data
                }
            else:
                # Execution completed but no clear pass/fail indication
                return {
                    'success': False,
                    'error_type': 'execution',
                    'error_message': 'Test execution completed but results unclear',
                    'test_output': run_result.stdout,
                    'hint': 'Check the test output for runtime errors',
                    'performance_data': performance_data
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_type': 'timeout',
                'error_message': 'Execution timeout',
                'test_output': None,
                'hint': 'Possible infinite loop in vectorized code',
                'performance_data': None
            }
        except Exception as e:
            return {
                'success': False,
                'error_type': 'execution',
                'error_message': f'Execution failed: {str(e)}',
                'test_output': None,
                'hint': 'Check for runtime errors or missing dependencies',
                'performance_data': None
            }
    
    def parse_performance_output(self, output):
        """Parse the performance output from the modified tsvc.c"""
        performance_data = {
            'original_time': None,
            'vectorized_time': None,
            'original_checksum': None,
            'vectorized_checksum': None,
            'speedup': None,
            'checksum_diff': None
        }
        
        import re
        
        # Parse timing and checksum data
        lines = output.split('\n')
        for line in lines:
            if '_orig' in line and '\t' in line:
                # Parse original function results: s1244	s1244_orig	  4.158379	159997.000000
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
                        # The format is: function_name	function_name_orig	time	checksum
                        time_str = parts[2].strip()
                        checksum_str = parts[3].strip()
                        performance_data['original_time'] = float(time_str)
                        performance_data['original_checksum'] = float(checksum_str)
                    except (ValueError, IndexError):
                        pass
            elif '_vec' in line and '\t' in line:
                # Parse vectorized function results: s1244_vectorized_wrapper	s1244_vec	  0.616577	160000.000000
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
                        # The format is: function_name_wrapper	function_name_vec	time	checksum
                        time_str = parts[2].strip()
                        checksum_str = parts[3].strip()
                        performance_data['vectorized_time'] = float(time_str)
                        performance_data['vectorized_checksum'] = float(checksum_str)
                    except (ValueError, IndexError):
                        pass
            elif 'Speedup:' in line:
                # Parse speedup
                match = re.search(r'Speedup: ([\d.]+)x', line)
                if match:
                    performance_data['speedup'] = float(match.group(1))
            elif 'Checksum difference:' in line:
                # Parse checksum difference (handle scientific notation with + sign)
                match = re.search(r'Checksum difference: ([\d.e+-]+)', line)
                if match:
                    performance_data['checksum_diff'] = float(match.group(1))
        
        return performance_data
    
    def analyze_tsvc_error(self, error_output, func_name):
        """Analyze TSVC-specific test output to provide hints"""
        if "CORRECTNESS: FAIL" in error_output:
            # Extract checksum difference
            import re
            diff_match = re.search(r'Checksum difference: ([\d.e+-]+)', error_output)
            if diff_match:
                diff_value = float(diff_match.group(1))
                if diff_value > 1e-3:
                    return f"Large checksum difference ({diff_value:.2e}). The vectorized version likely has a logic error."
                else:
                    return f"Small checksum difference ({diff_value:.2e}). May be due to floating-point precision differences."
            else:
                return "Checksum mismatch detected. The vectorized version produces different results than the original."
        
        elif "Segmentation fault" in error_output:
            return "Memory access error. Check array bounds in vector operations."
        
        elif "Compilation failed" in error_output:
            return "Compilation error. Check syntax and intrinsic usage."
        
        else:
            # Generic hint - show relevant parts of the output
            relevant_lines = []
            for line in error_output.split('\n'):
                if any(keyword in line.lower() for keyword in ['error', 'fail', 'mismatch', 'abort']):
                    relevant_lines.append(line)
            
            if relevant_lines:
                return f"Test failed with errors:\n" + '\n'.join(relevant_lines[:3])
            else:
                return f"Test failed with output:\n{error_output[:200]}"

    def analyze_error(self, error_output, func_name):
        """Legacy method - redirect to analyze_tsvc_error"""
        return self.analyze_tsvc_error(error_output, func_name)
    
    def save_iteration_data(self, func_name, iteration, vectorized_code, source_code, feedback, clang_report):
        """Save all data from this iteration for debugging"""
        # Calculate workspace root consistently
        workspace_root = os.path.join(os.path.dirname(__file__), '../..')
        workspace_root = os.path.abspath(workspace_root)
        attempts_dir = os.path.join(workspace_root, f"tsvc_vectorized_attempts/{func_name}")
        os.makedirs(attempts_dir, exist_ok=True)
        
        # Save LLM response
        with open(os.path.join(attempts_dir, f"attempt_{iteration}.c"), 'w') as f:
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
        with open(os.path.join(attempts_dir, f"prompt_{iteration}.txt"), 'w') as f:
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
                'vectorized_code': vectorized_code,
                'performance_data': test_result.get('performance_data'),
                'test_output': test_result.get('test_output'),
                'error_message': test_result.get('error_message'),
                'hint': test_result.get('hint')
            })
            
            if test_result['success']:
                print(f"  ✓ SUCCESS! Correct vectorization achieved.")
                # Print performance data if available
                if test_result.get('performance_data'):
                    perf = test_result['performance_data']
                    print(f"  - Performance Results:")
                    if perf.get('original_time') and perf.get('vectorized_time'):
                        print(f"    Original time: {perf['original_time']:.6f}s")
                        print(f"    Vectorized time: {perf['vectorized_time']:.6f}s")
                    if perf.get('speedup'):
                        print(f"    Speedup: {perf['speedup']:.2f}x")
                    if perf.get('checksum_diff') is not None:
                        print(f"    Checksum difference: {perf['checksum_diff']:.2e}")
                    if perf.get('original_checksum') and perf.get('vectorized_checksum'):
                        print(f"    Original checksum: {perf['original_checksum']:.1f}")
                        print(f"    Vectorized checksum: {perf['vectorized_checksum']:.1f}")
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
                # Print performance data even for failed tests if available
                if test_result.get('performance_data'):
                    perf = test_result['performance_data']
                    print(f"  - Performance Data:")
                    if perf.get('original_time') and perf.get('vectorized_time'):
                        print(f"    Original time: {perf['original_time']:.6f}s")
                        print(f"    Vectorized time: {perf['vectorized_time']:.6f}s")
                    if perf.get('speedup'):
                        print(f"    Speedup: {perf['speedup']:.2f}x")
                    if perf.get('checksum_diff') is not None:
                        print(f"    Checksum difference: {perf['checksum_diff']:.2e}")
                    if perf.get('original_checksum') and perf.get('vectorized_checksum'):
                        print(f"    Original checksum: {perf['original_checksum']:.1f}")
                        print(f"    Vectorized checksum: {perf['vectorized_checksum']:.1f}")
                
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
            'final_performance_data': attempts[-1].get('performance_data') if attempts else None,
            'attempts': attempts
        }
    
    def run_experiment(self, functions_to_test=None):
        """Run the vectorization experiment"""
        
        if functions_to_test is None:
            functions_to_test = ['s114']
        
        # Calculate workspace root for consistent file placement
        workspace_root = os.path.join(os.path.dirname(__file__), '../..')
        workspace_root = os.path.abspath(workspace_root)
        
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
            
            # Save results in workspace root
            results_dir = os.path.join(workspace_root, 'tsvc_results')
            os.makedirs(results_dir, exist_ok=True)
            with open(os.path.join(results_dir, f'{func_name}.json'), 'w') as f:
                json.dump(result, f, indent=2)
            
            time.sleep(1)  # Rate limiting
        
        # Print summary
        self.print_summary(results, category_stats)
        
        # Save all results in workspace root
        results_file = os.path.join(workspace_root, 'tsvc_vectorization_results.json')
        with open(results_file, 'w') as f:
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
            perf_info = ""
            if result.get('final_performance_data'):
                perf = result['final_performance_data']
                if perf.get('speedup'):
                    perf_info = f" (Speedup: {perf['speedup']:.2f}x)"
            print(f"  {result['function']:6s} ({result['category']}): {status} after {result['total_iterations']} iterations{perf_info}")
        
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
    experiment.run_experiment(functions_to_test=['s2251'])

if __name__ == "__main__":
    main()