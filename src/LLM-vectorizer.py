import anthropic
import subprocess
import tempfile
import os
import json
import time
import re

class TSVCVectorizerExperiment:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Using Claude Sonnet 4
        self.max_iterations = 3
        self.temperature = 1.0
        self.results = {}
        
        # Extract test functions from tsvc.c
        self.test_functions = self.extract_tsvc_functions()
    
    def extract_tsvc_functions(self):
        """Extract function code from tsvc.c file"""
        functions = {}
        
        # Read tsvc.c content
        with open('tsvc.c', 'r') as f:
            content = f.read()
        
        # Define the functions to extract with their categories
        function_list = {
            # Linear dependence testing
            's112': 'linear_dependence',
            's1113': 'linear_dependence',
            's114': 'linear_dependence',
            's115': 'linear_dependence',
            's116': 'linear_dependence',
            # Induction variable recognition
            's123': 'induction_variable',
            's126': 'induction_variable',
            # Global data flow analysis
            's131': 'global_dataflow',
            's132': 'global_dataflow',
            # Nonlinear dependence
            's141': 'nonlinear_dependence',
            # Control flow
            's161': 'control_flow',
            's1161': 'control_flow',
            # Statement reordering
            's211': 'statement_reordering',
            's212': 'statement_reordering',
            's1213': 'statement_reordering',
            # Loop distribution
            's221': 'loop_distribution',
            's222': 'loop_distribution',
            # Loop interchange
            's231': 'loop_interchange',
            's232': 'loop_interchange',
            's233': 'loop_interchange',
            's2233': 'loop_interchange',
            's235': 'loop_interchange',
            # Node splitting
            's241': 'node_splitting',
            's242': 'node_splitting',
            's244': 'node_splitting',
            's1244': 'node_splitting',
            # Scalar and array expansion
            's2251': 'scalar_expansion',
            's256': 'array_expansion',
            's258': 'scalar_expansion',
            's261': 'scalar_expansion',
            # Control flow
            's275': 'control_flow',
            's277': 'control_flow',
            # Crossing thresholds
            's281': 'crossing_thresholds',
            # Loop peeling
            's291': 'loop_peeling',
            's292': 'loop_peeling',
            's293': 'loop_peeling',
            # Wavefronts
            's2111': 'wavefronts',
            # Reductions
            's31111': 'reductions',
            's318': 'reductions',
            's3110': 'reductions',
            's3112': 'reductions',
            # Recurrences
            's321': 'recurrences',
            's322': 'recurrences',
            's323': 'recurrences',
            # Search loops
            's332': 'search_loops',
            # Packing
            's341': 'packing',
            's342': 'packing',
            's343': 'packing',
            # Non-logical ifs
            's442': 'non_logical_ifs',
            # Intrinsic functions
            's451': 'intrinsics',
            # Non-local gotos
            's481': 'non_local_gotos',
            's482': 'non_local_gotos'
        }
        
        for func_name, category in function_list.items():
            # Extract function body using regex
            pattern = rf'real_t {func_name}\s*\([^)]+\)\s*\{{(.*?)^}}'
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            
            if match:
                # Get the complete function including signature
                func_start = match.start()
                func_content = content[func_start:match.end()]
                
                # Extract just the core loop (removing timing and initialization)
                core_pattern = r'for \(int nl = 0;.*?dummy\('
                core_match = re.search(core_pattern, func_content, re.DOTALL)
                
                if core_match:
                    core_code = core_match.group(0)
                    # Remove the dummy call at the end
                    core_code = core_code.rsplit('dummy(', 1)[0].strip()
                    
                    functions[func_name] = {
                        'code': func_content,
                        'core_loop': core_code,
                        'category': category
                    }
        
        return functions
    
    def get_clang_vectorization_report(self, func_name, source_code):
        """Get Clang's vectorization analysis report"""
        
        # Create a minimal test program
        test_program = f"""
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define LEN_1D 32000
#define LEN_2D 256
#define real_t float

// Global arrays
real_t a[LEN_1D], b[LEN_1D], c[LEN_1D], d[LEN_1D], e[LEN_1D];
real_t aa[LEN_2D][LEN_2D], bb[LEN_2D][LEN_2D], cc[LEN_2D][LEN_2D];
real_t flat_2d_array[LEN_2D*LEN_2D];
int indx[LEN_1D];

void dummy(real_t a[], real_t b[], real_t c[], real_t d[], real_t e[], 
           real_t aa[][LEN_2D], real_t bb[][LEN_2D], real_t cc[][LEN_2D], real_t s) {{}}

{source_code}

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
            
            # Parse the report
            report = result.stderr
            
            # Extract vectorization failure reasons
            reasons = []
            if "loop not vectorized" in report:
                pattern = r"loop not vectorized: (.+?)(?:\n|$)"
                matches = re.findall(pattern, report)
                reasons.extend(matches)
            
            # Look for specific issues
            dependence_keywords = [
                "unsafe dependent memory operations",
                "loop-carried dependence",
                "backward dependence",
                "memory dependence",
                "cannot identify array bounds",
                "control flow",
                "non-constant loop count"
            ]
            
            found_issues = []
            for keyword in dependence_keywords:
                if keyword in report.lower():
                    found_issues.append(keyword)
            
            return {
                'can_vectorize': len(reasons) == 0 and "vectorized loop" in report,
                'reasons': reasons,
                'issues': found_issues,
                'full_report': report
            }
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_anthropic_prompt(self, source_code, func_name, clang_analysis, feedback=None):
        """Create prompt for Anthropic API following the example format"""
        
        system_prompt = """You are an expert in SIMD vectorization using AVX2 intrinsics.

Please eliminate any dependencies and generate optimized vectorized C code that:

Uses AVX2 intrinsics (mm256* functions)
Targets 8-element vectors for float arrays
Handles the identified dependencies correctly
Ensures semantic equivalence with original code

Always generate only the vectorized function implementation.

When doing vectorization, always follow the steps below.
1. Set the inner loop iterations = 9 to create Fallback scalar loop, out loop as small as possible(if there is one). Enumerate the output by executing the code exactly as written, and replacing a variable with a constant is strictly banned, read it from memory every time inside the loop instead.
2. pay attention to the process of enumerating, understand the pattern from this special case.
3.If your answer is the loop not vectorizable, doing the calculation step by step again with iteration added by 2 and with detailed process present, and again, no any sort of variable replacement, read it from memory every time inside the loop. When you understand the pattern and know how to vectorize, go to 4.
4. generalize the case to give the vectorized code for the real test."""
        
        if feedback is None:
            # Initial vectorization attempt
            user_message = f"""{source_code}
Clang analysis:
{clang_analysis}"""
        else:
            # Repair attempt based on feedback
            user_message = f"""You previously generated vectorized code that was incorrect.
Original function:
{source_code}
Clang analysis:
{clang_analysis}
Your previous vectorized attempt had this error:
{feedback['error_message']}
The test showed these mismatches:
{feedback['test_output']}
Please fix the vectorized code. The issue is likely related to:
{feedback['hint']}
Generate the corrected vectorized function."""
        
        return system_prompt, user_message
    
    def vectorizer_agent(self, source_code, func_name, clang_analysis, feedback=None):
        """Vectorizer agent using Anthropic API"""
        
        system_prompt, user_message = self.create_anthropic_prompt(
            source_code, func_name, clang_analysis, feedback
        )
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=20000,
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
    
    def create_test_harness(self, func_name, func_data):
        """Create test harness for TSVC functions"""
        
        # Special handling for functions with different signatures
        if func_name in ['s242', 's318', 's332']:
            return self.create_special_test_harness(func_name, func_data)
        
        return f"""
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>
#include <math.h>
#include <string.h>

#define LEN_1D 32000
#define LEN_2D 256
#define real_t float
#define iterations 100

// Global arrays
__attribute__((aligned(32))) real_t a1[LEN_1D], b1[LEN_1D], c1[LEN_1D], d1[LEN_1D], e1[LEN_1D];
__attribute__((aligned(32))) real_t a2[LEN_1D], b2[LEN_1D], c2[LEN_1D], d2[LEN_1D], e2[LEN_1D];
__attribute__((aligned(32))) real_t aa1[LEN_2D][LEN_2D], bb1[LEN_2D][LEN_2D], cc1[LEN_2D][LEN_2D];
__attribute__((aligned(32))) real_t aa2[LEN_2D][LEN_2D], bb2[LEN_2D][LEN_2D], cc2[LEN_2D][LEN_2D];
__attribute__((aligned(32))) real_t flat_2d_array1[LEN_2D*LEN_2D];
__attribute__((aligned(32))) real_t flat_2d_array2[LEN_2D*LEN_2D];
__attribute__((aligned(32))) int indx1[LEN_1D];
__attribute__((aligned(32))) int indx2[LEN_1D];

void dummy(real_t a[], real_t b[], real_t c[], real_t d[], real_t e[], 
           real_t aa[][LEN_2D], real_t bb[][LEN_2D], real_t cc[][LEN_2D], real_t s) {{}}

// Original function
{func_data['code'].replace(func_name, f'{func_name}_original').replace('a[', 'a1[').replace('b[', 'b1[').replace('c[', 'c1[').replace('d[', 'd1[').replace('e[', 'e1[').replace('aa[', 'aa1[').replace('bb[', 'bb1[').replace('cc[', 'cc1[').replace('flat_2d_array[', 'flat_2d_array1[').replace('indx[', 'indx1[').replace('dummy(a1', 'dummy(a1')}

// Vectorized function will be inserted here
__VECTORIZED_CODE__

int main() {{
    // Initialize arrays
    for (int i = 0; i < LEN_1D; i++) {{
        a1[i] = a2[i] = (real_t)(i % 128) / 128.0f;
        b1[i] = b2[i] = (real_t)((i + 1) % 128) / 128.0f;
        c1[i] = c2[i] = (real_t)((i + 2) % 128) / 128.0f;
        d1[i] = d2[i] = (real_t)((i + 3) % 128) / 128.0f;
        e1[i] = e2[i] = (real_t)((i + 4) % 128) / 128.0f;
        indx1[i] = indx2[i] = (i % 4) + 1;
    }}
    
    for (int i = 0; i < LEN_2D; i++) {{
        for (int j = 0; j < LEN_2D; j++) {{
            aa1[i][j] = aa2[i][j] = (real_t)((i * j) % 256) / 256.0f;
            bb1[i][j] = bb2[i][j] = (real_t)((i + j) % 256) / 256.0f;
            cc1[i][j] = cc2[i][j] = (real_t)((i - j + 256) % 256) / 256.0f;
        }}
    }}
    
    for (int i = 0; i < LEN_2D*LEN_2D; i++) {{
        flat_2d_array1[i] = flat_2d_array2[i] = (real_t)(i % 512) / 512.0f;
    }}
    
    // Run both versions
    {func_name}_original(NULL);
    {func_name}_vectorized(NULL);
    
    // Compare results
    int match = 1;
    real_t tolerance = 1e-5;
    
    // Check 1D arrays
    for (int i = 0; i < LEN_1D; i++) {{
        if (fabs(a1[i] - a2[i]) > tolerance) {{
            printf("Mismatch in a[%d]: %f vs %f\\n", i, a1[i], a2[i]);
            match = 0;
            if (i > 10) break;
        }}
        if (fabs(b1[i] - b2[i]) > tolerance) {{
            printf("Mismatch in b[%d]: %f vs %f\\n", i, b1[i], b2[i]);
            match = 0;
            if (i > 10) break;
        }}
    }}
    
    if (match) {{
        printf("SUCCESS\\n");
        return 0;
    }} else {{
        return 1;
    }}
}}"""
    
    def create_special_test_harness(self, func_name, func_data):
        """Special test harness for functions with special parameters"""
        # Implementation for s242, s318, s332 etc.
        # These need special handling due to their unique parameter requirements
        pass
    
    def compiler_tester_agent(self, func_name, func_data, vectorized_code):
        """Test the vectorized code for correctness"""
        
        # Extract just the function code
        code_match = re.search(r'```c?\n(.*?)\n```', vectorized_code, re.DOTALL)
        if code_match:
            vectorized_func = code_match.group(1)
        else:
            # Try to extract function directly
            func_pattern = rf'real_t {func_name}\s*\([^)]+\)\s*\{{.*\}}'
            func_match = re.search(func_pattern, vectorized_code, re.DOTALL)
            if func_match:
                vectorized_func = func_match.group(0)
            else:
                vectorized_func = vectorized_code
        
        # Replace function name and array references
        vectorized_func = vectorized_func.replace(func_name, f'{func_name}_vectorized')
        vectorized_func = vectorized_func.replace('a[', 'a2[').replace('b[', 'b2[')
        vectorized_func = vectorized_func.replace('c[', 'c2[').replace('d[', 'd2[')
        vectorized_func = vectorized_func.replace('e[', 'e2[')
        vectorized_func = vectorized_func.replace('aa[', 'aa2[').replace('bb[', 'bb2[')
        vectorized_func = vectorized_func.replace('cc[', 'cc2[')
        vectorized_func = vectorized_func.replace('flat_2d_array[', 'flat_2d_array2[')
        vectorized_func = vectorized_func.replace('indx[', 'indx2[')
        vectorized_func = vectorized_func.replace('dummy(a2', 'dummy(a2')
        
        # Create test harness
        test_template = self.create_test_harness(func_name, func_data)
        test_code = test_template.replace('__VECTORIZED_CODE__', vectorized_func)
        
        # Save for debugging
        os.makedirs(f"tsvc_vectorized_attempts/{func_name}", exist_ok=True)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Compile
            exe_file = temp_file.replace('.c', '')
            compile_result = subprocess.run(
                ['gcc', '-mavx2', '-lm', '-o', exe_file, temp_file],
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
        """Analyze error output to provide hints"""
        if "a[i+1]" in error_output or "a[i-1]" in error_output:
            return "Loop-carried dependency issue. Check if you're reading values before they're written."
        elif "Segmentation fault" in error_output:
            return "Memory access error. Check array bounds and vector load/store alignment."
        elif func_name.startswith('s1'):
            return "Check dependency handling and loop iteration order."
        elif func_name.startswith('s2'):
            return "Statement reordering or loop distribution may be needed."
        elif func_name.startswith('s3'):
            return "Reduction or recurrence pattern - may need special handling."
        else:
            return "Check operation order and ensure all dependencies are correctly handled."
    
    def run_vectorization_fsm(self, func_name, func_data):
        """Main FSM orchestration for a single function"""
        print(f"\n{'='*60}")
        print(f"Vectorizing {func_name} ({func_data['category']})")
        print(f"{'='*60}")
        
        # Get Clang analysis
        print("\nGetting Clang analysis...")
        clang_analysis = self.get_clang_vectorization_report(func_name, func_data['code'])
        
        if clang_analysis['can_vectorize']:
            analysis_text = "Clang reports this loop can be vectorized."
        else:
            analysis_text = f"Clang cannot vectorize due to: {', '.join(clang_analysis['reasons'])}"
        
        print(f"Clang says: {analysis_text}")
        
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
                analysis_text,
                feedback
            )
            
            if vectorized_code is None:
                print("  - API error, stopping")
                break
            
            # Save attempt
            with open(f"tsvc_vectorized_attempts/{func_name}/attempt_{iteration}.c", 'w') as f:
                f.write(vectorized_code)
            
            # Test the code
            print("  - Testing vectorized code...")
            test_result = self.compiler_tester_agent(func_name, func_data, vectorized_code)
            
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
                if test_result['test_output']:
                    print(f"  - Error: {test_result['test_output'][:200]}...")
                print(f"  - Hint: {test_result['hint']}")
                
                # Prepare feedback for next iteration
                feedback = test_result
        
        return {
            'function': func_name,
            'category': func_data['category'],
            'clang_analysis': analysis_text,
            'total_iterations': len(attempts),
            'success': attempts[-1]['success'] if attempts else False,
            'attempts': attempts
        }
    
    def run_experiment(self, functions_to_test=None):
        """Run the vectorization experiment"""
        
        if functions_to_test is None:
            # Test a subset of functions from different categories
            functions_to_test = ['s112', 's1113', 's211', 's212', 's221', 
                               's231', 's281', 's291', 's321', 's332']
        
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
            
            # Save intermediate results
            os.makedirs('tsvc_results', exist_ok=True)
            with open(f'tsvc_results/{func_name}.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            time.sleep(1)  # Rate limiting
        
        # Summary
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
            print(f"  {result['function']:6s} ({result['category']:20s}): {status} after {result['total_iterations']} iterations")
        
        # By category
        print("\nBy Category:")
        for category, stats in category_stats.items():
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {category:20s}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
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

def main():
    # Use your Anthropic API key
    api_key = "your-anthropic-api-key"
    
    experiment = TSVCVectorizerExperiment(api_key)
    
    # You can specify which functions to test, or leave None to test default subset
    # To test all functions: functions_to_test = list(experiment.test_functions.keys())
    experiment.run_experiment(functions_to_test=['s112', 's1113', 's211', 's212'])

if __name__ == "__main__":
    main()