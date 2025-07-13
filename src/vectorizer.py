import anthropic
import subprocess
import os
import json
import time
import re
import glob
import shutil

def cleanup_workspace():
    """Clean up workspace before running vectorizer"""
    # Calculate workspace root relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(script_dir, '../..')
    workspace_dir = os.path.abspath(workspace_dir)
    
    # 1. Delete all .o files in workspace
    o_files = glob.glob(os.path.join(workspace_dir, "**/*.o"), recursive=True)
    for o_file in o_files:
        try:
            os.remove(o_file)
        except OSError:
            pass
    
    # 2. Clean tsvc_results directory
    tsvc_results_dir = os.path.join(workspace_dir, "tsvc_results")
    if os.path.exists(tsvc_results_dir):
        try:
            shutil.rmtree(tsvc_results_dir)
            os.makedirs(tsvc_results_dir)
        except OSError:
            pass
    
    # 3. Clean tsvc_vectorized_attempts directory
    tsvc_attempts_dir = os.path.join(workspace_dir, "tsvc_vectorized_attempts")
    if os.path.exists(tsvc_attempts_dir):
        try:
            shutil.rmtree(tsvc_attempts_dir)
            os.makedirs(tsvc_attempts_dir)
        except OSError:
            pass
    
    # 4. Delete tsvc_vectorization_results.json file
    results_file = os.path.join(workspace_dir, "tsvc_vectorization_results.json")
    if os.path.exists(results_file):
        try:
            os.remove(results_file)
        except OSError:
            pass

class TSVCVectorizerExperiment:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 1
        self.temperature = 0.7  # Balanced temperature for creative but consistent solutions
        self.results = {}
        
        # Extract test functions - will be populated by run_experiment
        self.test_functions = {}
    
    def extract_tsvc_functions(self, function_names=None):
        """Extract function code from tsvc.c file"""       
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
                
                
                # Now find the computational loop
                # For nested structures (like s114), we want the complete nested structure
                # For single loops (like s1113), we want just that loop
                
                core_loop = None
                
                # Sort loops by depth (outermost first)
                loops.sort(key=lambda x: x['depth'])
                
                # Look for computational loops
                computational_loops = []
                for loop in loops:
                    # Check if it has array operations OR function calls (computational criteria)
                    has_array_ops = re.search(r'\w+\[[^\]]+\]', loop['text'])
                    has_function_calls = re.search(r'\b(?!dummy|gettimeofday|printf|initialise_arrays|calc_checksum)\w+\s*\([^)]*\)', loop['text'])
                    
                    if has_array_ops or has_function_calls:
                        # Don't skip loops that contain dummy calls - they might still be computational
                        # The dummy call is typically at the end and doesn't affect the core computation
                        computational_loops.append(loop)
                
                # If no computational loops found, but we have 'nl' loops with function calls, include them
                # This handles cases like s31111 where the 'nl' loop IS the computational loop
                if not computational_loops:
                    for loop in loops:
                        if 'nl' in loop['header']:
                            # Check if this 'nl' loop has computational content (function calls)
                            has_function_calls = re.search(r'\b(?!dummy|gettimeofday|printf|initialise_arrays|calc_checksum)\w+\s*\([^)]*\)', loop['text'])
                            if has_function_calls:
                                computational_loops.append(loop)
                
                
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
                        else:
                            # Not all nested, pick the last one (likely the innermost)
                            core_loop = computational_loops[-1]['text']
                    else:
                        # Single computational loop
                        core_loop = computational_loops[0]['text']
                
                if not core_loop:
                    core_loop = "// No computational loop found"
                
                # Store the original core loop BEFORE adding declarations
                original_core_loop = core_loop
                
                # Clean up the loop formatting first
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
                    
                    original_core_loop = '\n'.join(cleaned_lines)
                
                # Add missing variable declarations to create a version with declarations
                core_loop_with_decls = original_core_loop
                if original_core_loop and original_core_loop != "// No computational loop found":
                    core_loop_with_decls = self.add_missing_declarations(original_core_loop, func_body)
                
                # Extract the return statement from the original function
                return_match = re.search(r'return\s+([^;]+);', func_body)
                return_expression = return_match.group(1) if return_match else None
                
                functions[func_name] = {
                    'code': full_function,
                    'core_loop': original_core_loop,  # Store the clean original without declarations
                    'core_loop_with_decls': core_loop_with_decls,  # Store version with declarations if needed
                    'return_expression': return_expression
                }
                
                
            else:
                pass  # Function not found
        
        return functions
    
    def add_missing_declarations(self, core_loop, func_body):
        """Add missing variable declarations to the extracted loop with recursive dependency resolution"""
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
            r'\[\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\]\s*\[', # [k][...] - multi-dimensional arrays
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
                # Skip type names that might be incorrectly captured as variables
                if match in ['real_t', 'int', 'float', 'double', 'char', 'void']:
                    continue
                # Skip common array names and loop variables that are typically declared in for loops
                # But be smarter about 'i' and 'j' - only skip them if they're actually declared in for loops
                elif match in ['a', 'b', 'c', 'd', 'e', 'aa', 'bb', 'cc', 'nl']:
                    continue
                # Skip function names and macro names
                elif match in ['test', 'dummy', 'gettimeofday', 'printf', 'initialise_arrays', 'calc_checksum', 'iterations', 'LEN_1D', 'LEN_2D', 'ARRAY_ALIGNMENT']:
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
        
        # Recursively resolve variable dependencies
        all_required_vars = self.resolve_variable_dependencies(used_vars, func_body)
        
        # Find declarations and build dependency-ordered list
        declarations = self.build_ordered_declarations(all_required_vars, func_body)
        
        # Add declarations before the core loop (not inside it)
        if declarations:
            # Prepend declarations before the loop
            core_loop = '\n'.join(declarations) + '\n' + core_loop
        
        return core_loop
    
    def resolve_variable_dependencies(self, initial_vars, func_body):
        """Recursively resolve variable dependencies to find all required variables"""
        import re
        
        all_vars = set(initial_vars)
        to_process = set(initial_vars)
        processed = set()
        
        while to_process:
            var = to_process.pop()
            if var in processed:
                continue
            processed.add(var)
            
            # Find initialization of this variable
            init_matches = re.findall(rf'\b{var}\s*=\s*([^;]+);', func_body)
            for init in init_matches:
                init = init.strip()
                # Skip increment/decrement and complex expressions
                if re.match(r'^.*[\+\-]{2}.*$', init) or '->' in init or 'func_args' in init:
                    continue
                
                # Find variables referenced in this initialization
                referenced_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', init)
                for ref_var in referenced_vars:
                    # Skip constants, type names, array names, function names, and already processed variables
                    if (ref_var.isdigit() or
                        ref_var in ['real_t', 'int', 'float', 'double', 'char', 'void'] or
                        ref_var in ['a', 'b', 'c', 'd', 'e', 'aa', 'bb', 'cc', 'nl'] or
                        ref_var in ['test', 'dummy', 'gettimeofday', 'printf', 'initialise_arrays', 'calc_checksum', 'iterations', 'LEN_1D', 'LEN_2D', 'ARRAY_ALIGNMENT'] or
                        ref_var in processed):
                        continue
                    
                    # Add to required variables if not already present
                    if ref_var not in all_vars:
                        all_vars.add(ref_var)
                        to_process.add(ref_var)
        
        return all_vars
    
    def build_ordered_declarations(self, all_vars, func_body):
        """Build variable declarations in dependency order"""
        import re
        
        declarations = []
        var_dependencies = {}
        var_initializations = {}
        
        # First pass: collect all variable information
        for var in all_vars:
            # Look for variable declarations or initializations
            decl_pattern1 = rf'\b(int|real_t|float)\s+{var}\s*(?:=\s*[^;]+)?;'
            
            # Find declaration type
            func_decl_match = re.search(decl_pattern1, func_body)
            var_type = 'int'  # default
            if func_decl_match:
                var_type = func_decl_match.group(1)
            
            # Find initialization
            init_matches = re.findall(rf'\b{var}\s*=\s*([^;]+);', func_body)
            valid_init = None
            dependencies = set()
            
            for init in init_matches:
                init = init.strip()
                # Skip increment/decrement and complex expressions
                if (re.match(r'^.*[\+\-]{2}.*$', init) or
                    '->' in init or
                    'func_args' in init):
                    continue
                
                # This is a valid initialization
                valid_init = init
                
                # Find dependencies in this initialization
                referenced_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', init)
                for ref_var in referenced_vars:
                    if (not ref_var.isdigit() and
                        ref_var not in ['real_t', 'int', 'float', 'double', 'char', 'void'] and
                        ref_var not in ['a', 'b', 'c', 'd', 'e', 'aa', 'bb', 'cc', 'nl'] and
                        ref_var not in ['test', 'dummy', 'gettimeofday', 'printf', 'initialise_arrays', 'calc_checksum', 'iterations', 'LEN_1D', 'LEN_2D', 'ARRAY_ALIGNMENT'] and
                        ref_var in all_vars and ref_var != var):
                        dependencies.add(ref_var)
                break  # Use first valid initialization
            
            var_dependencies[var] = dependencies
            var_initializations[var] = (var_type, valid_init)
        
        # Second pass: topological sort to order declarations
        ordered_vars = self.topological_sort(all_vars, var_dependencies)
        
        # Third pass: generate declarations
        for var in ordered_vars:
            var_type, init_value = var_initializations[var]
            if init_value:
                declarations.append(f"    {var_type} {var} = {init_value};")
            else:
                # No valid initialization found, use test value
                declarations.append(f"    {var_type} {var} = 1;")
        
        return declarations
    
    def topological_sort(self, variables, dependencies):
        """Topologically sort variables based on their dependencies"""
        # Kahn's algorithm for topological sorting
        in_degree = {var: 0 for var in variables}
        
        # Calculate in-degrees - count how many variables depend on each variable
        for var in variables:
            for dep in dependencies[var]:
                if dep in in_degree:
                    in_degree[var] += 1  # var depends on dep, so var's in-degree increases
        
        # Find variables with no dependencies (in-degree 0)
        queue = [var for var in variables if in_degree[var] == 0]
        result = []
        
        while queue:
            var = queue.pop(0)
            result.append(var)
            
            # Remove this variable's dependencies and update in-degrees
            for other_var in variables:
                if var in dependencies[other_var]:
                    in_degree[other_var] -= 1
                    if in_degree[other_var] == 0:
                        queue.append(other_var)
        
        # If we couldn't sort all variables, there might be circular dependencies
        if len(result) != len(variables):
            # Add remaining variables in arbitrary order
            for var in variables:
                if var not in result:
                    result.append(var)
        
        return result
    
    
    def get_system_prompt(self, func_name, loop_description, return_expression):
        """Generate the system prompt for vectorization"""
        
        # Determine if function needs specific return value
        needs_return = return_expression is not None and return_expression != "calc_checksum(__func__)"
        
        if needs_return:
            return_info = f"""
IMPORTANT: The original function returns: {return_expression}
Your vectorized function MUST:
- Be named `real_t {func_name}_vectorized(struct args_t * func_args)`
- Include initialise_arrays and gettimeofday calls like the original
- Compute and return the exact same value: {return_expression}
- Ensure all variables used in the return expression are properly computed"""
        else:
            return_info = f"""
The vectorized function should:
- Be named `real_t {func_name}_vectorized(struct args_t * func_args)`
- Include initialise_arrays and gettimeofday calls like the original
- Return calc_checksum(__func__)"""
        
        return f"""You are an expert in SIMD vectorization using AVX2 intrinsics.

Generate a complete C function named `{func_name}_vectorized` that vectorizes this {loop_description} using AVX2 intrinsics. The function should:
- Have the exact same signature as the original: real_t {func_name}_vectorized(struct args_t * func_args)
- Include the same initialization pattern: initialise_arrays(__func__) at the beginning
- Use gettimeofday(&func_args->t1, NULL) BEFORE the computation loops (NOT local struct timeval variables)
- Use gettimeofday(&func_args->t2, NULL) AFTER the computation loops (NOT local struct timeval variables)
- DO NOT declare struct timeval variables - use func_args->t1 and func_args->t2 directly
- Use the existing global arrays (a, b, c, d, e for 1D arrays and aa, bb, cc for 2D arrays) - DO NOT declare new arrays
- Include any necessary headers like #include <immintrin.h>
- Include ALL the iteration logic from the original function (including outer loops like 'for (int nl = 0; nl < 2000*iterations; nl++)')
- Use AVX2 intrinsics (_mm256_ps functions) for 8-element float vectors (NOT _mm256_pd which is for double)
- Ensure semantic equivalence with the original code
- Call dummy() function where appropriate to match original behavior

{return_info}

IMPORTANT TYPE AND DECLARATION CONSTRAINTS:
- Arrays are declared as 'real_t' type (NOT double), where real_t is typedef'd as float
- DO NOT declare extern variables for: LEN_1D, LEN_2D, iterations (these are macros)
- 1D arrays: a, b, c, d, e are declared as 'real_t a[LEN_1D]' etc.
- 2D arrays: aa, bb, cc are declared as 'real_t aa[LEN_2D][LEN_2D]' etc.
- dummy() function signature: int dummy(real_t*, real_t*, real_t*, real_t*, real_t*, real_t(*)[LEN_2D], real_t(*)[LEN_2D], real_t(*)[LEN_2D], real_t)
- If you need to reference these arrays, do NOT use extern declarations - they are already global

When doing vectorization analysis, follow these steps:
1. Simplify the case by setting the loop iterations to a small number and enumerate the process as the code written.
2. When enumerating, recognize overwrittened assignments and calculations that cancled each other out, remove all these redundant operations,
   aware the edge cases at the beginning and the end.
3. For the rest of operations, identify which element is refered as its original value and which one is refered as its updated value.
   CRITICAL: If a[i] depends on a[j] and j might be overwritten during the loop, you must split the vectorization into phases:
   - Phase 1: Process elements that use original values
   - Phase 2: Process elements that use updated values
4. Load original values(not updated if executing sequentially like a[i+1]) directly from memory first, then compute elements that use original values, then store these elements.
   After that, load the updated values from memory, then compute elements that use updated values, finally store these elements.
5. Making necessary redundancy removing based on step 2, and necessary unlooping, loop distribution, loop interchanging, statement reordering based on step 3 & 4.
6. Understand the pattern, then generate the actual vectorized code for the full loop range."""
    
    def vectorizer_agent(self, source_code, func_name, feedback=None):
        """Generate vectorized code using Anthropic API"""
        
        # Get return expression for this function
        return_expression = self.test_functions[func_name].get('return_expression', None)
        
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
- Has the correct signature: real_t {func_name}_vectorized(struct args_t * func_args)
- Correctly vectorizes the {loop_description}

Output only the C function, no explanations."""
        
        system_prompt = self.get_system_prompt(func_name, loop_description, return_expression)
        
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
        
        # Check if the LLM just copied the original code
        if 'vectorized' in code and not any(ind in code for ind in vectorization_indicators):
            # It has the vectorized function name but no actual vectorization
            return False, "Function appears to be a copy of the original without actual vectorization. The LLM may have misunderstood the task."
        
        # Only if no intrinsics found, then it's not vectorized
        return False, "No vector intrinsics found. The code needs to use AVX2 intrinsics like _mm256_load_ps, _mm256_add_ps, etc."
    
    def create_modified_tsvc(self, func_name, vectorized_func):
        """Create a minimal test harness that leverages existing TSVC infrastructure"""
        
        # Read the original function from tsvc.c to get its signature
        try:
            with open('TSVC_2/src/tsvc.c', 'r') as f:
                tsvc_content = f.read()
        except FileNotFoundError:
            try:
                with open('tsvc.c', 'r') as f:
                    tsvc_content = f.read()
            except FileNotFoundError:
                raise FileNotFoundError("tsvc.c file not found")
        
        # Extract the original function
        import re
        original_func_pattern = rf'(real_t {func_name}\(struct args_t \* func_args\)\s*\{{.*?\n\}})'
        original_match = re.search(original_func_pattern, tsvc_content, re.DOTALL)
        
        if not original_match:
            raise ValueError(f"Original function {func_name} not found in tsvc.c")
        
        original_func = original_match.group(1)
        
        # Get additional functions needed for this specific function
        additional_functions = self._get_additional_functions(func_name)
        variable_declarations = ""
        
        # Create minimal test harness that leverages existing TSVC infrastructure
        minimal_tsvc = """
/*
 * Minimal test harness for {func_name} using existing TSVC infrastructure
 * This leverages common.c, array_defs.h, and follows tsvc_orig.c patterns
 */

#include "common.h"
#include "array_defs.h"
#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Array definitions (from array_defs.h)
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t flat_2d_array[LEN_2D*LEN_2D];
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t x[LEN_1D];
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t a[LEN_1D],b[LEN_1D],c[LEN_1D],d[LEN_1D],e[LEN_1D],
                                   aa[LEN_2D][LEN_2D],bb[LEN_2D][LEN_2D],cc[LEN_2D][LEN_2D],tt[LEN_2D][LEN_2D];
__attribute__((aligned(ARRAY_ALIGNMENT))) int indx[LEN_1D];
real_t* __restrict__ xx;
real_t* yy;

{variable_declarations}

// Dummy function (from dummy.c)
int dummy(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], real_t d[LEN_1D], real_t e[LEN_1D],
          real_t aa[LEN_2D][LEN_2D], real_t bb[LEN_2D][LEN_2D], real_t cc[LEN_2D][LEN_2D], real_t s) {{
    // Called in each loop to make all computations appear required
    return 0;
}}

{additional_functions}

// Original function from tsvc.c
{original_func}

// Vectorized version
{vectorized_func}

// Test function using the clean TSVC pattern
void test_{func_name}_comparison() {{
    struct args_t func_args_orig = {{0}};
    struct args_t func_args_vec = {{0}};
    
    {argument_setup}
    
    printf("Testing {func_name}:\\n");
    printf("Function\\tTime(sec)\\tChecksum\\n");
    
    // Test original version
    real_t checksum_orig = {func_name}(&func_args_orig);
    double time_orig = (func_args_orig.t2.tv_sec - func_args_orig.t1.tv_sec) +
                      (func_args_orig.t2.tv_usec - func_args_orig.t1.tv_usec) / 1000000.0;
    printf("{func_name}_orig\\t%10.6f\\t%f\\n", time_orig, checksum_orig);
    
    // Test vectorized version
    real_t checksum_vec = {func_name}_vectorized(&func_args_vec);
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
    int* ip;
    real_t s1, s2;
    init(&ip, &s1, &s2);  // Use existing initialization from common.c
    
    test_{func_name}_comparison();
    
    return EXIT_SUCCESS;
}}
""".format(
    func_name=func_name,
    original_func=original_func,
    vectorized_func=vectorized_func,
    additional_functions=additional_functions,
    variable_declarations=variable_declarations,
    argument_setup=self._generate_argument_setup(func_name)
)
        
        return minimal_tsvc
    
    def _get_additional_functions(self, func_name):
        """Get additional functions needed for specific test cases"""
        if func_name == "s31111":
            # s31111 needs the test function
            return """
// Additional function needed for s31111
real_t test(real_t* A){
 real_t s = (real_t)0.0;
 for (int i = 0; i < 4; i++)
   s += A[i];
 return s;
}"""
        else:
            return ""
    
    
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
        
        # Fix gettimeofday issues - replace local struct timeval with func_args
        vectorized_func = re.sub(r'struct\s+timeval\s+\w+\s*,\s*\w+\s*;', '', vectorized_func)
        vectorized_func = re.sub(r'gettimeofday\s*\(\s*&\s*(\w+)\s*,\s*NULL\s*\)', 
                                lambda m: 'gettimeofday(&func_args->t1, NULL)' if m.group(1) in ['start', 't1'] 
                                         else 'gettimeofday(&func_args->t2, NULL)', 
                                vectorized_func)
        
        # Fix calc_checksum issues - replace __func__ with the original function name
        func_name_match = re.search(r'(\w+)_vectorized', vectorized_func)
        if func_name_match:
            orig_func_name = func_name_match.group(1)
            vectorized_func = re.sub(r'calc_checksum\s*\(\s*__func__\s*\)', 
                                    f'calc_checksum("{orig_func_name}")', 
                                    vectorized_func)
            # Also fix initialise_arrays
            vectorized_func = re.sub(r'initialise_arrays\s*\(\s*__func__\s*\)', 
                                    f'initialise_arrays("{orig_func_name}")', 
                                    vectorized_func)
        
        return vectorized_func
    
    def compiler_tester_agent(self, func_name, vectorized_code, iteration=1):
        """Test the vectorized code using the modified tsvc.c framework"""
        
        # Extract and clean the function first
        vectorized_func = self.extract_and_clean_function(vectorized_code)
        
        # Save files for debugging - create in workspace root directory
        # The script is in TSVC_2/src/, so workspace root is two levels up
        workspace_root = os.path.join(os.path.dirname(__file__), '../..')
        workspace_root = os.path.abspath(workspace_root)
        attempts_dir = os.path.join(workspace_root, f"tsvc_vectorized_attempts/{func_name}")
        os.makedirs(attempts_dir, exist_ok=True)
        
        # Save the extracted vectorized function BEFORE checking if it's vectorized
        with open(os.path.join(attempts_dir, f"extracted_function_{iteration}.c"), 'w') as f:
            f.write(vectorized_func)
        
        # Then check if the extracted function is actually vectorized
        is_vectorized, vec_message = self.check_if_vectorized(vectorized_func)
        if not is_vectorized:
            return {
                'success': False,
                'error_type': 'not_vectorized',
                'error_message': vec_message,
                'test_output': None,
                'hint': 'The code must use AVX2 intrinsics (_mm256_* functions) to vectorize the loop. Review the vectorization steps in the system prompt.',
                'performance_data': None
            }
        
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
        
        # Save the modified tsvc.c
        modified_tsvc_path = os.path.join(attempts_dir, f"modified_tsvc_{iteration}.c")
        with open(modified_tsvc_path, 'w') as f:
            f.write(modified_tsvc_content)

        
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
            
            # Save the full output for debugging
            with open(os.path.join(attempts_dir, f"test_output_{iteration}.txt"), 'w') as f:
                f.write(run_result.stdout)
                if run_result.stderr:
                    f.write("\n\nSTDERR:\n")
                    f.write(run_result.stderr)
            
            # Parse the output to extract performance data
            performance_data = self.parse_performance_output(run_result.stdout)
            
            # Check if the test passed based on correctness
            if "CORRECTNESS: PASS" in run_result.stdout:
                # Check performance to distinguish between good and poor speedup
                if "PERFORMANCE: IMPROVED" in run_result.stdout:
                    return {
                        'success': True,
                        'error_type': None,
                        'error_message': None,
                        'test_output': run_result.stdout,
                        'performance_data': performance_data,
                        'speedup_status': 'improved'
                    }
                else:
                    return {
                        'success': True,
                        'error_type': None,
                        'error_message': None,
                        'test_output': run_result.stdout,
                        'performance_data': performance_data,
                        'speedup_status': 'no_improvement'
                    }
            elif "CORRECTNESS: FAIL" in run_result.stdout:
                return {
                    'success': False,
                    'error_type': 'correctness',
                    'error_message': 'Checksum mismatch between original and vectorized versions',
                    'test_output': run_result.stdout,
                    'hint': self.analyze_tsvc_error(run_result.stdout),
                    'performance_data': performance_data
                }
            else:
                # Execution completed but no clear pass/fail indication
                # This is where the original bug was - we need better error diagnostics
                error_msg = "Test execution completed but results unclear"
                if run_result.stderr:
                    error_msg += f"\nSTDERR: {run_result.stderr}"
                
                # Check for common issues in stdout
                if "Unknown function name" in run_result.stdout:
                    error_msg = "calc_checksum failed: function name not recognized"
                elif "_vec" not in run_result.stdout:
                    error_msg = "Vectorized function did not execute properly"
                
                return {
                    'success': False,
                    'error_type': 'execution_incomplete',
                    'error_message': error_msg,
                    'test_output': run_result.stdout,
                    'hint': 'Check if the vectorized function has the correct signature and return statement',
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
                'error_type': 'execution_error',
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
                # Parse original function results
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        time_str = parts[1].strip()
                        checksum_str = parts[2].strip()
                        performance_data['original_time'] = float(time_str)
                        performance_data['original_checksum'] = float(checksum_str)
                    except (ValueError, IndexError):
                        pass
            elif '_vec' in line and '\t' in line:
                # Parse vectorized function results
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        time_str = parts[1].strip()
                        checksum_str = parts[2].strip()
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
    
    def _get_function_arguments(self, func_name):
        """Get special arguments required for specific TSVC functions"""
        
        # Functions that require struct{real_t a; real_t b;} * arg_info
        real_t_struct_functions = {
            's242': {'a': 1.0, 'b': 1.0},  # s1 = 1, s2 = 1
        }
        
        # Functions that require int * arg_info  
        int_functions = {
            's162': 1,      # k = 1
            's171': 1,      # inc = 1  
            's174': 10,     # M = 10
            's175': 1,      # inc = 1
        }
        
        # Functions that require struct{int a; int b;} * arg_info
        int_struct_functions = {
            's122': {'a': 1, 'b': 2},    # n1 = 1, n3 = 2
            's172': {'a': 1, 'b': 1},    # n1 = 1, n3 = 1  
        }
        
        if func_name in real_t_struct_functions:
            return real_t_struct_functions[func_name]
        elif func_name in int_functions:
            return int_functions[func_name]
        elif func_name in int_struct_functions:
            return int_struct_functions[func_name]
        else:
            return None

    def _generate_argument_setup(self, func_name):
        """Generate C code to set up arguments for a specific function"""
        args = self._get_function_arguments(func_name)
        
        if args is None:
            return "// No special arguments needed - use standard TSVC pattern\n    func_args_orig.arg_info = NULL;\n    func_args_vec.arg_info = NULL;"
        
        if func_name == 's242':
            # struct{real_t a; real_t b;} * arg_info
            return f"""// Set up arguments for s242: struct{{real_t a; real_t b;}}
    static struct{{real_t a; real_t b;}} s242_args = {{{args['a']}, {args['b']}}};
    func_args_orig.arg_info = &s242_args;
    func_args_vec.arg_info = &s242_args;"""
        
        elif func_name in ['s162', 's171', 's174', 's175']:
            # int * arg_info
            return f"""// Set up arguments for {func_name}: int
    static int {func_name}_arg = {args};
    func_args_orig.arg_info = &{func_name}_arg;
    func_args_vec.arg_info = &{func_name}_arg;"""
        
        elif func_name in ['s122', 's172']:
            # struct{int a; int b;} * arg_info  
            return f"""// Set up arguments for {func_name}: struct{{int a; int b;}}
    static struct{{int a; int b;}} {func_name}_args = {{{args['a']}, {args['b']}}};
    func_args_orig.arg_info = &{func_name}_args;
    func_args_vec.arg_info = &{func_name}_args;"""
        
        else:
            return "// No special arguments needed - use standard TSVC pattern\n    func_args_orig.arg_info = NULL;\n    func_args_vec.arg_info = NULL;"

    def analyze_tsvc_error(self, error_output):
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
    
    def save_iteration_data(self, func_name, iteration, vectorized_code, source_code, feedback):
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
        
        return_expression = self.test_functions[func_name].get('return_expression', None)
        system_prompt = self.get_system_prompt(func_name, loop_description, return_expression)
        
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
        print(f"Vectorizing {func_name}")
        print(f"{'='*60}")
        
        # Use core loop for vectorization
        source_to_vectorize = func_data['core_loop']
        
        attempts = []
        feedback = None
        
        for iteration in range(1, self.max_iterations + 1):
            # Generate/repair code
            vectorized_code = self.vectorizer_agent(
                source_to_vectorize, 
                func_name, 
                feedback
            )
            
            if vectorized_code is None:
                print("  API error, stopping")
                break
            
            # Save iteration data
            self.save_iteration_data(func_name, iteration, vectorized_code, source_to_vectorize, feedback)
            
            # Test the code
            test_result = self.compiler_tester_agent(func_name, vectorized_code, iteration)
            
            attempts.append({
                'iteration': iteration,
                'success': test_result['success'],
                'error_type': test_result['error_type'],
                'speedup_status': test_result.get('speedup_status'),
                'vectorized_code': vectorized_code,
                'performance_data': test_result.get('performance_data'),
                'test_output': test_result.get('test_output'),
                'error_message': test_result.get('error_message'),
                'hint': test_result.get('hint')
            })
            
            if test_result['success']:
                perf = test_result.get('performance_data', {})
                speedup = perf.get('speedup', 0) if perf else 0
                if speedup and speedup > 1.0:
                    print(f"  ✓ SUCCESS! Speedup: {speedup:.2f}x")
                else:
                    print(f"  ✓ SUCCESS! (No speedup: {speedup:.2f}x)" if speedup else "  ✓ SUCCESS! (No speedup data)")
                break
            else:
                print(f"  ✗ FAILED: {test_result['error_type']}")
                
                # Continue with the next iteration regardless of error type
                
                # Prepare feedback for next iteration
                feedback = test_result
                feedback['previous_code'] = vectorized_code
        
        return {
            'function': func_name,
            'total_iterations': len(attempts),
            'success': attempts[-1]['success'] if attempts else False,
            'speedup_status': attempts[-1].get('speedup_status') if attempts else None,
            'final_performance_data': attempts[-1].get('performance_data') if attempts else None,
            'attempts': attempts
        }
    
    def run_experiment(self, functions_to_test=None):
        """Run the vectorization experiment"""
        
        if functions_to_test is None:
            functions_to_test = ['s112']
        
        # Calculate workspace root for consistent file placement
        workspace_root = os.path.join(os.path.dirname(__file__), '../..')
        workspace_root = os.path.abspath(workspace_root)
        
        # Extract the test functions first
        self.test_functions = self.extract_tsvc_functions(functions_to_test)
        
        results = []
        
        for func_name in functions_to_test:
            if func_name not in self.test_functions:
                continue
                
            func_data = self.test_functions[func_name]
            result = self.run_vectorization_fsm(func_name, func_data)
            results.append(result)
            
            # Save results in workspace root
            results_dir = os.path.join(workspace_root, 'tsvc_results')
            os.makedirs(results_dir, exist_ok=True)
            with open(os.path.join(results_dir, f'{func_name}.json'), 'w') as f:
                json.dump(result, f, indent=2)
            
            # Continue with the next function regardless of errors
            
            time.sleep(1)  # Rate limiting
        
        # Print summary
        self.print_summary(results)
        
        # Save all results in workspace root
        results_file = os.path.join(workspace_root, 'tsvc_vectorization_results.json')
        with open(results_file, 'w') as f:
            json.dump({
                'experiment': 'TSVC_vectorization_with_anthropic',
                'model': self.model,
                'temperature': self.temperature,
                'max_iterations': self.max_iterations,
                'results': results
            }, f, indent=2)
        
        return results
    
    def print_summary(self, results):
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
            if result['success']:
                # Check if we have speedup status from the final attempt
                final_attempt = result['attempts'][-1] if result['attempts'] else {}
                speedup_status = final_attempt.get('speedup_status', 'unknown')
                
                if speedup_status == 'improved':
                    status = "SUCCESS (IMPROVED)"
                elif speedup_status == 'no_improvement':
                    status = "SUCCESS (NO SPEEDUP)"
                else:
                    status = "SUCCESS"
            else:
                status = "FAILED"
            
            perf_info = ""
            if result.get('final_performance_data'):
                perf = result['final_performance_data']
                if perf.get('speedup'):
                    speedup_val = perf['speedup']
                    if speedup_val > 1.0:
                        perf_info = f" (Speedup: {speedup_val:.2f}x)"
                    else:
                        perf_info = f" (Speedup: {speedup_val:.2f}x - NO IMPROVEMENT)"
            print(f"  {result['function']:6s}: {status}{perf_info}")


def get_all_tsvc_functions():
    """Extract all function names from tsvc.c"""
    import re
    
    # Read tsvc.c file
    tsvc_content = None
    try:
        with open('TSVC_2/src/tsvc.c', 'r') as f:
            tsvc_content = f.read()
    except FileNotFoundError:
        try:
            with open('tsvc.c', 'r') as f:
                tsvc_content = f.read()
        except FileNotFoundError:
            print("Error: tsvc.c not found")
            return []
    
    # Find all function definitions matching the pattern
    func_pattern = r'real_t (s\d+[a-z]*?)\(struct args_t \* func_args\)'
    matches = re.findall(func_pattern, tsvc_content)
    
    # Filter out any duplicates and sort
    functions = sorted(list(set(matches)))
    
    print(f"Found {len(functions)} functions in tsvc.c")
    return functions

def main():
    # Clean up workspace before running
    cleanup_workspace()
    
    # Use your Anthropic API key
    api_key = "key"
    
    # Get all functions from tsvc.c
    all_functions = get_all_tsvc_functions()
    
    experiment = TSVCVectorizerExperiment(api_key)
    
    # Test a few functions first to verify the fix
    test_functions = ['s112', 's114', 's115', 's116', 's1161']
    print(f"Testing {len(test_functions)} functions to verify the fix...")
    experiment.run_experiment(functions_to_test=all_functions)

if __name__ == "__main__":
    main()