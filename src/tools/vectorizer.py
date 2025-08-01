import anthropic
import subprocess
import os
import json
import time
import re
import glob
import shutil
from alive2_verifier import Alive2Verifier

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
    def __init__(self, api_key, enable_alive2=False, alive2_path=None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 3
        self.temperature = 0.7  # Balanced temperature for creative but consistent solutions
        self.results = {}
        
        # Extract test functions - will be populated by run_experiment
        self.test_functions = {}
        
        # Initialize Alive2 verifier if enabled
        self.enable_alive2 = enable_alive2
        self.alive2_verifier = None
        if enable_alive2:
            try:
                self.alive2_verifier = Alive2Verifier(alive2_path)
                print("Alive2 formal verification enabled")
            except RuntimeError as e:
                print(f"WARNING: Alive2 initialization failed: {e}")
                print("Continuing without formal verification")
                self.enable_alive2 = False
    
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
                
                # Remove comments from the function code before processing
                full_function_cleaned = self.remove_comments_from_code(full_function)
                func_body_cleaned = self.remove_comments_from_code(func_body)
                
                # Extract the return statement from the cleaned function body
                return_match = re.search(r'return\s+([^;]+);', func_body_cleaned)
                return_expression = return_match.group(1) if return_match else None
                
                functions[func_name] = {
                    'code': full_function_cleaned,
                    'return_expression': return_expression
                }
                
                
            else:
                pass  # Function not found
        
        return functions
    
    def remove_comments_from_code(self, code):
        """Remove C-style comments from function code"""
        # Remove single-line comments (//)
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* */)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Clean up multiple consecutive empty lines
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
        
        # Clean up leading/trailing whitespace on lines
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def analyze_function(self, function_code):
        """Analyze the function to extract key information"""
        import re
        
        # Find arrays used in the function
        arrays_used = set()
        # 1D arrays
        for array in ['a', 'b', 'c', 'd', 'e']:
            if re.search(rf'\b{array}\[', function_code):
                arrays_used.add(array)
        # 2D arrays
        for array in ['aa', 'bb', 'cc']:
            if re.search(rf'\b{array}\[', function_code):
                arrays_used.add(array)
        
        return {
            'arrays_used': sorted(list(arrays_used))
        }
    
    def get_system_prompt(self, full_function_code):
        """Generate the system prompt for vectorization with the original function included"""
        
        # Extract return expression from the function code
        return_match = re.search(r'return\s+([^;]+);', full_function_code)
        return_expression = return_match.group(1) if return_match else None
        
        # Analyze the function to extract key information dynamically
        func_analysis = self.analyze_function(full_function_code)
        
        return f"""You are an expert in SIMD vectorization using AVX2 intrinsics.

Given the following original TSVC function:

```c
{full_function_code}
```

Generate a vectorized version named `$func_name_vectorized` that:

1. **Preserves the exact same behavior** as the original function
2. **Uses AVX2 intrinsics** (_mm256_* functions) for vectorization
3. **Returns the same value**: {return_expression}
4. **Maintains the same function signature**: real_t $func_name_vectorized(struct args_t * func_args)

**CRITICAL: Data Type and Intrinsics**
- `real_t` is defined as `float` (single precision), NOT double

Key requirements based on the original function:
- Arrays used: {', '.join(func_analysis['arrays_used'])}
- Timing: Use gettimeofday with func_args->t1 and func_args->t2 (already declared in func_args)
- Include necessary headers like #include <immintrin.h> for AVX2
- Call dummy() the same number of times as the original (typically inside the 'nl' loop)
- Arrays are already declared globally - do NOT redeclare them

When doing vectorization analysis, follow these steps:
1. Simplify the case by setting the loop iterations to a small number and enumerate the process as the code written.
2. When enumerating, recognize and remove overwritten assignments and calculations that cancel each other out to make the dependencies clear.
3. For the rest of operations, identify which element is referred as its original value and which one is referred as its updated value.
   CRITICAL: If a[i] depends on a[j] and a[j] might update during the loop, you must split the vectorization into phases:
   - Phase 1: Process elements that use original values
   - Phase 2: Process elements that use updated values
4. Load original values(not updated if executing sequentially like a[i+1]) directly from memory first, then compute elements that use original values, then store these elements.
   After that, load the updated values from memory, then compute elements that use updated values, finally store these elements.
5. Make necessary unrolling, loop distribution, loop interchanging, statement reordering based on step 3 & 4. Feel free to optimize and restructure as needed.
6. Understand the pattern, then generate the actual vectorized code for the full loop range, ensuring final results match the original."""
    
    def vectorizer_agent(self, func_name, feedback=None):
        """Generate vectorized code using Anthropic API"""
        
        # Get the full function code
        full_function_code = self.test_functions[func_name]['code']
        
        # Create prompts based on whether this is initial attempt or repair
        if feedback is None:
            # Initial attempt - system prompt contains the function
            system_prompt = self.get_system_prompt(full_function_code)
            user_message = "Generate the vectorized version of the function."
        else:
            # Repair attempt - include error feedback
            system_prompt = self.get_system_prompt(full_function_code)
            
            if feedback['error_type'] == 'compilation':
                user_message = f"""The previous attempt had compilation errors:

{feedback['error_message']}

Please fix these errors and generate a corrected vectorized function."""
            elif feedback['error_type'] == 'correctness':
                user_message = f"""The previous attempt produced incorrect results:

{feedback['test_output']}

Please analyze the issue and generate a corrected vectorized function that produces the same results as the original."""
            elif feedback['error_type'] == 'not_vectorized':
                user_message = f"""The previous attempt did not actually use vector intrinsics. You must use AVX2 intrinsics (_mm256_* functions) to vectorize the loops.

Previous incorrect attempt:
{feedback.get('previous_code', '')}

Generate a properly vectorized version using AVX2 intrinsics."""
            elif feedback['error_type'] == 'execution_time_zero':
                user_message = f"""The previous attempt had both original and vectorized versions execute in 0.000000 seconds, indicating the compiler optimized away the computation:

{feedback.get('test_output', '')}

This suggests the compiler eliminated the entire loop because it detected no meaningful side effects. To fix this:

1. Ensure the dummy() function is called with the computed result (not a constant)
2. Make sure the loop variable and intermediate results are actually used
3. Consider adding __attribute__((noinline)) to prevent function inlining
4. Use volatile keywords for critical variables if needed
5. Ensure the return value depends on the actual computation

Generate a corrected vectorized function that cannot be optimized away by the compiler."""
            else:
                user_message = f"""The previous attempt had an error:
{feedback.get('error_message', 'Unknown error')}

Please fix the issue and generate a corrected vectorized function."""
        
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
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
                error_str = str(e)
                print(f"API error (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Check if it's a rate limit/overload error
                if "529" in error_str or "overloaded" in error_str.lower() or "rate" in error_str.lower():
                    if attempt < max_retries - 1:  # Don't wait on the last attempt
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"API overloaded, retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                
                # For other errors or final attempt, return None
                return None
        
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
        return False, "No vector intrinsics found. The code needs to use AVX2 intrinsics like _mm256_load_ps, _mm256_add_ps, etc. Remember: real_t is float, so use _ps intrinsics, not _pd."
    
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
        from string import Template
        
        minimal_tsvc_template = Template("""
/*
 * Minimal test harness for $func_name using existing TSVC infrastructure
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

$variable_declarations

// Dummy function declaration (actual implementation in dummy.c)
int dummy(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], real_t d[LEN_1D], real_t e[LEN_1D],
          real_t aa[LEN_2D][LEN_2D], real_t bb[LEN_2D][LEN_2D], real_t cc[LEN_2D][LEN_2D], real_t s);

$additional_functions

// Original function from tsvc.c
$original_func

// Vectorized version
$vectorized_func

// Test function using the clean TSVC pattern
void test_${func_name}_comparison() {
    struct args_t func_args_orig = {0};
    struct args_t func_args_vec = {0};
    
    $argument_setup
    
    printf("Testing $func_name:\\n");
    printf("Function\\tTime(sec)\\tChecksum\\n");
    
    // Test original version
    real_t checksum_orig = $func_name(&func_args_orig);
    double time_orig = (func_args_orig.t2.tv_sec - func_args_orig.t1.tv_sec) +
                      (func_args_orig.t2.tv_usec - func_args_orig.t1.tv_usec) / 1000000.0;
    printf("${func_name}_orig\\t%10.6f\\t%f\\n", time_orig, checksum_orig);
    
    // Test vectorized version
    real_t checksum_vec = ${func_name}_vectorized(&func_args_vec);
    double time_vec = (func_args_vec.t2.tv_sec - func_args_vec.t1.tv_sec) +
                     (func_args_vec.t2.tv_usec - func_args_vec.t1.tv_usec) / 1000000.0;
    printf("${func_name}_vec\\t%10.6f\\t%f\\n", time_vec, checksum_vec);
    
    // Compare results
    double checksum_diff = fabs(checksum_orig - checksum_vec);
    double speedup;
    
    // Handle case where execution time is too small to measure
    if (time_vec <= 0.0 && time_orig <= 0.0) {
        speedup = 0.0;  // Both versions too fast to measure
    } else if (time_vec <= 0.0) {
        speedup = 999.99;  // Vectorized version is extremely fast
    } else if (time_orig <= 0.0) {
        speedup = 0.0;  // Original version too fast, vectorized slower
    } else {
        speedup = time_orig / time_vec;
    }
    
    printf("\\nComparison Results:\\n");
    printf("Checksum difference: %e\\n", checksum_diff);
    if (time_vec <= 0.0 && time_orig <= 0.0) {
        printf("Speedup: N/A (both execution times too small to measure)\\n");
    } else if (time_vec <= 0.0) {
        printf("Speedup: %.2fx\\n", speedup);
    } else if (time_orig <= 0.0) {
        printf("Speedup: 0.00x (original too fast, vectorized slower)\\n");
    } else {
        printf("Speedup: %.2fx\\n", speedup);
    }
    
    if (checksum_diff < 1e-5) {
        printf("CORRECTNESS: PASS\\n");
    } else {
        printf("CORRECTNESS: FAIL\\n");
    }
    
    if (speedup > 1.0) {
        printf("PERFORMANCE: IMPROVED\\n");
    } else {
        printf("PERFORMANCE: NO IMPROVEMENT\\n");
    }
}

int main(int argc, char ** argv){
    int* ip;
    real_t s1, s2;
    init(&ip, &s1, &s2);  // Use existing initialization from common.c
    
    test_${func_name}_comparison();
    
    return EXIT_SUCCESS;
}
""")
        
        minimal_tsvc = minimal_tsvc_template.substitute(
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
__attribute__((noinline))
real_t test(real_t* A){
 volatile real_t s = (real_t)0.0;
 for (int i = 0; i < 4; i++)
   s += A[i];
 return s;
}"""
        else:
            return ""
    
    
    def extract_and_clean_function(self, vectorized_code):
        """Extract and clean the function from LLM response"""
        # Find all code blocks
        code_blocks = re.findall(r'```c?\n(.*?)\n```', vectorized_code, re.DOTALL)
        
        if code_blocks:
            # The LLM typically provides the complete function last
            # Look for the last block that contains a complete function
            vectorized_func = None
            
            # Go through blocks from last to first
            for block in reversed(code_blocks):
                # Check if this block contains a complete function signature
                if re.search(r'real_t\s+\w+_vectorized\s*\(.*?\{.*?\}', block, re.DOTALL):
                    vectorized_func = block
                    break
            
            # If no complete function found, take the last block
            if vectorized_func is None:
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
    
    def find_function_boundaries(self, modified_tsvc_path, func_name):
        """Find the exact line numbers where original and vectorized functions start"""
        try:
            with open(modified_tsvc_path, 'r') as f:
                lines = f.readlines()
            
            original_start = None
            vectorized_start = None
            
            for i, line in enumerate(lines, 1):  # 1-based line numbers
                # Look for original function
                if f'real_t {func_name}(' in line and f'{func_name}_vectorized' not in line:
                    original_start = i
                # Look for vectorized function
                elif f'real_t {func_name}_vectorized(' in line:
                    vectorized_start = i
                    
            return original_start, vectorized_start
            
        except Exception as e:
            # Fallback to rough estimates if file parsing fails
            return 30, 60

    def run_alive2_verification(self, func_name, original_func, vectorized_func, 
                                modified_tsvc_path, iteration):
        """Run Alive2 formal verification on the transformation."""
        if not self.enable_alive2 or not self.alive2_verifier:
            return None
        
        print(f"  Running Alive2 formal verification...")
        
        # Get include directories
        script_dir = os.path.dirname(os.path.abspath(__file__))
        include_dirs = [script_dir]
        
        # Create minimal C files for each function
        original_c = f"""
#include "common.h"
#include "array_defs.h"
#include <sys/time.h>

// Array declarations
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t a[LEN_1D],b[LEN_1D],c[LEN_1D],d[LEN_1D],e[LEN_1D];
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t aa[LEN_2D][LEN_2D],bb[LEN_2D][LEN_2D],cc[LEN_2D][LEN_2D];

// Dummy function stub
int dummy(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], real_t d[LEN_1D], real_t e[LEN_1D],
          real_t aa[LEN_2D][LEN_2D], real_t bb[LEN_2D][LEN_2D], real_t cc[LEN_2D][LEN_2D], real_t s) {{
    return 0;
}}

{original_func}
"""
        
        vectorized_c = f"""
#include "common.h"
#include "array_defs.h"
#include <immintrin.h>
#include <sys/time.h>

// Array declarations
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t a[LEN_1D],b[LEN_1D],c[LEN_1D],d[LEN_1D],e[LEN_1D];
__attribute__((aligned(ARRAY_ALIGNMENT))) real_t aa[LEN_2D][LEN_2D],bb[LEN_2D][LEN_2D],cc[LEN_2D][LEN_2D];

// Dummy function stub
int dummy(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], real_t d[LEN_1D], real_t e[LEN_1D],
          real_t aa[LEN_2D][LEN_2D], real_t bb[LEN_2D][LEN_2D], real_t cc[LEN_2D][LEN_2D], real_t s) {{
    return 0;
}}

{vectorized_func}
"""
        
        try:
            result = self.alive2_verifier.create_verification_wrapper(
                original_c, vectorized_c, func_name, include_dirs
            )
            
            # Save verification results
            workspace_root = os.path.join(os.path.dirname(__file__), '../..')
            workspace_root = os.path.abspath(workspace_root)
            attempts_dir = os.path.join(workspace_root, f"tsvc_vectorized_attempts/{func_name}")
            
            with open(os.path.join(attempts_dir, f"alive2_verification_{iteration}.txt"), 'w') as f:
                f.write(f"Alive2 Verification Results for {func_name}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Verified: {result.get('verified', False)}\n")
                f.write(f"Stage: {result.get('stage', 'unknown')}\n")
                if result.get('error'):
                    f.write(f"Error: {result['error']}\n")
                if result.get('counterexample'):
                    f.write(f"\nCounterexample:\n{result['counterexample']}\n")
                if result.get('output'):
                    f.write(f"\nFull Output:\n{result['output']}\n")
            
            return result
            
        except Exception as e:
            print(f"  Alive2 verification failed with exception: {e}")
            return {
                'verified': False,
                'error': f'Exception during verification: {str(e)}',
                'stage': 'exception'
            }
    
    def parse_vectorization_info(self, stderr_output, func_name, modified_tsvc_path):
        """Parse compiler vectorization information from stderr output
        
        GCC vectorization output format:
        - filename:line:col: optimized: loop vectorized using N byte vectors
        - filename:line:col: missed: couldn't vectorize loop
        - filename:line:col: missed: not vectorized: reason
        
        We use exact function boundaries to distinguish original vs vectorized function feedback.
        """
        vectorization_info = {
            'original_vectorized': False,
            'vectorized_vectorized': False,
            'original_missed_reasons': [],
            'vectorized_missed_reasons': [],
            'original_optimized': [],
            'vectorized_optimized': [],
            'total_optimized': [],
            'total_missed': []
        }
        
        if not stderr_output:
            return vectorization_info
            
        # Find exact function boundaries
        original_start, vectorized_start = self.find_function_boundaries(modified_tsvc_path, func_name)
        
        lines = stderr_output.split('\n')
        
        # Filter only relevant vectorization messages
        relevant_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip irrelevant messages
            if any(skip in line for skip in [
                'statement clobbers memory',
                'not vectorized: no vectype',
                'basic block part vectorized',  # Not loop vectorization
                'include/',  # Skip messages from system headers
                '.h:'  # Skip messages from header files
            ]):
                continue
                
            # Only keep messages about our modified_tsvc file
            if 'modified_tsvc' not in line:
                continue
                
            # Keep only loop vectorization messages
            if ('optimized:' in line and 'loop vectorized' in line) or \
               ('missed:' in line and ('vectorize' in line or 'not vectorized:' in line)):
                relevant_lines.append(line)
        
        # Now parse the filtered lines using exact function boundaries
        for line in relevant_lines:
            try:
                # Extract line number from compiler output
                parts = line.split(':')
                if len(parts) >= 2:
                    line_num = int(parts[1])
                    
                    # Determine which function based on exact boundaries
                    is_original = original_start and line_num >= original_start and (not vectorized_start or line_num < vectorized_start)
                    is_vectorized = vectorized_start and line_num >= vectorized_start
                    
                    if 'optimized:' in line and 'loop vectorized' in line:
                        vectorization_info['total_optimized'].append(line)
                        
                        if is_original:
                            vectorization_info['original_vectorized'] = True
                            vectorization_info['original_optimized'].append(line)
                        elif is_vectorized:
                            vectorization_info['vectorized_vectorized'] = True
                            vectorization_info['vectorized_optimized'].append(line)
                            
                    elif 'missed:' in line:
                        # Keep all missed reasons for better debugging
                        vectorization_info['total_missed'].append(line)
                        
                        if is_original:
                            # Only deduplicate exact same messages to preserve different reasons for same line
                            if line not in vectorization_info['original_missed_reasons']:
                                vectorization_info['original_missed_reasons'].append(line)
                        elif is_vectorized:
                            # Only deduplicate exact same messages to preserve different reasons for same line
                            if line not in vectorization_info['vectorized_missed_reasons']:
                                vectorization_info['vectorized_missed_reasons'].append(line)
                                
            except (ValueError, IndexError):
                # If we can't parse line numbers, skip this line
                pass
                
        return vectorization_info
    
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
                'performance_data': None,
                'vectorization_info': None  # No compilation happened yet
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
                'performance_data': None,
                'vectorization_info': None  # No compilation happened yet
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
        dummy_c_path = os.path.join(src_dir, 'dummy.c')
        
        # Compile with full optimization including auto-vectorization
        # Key: Test if LLM can do better than compiler's auto-vectorization
        # This creates a realistic baseline where compiler does its best vectorization
        # 
        # Enhanced with vectorization analysis to determine if compiler vectorized the code
        # Using more specific flags to reduce noise in output
        compile_result = subprocess.run([
            'gcc',
            '-std=c99',
            '-O3',                  # High optimization level like TSVC_2
            '-fstrict-aliasing',    # Enable strict aliasing optimization 
            '-fivopts',             # Enable if-conversion optimization
            '-ftree-vectorize',     # Enable auto-vectorization - LLM must beat compiler
            '-mavx2',               # Enable AVX2 for intrinsics
            '-mfma',                # Enable FMA for intrinsics
            '-fopt-info-vec-optimized',  # Report successful vectorizations
            '-fopt-info-vec-missed',     # Report missed vectorization opportunities
            '-I', src_dir,          # Use src directory for headers
            '-o', exe_file,
            modified_tsvc_path,
            common_c_path,          # Full path to common.c
            dummy_c_path,           # Full path to dummy.c - separate compilation unit
            '-lm'
        ], capture_output=True, text=True, cwd=src_dir)
        
        # Parse vectorization information from compiler output
        vectorization_info = self.parse_vectorization_info(compile_result.stderr, func_name, modified_tsvc_path)
        
        # Save compiler output for analysis
        with open(os.path.join(attempts_dir, f"compiler_output_{iteration}.txt"), 'w') as f:
            # Show function boundaries for debugging
            original_start, vectorized_start = self.find_function_boundaries(modified_tsvc_path, func_name)
            f.write("=== VECTORIZATION ANALYSIS ===\n")
            f.write(f"Original function starts at line: {original_start}\n")
            f.write(f"Vectorized function starts at line: {vectorized_start}\n")
            f.write(f"Original function vectorized by compiler: {vectorization_info['original_vectorized']}\n")
            f.write(f"Vectorized function vectorized by compiler: {vectorization_info['vectorized_vectorized']}\n\n")
            
            f.write("--- ORIGINAL FUNCTION ---\n")
            if vectorization_info['original_optimized']:
                f.write("✅ Compiler successfully vectorized:\n")
                for opt in vectorization_info['original_optimized']:
                    # Extract just the relevant part
                    if ':' in opt:
                        parts = opt.split(':', 4)
                        if len(parts) >= 5:
                            f.write(f"  Line {parts[1]}: {parts[4]}\n")
                        else:
                            f.write(f"  {opt}\n")
            else:
                f.write("❌ Compiler did NOT vectorize\n")
                
            if vectorization_info['original_missed_reasons']:
                f.write("Missed opportunities:\n")
                # Group by line number to show all reasons for each line
                line_reasons = {}
                for missed in vectorization_info['original_missed_reasons']:
                    if ':' in missed:
                        parts = missed.split(':', 4)
                        if len(parts) >= 5:
                            line_num = parts[1]
                            reason = parts[4].strip()
                            if line_num not in line_reasons:
                                line_reasons[line_num] = []
                            if reason not in line_reasons[line_num]:
                                line_reasons[line_num].append(reason)
                
                # Output grouped by line number
                for line_num in sorted(line_reasons.keys(), key=int):
                    reasons = line_reasons[line_num]
                    if len(reasons) == 1:
                        f.write(f"  Line {line_num}: {reasons[0]}\n")
                    else:
                        f.write(f"  Line {line_num}:\n")
                        for reason in reasons:
                            f.write(f"    - {reason}\n")
            
            f.write("\n--- VECTORIZED FUNCTION ---\n")
            if vectorization_info['vectorized_optimized']:
                f.write("✅ Compiler successfully vectorized:\n")
                for opt in vectorization_info['vectorized_optimized']:
                    if ':' in opt:
                        parts = opt.split(':', 4)
                        if len(parts) >= 5:
                            f.write(f"  Line {parts[1]}: {parts[4]}\n")
                        else:
                            f.write(f"  {opt}\n")
            else:
                f.write("❌ Compiler did NOT vectorize\n")
                
            if vectorization_info['vectorized_missed_reasons']:
                f.write("Missed opportunities:\n")
                # Group by line number to show all reasons for each line
                line_reasons = {}
                for missed in vectorization_info['vectorized_missed_reasons']:
                    if ':' in missed:
                        parts = missed.split(':', 4)
                        if len(parts) >= 5:
                            line_num = parts[1]
                            reason = parts[4].strip()
                            if line_num not in line_reasons:
                                line_reasons[line_num] = []
                            if reason not in line_reasons[line_num]:
                                line_reasons[line_num].append(reason)
                
                # Output grouped by line number
                for line_num in sorted(line_reasons.keys(), key=int):
                    reasons = line_reasons[line_num]
                    if len(reasons) == 1:
                        f.write(f"  Line {line_num}: {reasons[0]}\n")
                    else:
                        f.write(f"  Line {line_num}:\n")
                        for reason in reasons:
                            f.write(f"    - {reason}\n")
            
            f.write("\n--- INTERPRETATION ---\n")
            if vectorization_info['original_vectorized'] and not vectorization_info['vectorized_vectorized']:
                f.write("⚠️  WARNING: Compiler vectorized original but NOT the LLM version!\n")
                f.write("   This suggests the LLM vectorization may have broken auto-vectorizability.\n")
            elif not vectorization_info['original_vectorized'] and vectorization_info['vectorized_vectorized']:
                f.write("✅ GOOD: LLM enabled vectorization where compiler couldn't!\n")
                f.write("   The manual intrinsics helped the compiler.\n")
            elif vectorization_info['original_vectorized'] and vectorization_info['vectorized_vectorized']:
                f.write("ℹ️  INFO: Both versions were vectorized by compiler.\n")
                f.write("   Performance differences come from vectorization strategy, not enablement.\n")
            else:
                f.write("❌ NEUTRAL: Neither version was auto-vectorized by compiler.\n")
                f.write("   The LLM's manual vectorization is the only vectorization present.\n")
            
            if compile_result.returncode != 0:
                f.write("\n\n=== COMPILATION ERRORS ===\n")
                f.write(compile_result.stderr)
        
        if compile_result.returncode != 0:
            return {
                'success': False,
                'error_type': 'compilation',
                'error_message': compile_result.stderr,
                'test_output': None,
                'hint': 'Check syntax, missing headers, or incorrect intrinsic usage',
                'performance_data': None,
                'vectorization_info': vectorization_info
            }
        
        # Run Alive2 verification if enabled
        alive2_result = None
        if self.enable_alive2 and self.alive2_verifier:
            # Get the original function code
            original_func = self.test_functions[func_name]['code']
            
            # Run verification
            alive2_result = self.run_alive2_verification(
                func_name, original_func, vectorized_func, 
                modified_tsvc_path, iteration
            )
            
            # If Alive2 found a counterexample, fail immediately
            if alive2_result and not alive2_result.get('verified', False):
                return {
                    'success': False,
                    'error_type': 'formal_verification_failed',
                    'error_message': f"Alive2 formal verification failed: {alive2_result.get('error', 'Unknown error')}",
                    'test_output': None,
                    'hint': 'The vectorized code is not semantically equivalent to the original. Check the transformation logic.',
                    'performance_data': None,
                    'vectorization_info': vectorization_info,
                    'alive2_result': alive2_result
                }
        
        # Run the test
        try:
            run_result = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=30,
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
            
            # Check for zero execution time (compiler optimization issue)
            if self._is_zero_execution_time(run_result.stdout):
                return {
                    'success': False,
                    'error_type': 'execution_time_zero',
                    'error_message': 'Both original and vectorized versions executed in 0.000000 seconds, suggesting compiler optimization eliminated the computation',
                    'test_output': run_result.stdout,
                    'hint': 'The compiler likely optimized away the entire computation. Ensure the vectorized function has meaningful work that cannot be eliminated. Check that: 1) The dummy() function is called properly with the computed result, 2) The loop variable and computations are actually used, 3) Consider adding __attribute__((noinline)) or volatile keywords to prevent optimization.',
                    'performance_data': performance_data,
                    'vectorization_info': vectorization_info
                }
            
            # Check for suspiciously fast baseline (potential optimization issue)
            if self._is_baseline_suspiciously_fast(performance_data):
                return {
                    'success': False,
                    'error_type': 'baseline_too_fast',
                    'error_message': 'Original version executed suspiciously fast, suggesting unintended compiler optimization',
                    'test_output': run_result.stdout,
                    'hint': 'The baseline (original) function is running too fast for the amount of work it should be doing. This suggests the compiler may have optimized it in ways that make comparison unfair. Consider using volatile variables or compiler barriers to ensure the computation actually happens.',
                    'performance_data': performance_data,
                    'vectorization_info': vectorization_info
                }
            
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
                        'speedup_status': 'improved',
                        'vectorization_info': vectorization_info
                    }
                else:
                    return {
                        'success': True,
                        'error_type': None,
                        'error_message': None,
                        'test_output': run_result.stdout,
                        'performance_data': performance_data,
                        'speedup_status': 'no_improvement',
                        'vectorization_info': vectorization_info
                    }
            elif "CORRECTNESS: FAIL" in run_result.stdout:
                return {
                    'success': False,
                    'error_type': 'correctness',
                    'error_message': 'Checksum mismatch between original and vectorized versions',
                    'test_output': run_result.stdout,
                    'hint': self.analyze_tsvc_error(run_result.stdout),
                    'performance_data': performance_data,
                    'vectorization_info': vectorization_info
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
                    'performance_data': performance_data,
                    'vectorization_info': vectorization_info
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_type': 'timeout',
                'error_message': 'Execution timeout',
                'test_output': None,
                'hint': 'Possible infinite loop in vectorized code. Common cause: Using _pd intrinsics instead of _ps. Remember: real_t is float, use _mm256_*_ps intrinsics.',
                'performance_data': None,
                'vectorization_info': vectorization_info
            }
        except Exception as e:
            return {
                'success': False,
                'error_type': 'execution_error',
                'error_message': f'Execution failed: {str(e)}',
                'test_output': None,
                'hint': 'Check for runtime errors or missing dependencies',
                'performance_data': None,
                'vectorization_info': vectorization_info
            }
    
    def _is_zero_execution_time(self, output):
        """Check if both original and vectorized versions have zero execution time"""
        
        # Look for timing data in the output
        timing_lines = []
        for line in output.split('\n'):
            if '\t' in line and 'Time(sec)' not in line:
                # This should be a timing data line
                parts = line.split('\t')
                if len(parts) >= 2:
                    timing_lines.append(parts)
        
        # Check if we have exactly 2 timing lines (original and vectorized)
        if len(timing_lines) != 2:
            return False
        
        # Extract execution times (timing is in the 3rd column, index 2)
        try:
            orig_time = float(timing_lines[0][2].strip())
            vec_time = float(timing_lines[1][2].strip())
            
            # Check if both times are zero (or very close to zero)
            # Only flag as error when BOTH are zero, not just one
            return orig_time <= 0.000001 and vec_time <= 0.000001
        except (ValueError, IndexError):
            return False
    
    def _is_baseline_suspiciously_fast(self, performance_data):
        """Check if baseline execution time is suspiciously fast, indicating unwanted compiler optimization"""
        if not performance_data or performance_data.get('original_time') is None:
            return False
        
        orig_time = performance_data['original_time']
        
        # If time is exactly zero or very close to zero, it's suspicious
        if orig_time <= 0.000001:
            return True
        
        # With -O3 -ftree-vectorize, baseline should be well-optimized but still measurable
        # If it's extremely fast, the compiler likely optimized away the computation entirely
        if orig_time < 0.00001:  # Less than 0.01 milliseconds is suspicious even with auto-vectorization
            return True
        
        # NOTE: With auto-vectorization enabled, we expect smaller speedups or even slowdowns
        # The goal is to test if LLM can beat compiler's vectorization, not just any vectorization
        # So we're more lenient with the ratio check since compiler baseline is already optimized
        if performance_data.get('vectorized_time') is not None:
            vec_time = performance_data['vectorized_time']
            if vec_time > 0 and orig_time > 0:
                ratio = vec_time / orig_time
                # If vectorized version is more than 50x slower than auto-vectorized original,
                # something is seriously wrong (likely computation was eliminated)
                if ratio > 50.0:
                    return True
        
        return False
    
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
                if len(parts) >= 4:
                    try:
                        time_str = parts[2].strip()
                        checksum_str = parts[3].strip()
                        performance_data['original_time'] = float(time_str)
                        performance_data['original_checksum'] = float(checksum_str)
                    except (ValueError, IndexError):
                        pass
            elif '_vec' in line and '\t' in line:
                # Parse vectorized function results
                parts = line.split('\t')
                if len(parts) >= 4:
                    try:
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
    
    def _get_function_arguments(self, func_name):
        """Get special arguments required for specific TSVC functions"""
        
        # Functions that require struct{real_t a; real_t b;} * arg_info
        real_t_struct_functions = {
            's242': {'a': 1.0, 'b': 2.0},  # s1 = 1, s2 = 2
        }
        
        # Functions that require int * arg_info  
        int_functions = {
            's318': 1,      # inc = 1
            's332': 1,      # t = 1
        }
        
        if func_name in real_t_struct_functions:
            return real_t_struct_functions[func_name]
        elif func_name in int_functions:
            return int_functions[func_name]
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
        
        elif func_name in ['s318', 's332']:
            # int * arg_info
            return f"""// Set up arguments for {func_name}: int
    static int {func_name}_arg = {args};
    func_args_orig.arg_info = &{func_name}_arg;
    func_args_vec.arg_info = &{func_name}_arg;"""
        
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

    def save_iteration_data(self, func_name, iteration, vectorized_code, feedback):
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
        full_function_code = self.test_functions[func_name]['code']
        system_prompt = self.get_system_prompt(full_function_code)
        
        if feedback is None:
            user_prompt = "Generate the vectorized version of the function."
        else:
            # Repair attempt prompts
            if feedback['error_type'] == 'compilation':
                user_prompt = f"""The previous attempt had compilation errors:

{feedback['error_message']}

Please fix these errors and generate a corrected vectorized function."""
            elif feedback['error_type'] == 'correctness':
                user_prompt = f"""The previous attempt produced incorrect results:

{feedback['test_output']}

Please analyze the issue and generate a corrected vectorized function that produces the same results as the original."""
            elif feedback['error_type'] == 'not_vectorized':
                user_prompt = f"""The previous attempt did not actually use vector intrinsics. You must use AVX2 intrinsics (_mm256_* functions) to vectorize the loops.

Previous incorrect attempt:
{feedback.get('previous_code', '')}

Generate a properly vectorized version using AVX2 intrinsics."""
            else:
                user_prompt = f"""The previous attempt had an error:
{feedback.get('error_message', 'Unknown error')}

Please fix the issue and generate a corrected vectorized function."""
        
        # Save the complete prompt
        with open(os.path.join(attempts_dir, f"prompt_{iteration}.txt"), 'w') as f:
            f.write(f"Iteration {iteration} Prompt\n{'='*50}\n\n")
            f.write(f"SYSTEM PROMPT:\n{'-'*50}\n{system_prompt}\n\n")
            f.write(f"USER PROMPT:\n{'-'*50}\n{user_prompt}\n")
    
    def run_vectorization_fsm(self, func_name):
        """Main FSM orchestration for a single function"""
        print(f"\n{'='*60}")
        print(f"Vectorizing {func_name}")
        print(f"{'='*60}")
        
        # Note: Full function code is now accessed directly from self.test_functions[func_name]['code']
        
        attempts = []
        feedback = None
        
        for iteration in range(1, self.max_iterations + 1):
            # Generate/repair code with retry logic for this iteration
            vectorized_code = None
            max_iteration_retries = 2  # Retry at iteration level
            
            for iteration_retry in range(max_iteration_retries):
                vectorized_code = self.vectorizer_agent(
                    func_name, 
                    feedback
                )
                
                if vectorized_code is not None:
                    break  # Success, continue with this iteration
                
                # API error occurred
                if iteration_retry < max_iteration_retries - 1:
                    print(f"  API error on iteration {iteration}, retrying iteration-level attempt {iteration_retry + 2}/{max_iteration_retries}")
                    time.sleep(2)  # Additional delay between iteration retries
                else:
                    print(f"  API error on iteration {iteration}, all iteration-level retries exhausted")
            
            if vectorized_code is None:
                print("  API error, stopping vectorization process")
                break
            
            # Save iteration data
            self.save_iteration_data(func_name, iteration, vectorized_code, feedback)
            
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
                'hint': test_result.get('hint'),
                'vectorization_info': test_result.get('vectorization_info'),
                'alive2_result': test_result.get('alive2_result')
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
                
            result = self.run_vectorization_fsm(func_name)
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
    
    # Check if Alive2 is available (optional)
    enable_alive2 = False
    alive2_path = None  # Set to specific path if not in PATH
    
    # You can enable Alive2 by setting this to True
    # enable_alive2 = True
    
    experiment = TSVCVectorizerExperiment(api_key, enable_alive2=enable_alive2, 
                                         alive2_path=alive2_path)
    
    # Run all functions
    experiment.run_experiment(functions_to_test=all_functions)

if __name__ == "__main__":
    main()