#!/usr/bin/env python3
"""
Analyze vectorizer-PE experiment results to identify failure patterns
"""

import json
import os
from typing import Dict, List, Any
from collections import defaultdict

def load_results(filepath: str) -> Dict[str, Any]:
    """Load the JSON results file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_failures(results: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Analyze failed cases and categorize them"""
    
    failures = {
        'correctness': [],
        'compilation': [],
        'timeout': [],
        'not_vectorized': [],
        'complete_failure': []  # Functions that failed all attempts
    }
    
    for result in results['results']:
        function_name = result['function']
        success = result['success']
        
        if not success:
            # Check if all attempts failed
            all_failed = True
            for attempt in result['attempts']:
                if attempt.get('success', False):
                    all_failed = False
                    break
            
            if all_failed:
                failures['complete_failure'].append({
                    'function': function_name,
                    'total_iterations': result['total_iterations']
                })
            
            for attempt in result['attempts']:
                error_type = attempt.get('error_type', '')
                error_message = attempt.get('error_message', '')
                
                if error_type in failures:
                    failures[error_type].append({
                        'function': function_name,
                        'iteration': attempt.get('iteration', 0),
                        'message': error_message,
                        'total_iterations': result['total_iterations']
                    })
    
    return failures

def analyze_performance(results: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Analyze performance patterns"""
    
    performance_categories = {
        'regression': [],      # < 1.0x (performance degradation)
        'no_speedup': [],      # = 1.0x
        'minimal': [],         # 1.0x - 1.5x
        'moderate': [],        # 1.5x - 3.0x
        'good': [],           # 3.0x - 10.0x
        'excellent': []        # > 10.0x
    }
    
    for result in results['results']:
        function_name = result['function']
        success = result['success']
        final_perf = result.get('final_performance_data')
        
        if success and final_perf:
            speedup = final_perf.get('speedup')
            checksum_diff = final_perf.get('checksum_diff', 0.0)
            
            # Only consider it truly successful if checksum matches (diff is 0)
            if speedup is not None and abs(checksum_diff) < 1e-6:
                # Get vectorization info from the successful attempt
                vectorization_info = None
                for attempt in result['attempts']:
                    if attempt.get('success', False):
                        vectorization_info = attempt.get('vectorization_info', {})
                        break
                
                entry = {
                    'function': function_name,
                    'speedup': speedup,
                    'iterations': result['total_iterations'],
                    'checksum_diff': checksum_diff,
                    'original_vectorized': vectorization_info.get('original_vectorized', False) if vectorization_info else False,
                    'vectorized_vectorized': vectorization_info.get('vectorized_vectorized', False) if vectorization_info else False,
                    'original_missed_reasons': vectorization_info.get('original_missed_reasons', []) if vectorization_info else [],
                    'vectorized_missed_reasons': vectorization_info.get('vectorized_missed_reasons', []) if vectorization_info else []
                }
                
                if speedup < 1.0:
                    performance_categories['regression'].append(entry)
                elif speedup == 1.0:
                    performance_categories['no_speedup'].append(entry)
                elif speedup < 1.5:
                    performance_categories['minimal'].append(entry)
                elif speedup < 3.0:
                    performance_categories['moderate'].append(entry)
                elif speedup < 10.0:
                    performance_categories['good'].append(entry)
                else:
                    performance_categories['excellent'].append(entry)
    
    return performance_categories

def categorize_failure_reasons(failures: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
    """Categorize specific failure reasons"""
    
    categories = {
        'data_dependencies': [],
        'complex_control_flow': [],
        'memory_patterns': [],
        'precision_issues': [],
        'compilation_errors': [],
        'implementation_errors': []
    }
    
    # Updated patterns based on the actual PE experiment results
    # From the summary, we know these 8 functions failed: s126, s2111, s2251, s242, s244, s258, s3112, s343
    dependency_functions = ['s2111', 's242', 's244', 's3112']  # Loop-carried dependencies
    control_flow_functions = ['s126', 's258', 's343']  # Conditional updates/branching
    memory_pattern_functions = ['s2251']  # Indirect addressing
    
    for error_type, error_list in failures.items():
        for error in error_list:
            func = error['function']
            if func in dependency_functions:
                categories['data_dependencies'].append(func)
            elif func in control_flow_functions:
                categories['complex_control_flow'].append(func)
            elif func in memory_pattern_functions:
                categories['memory_patterns'].append(func)
            elif error_type == 'compilation':
                categories['compilation_errors'].append(func)
            else:
                categories['implementation_errors'].append(func)
    
    return categories

def analyze_compiler_vectorization(results: Dict[str, Any]) -> Dict[str, List[str]]:
    """Analyze compiler vectorization patterns"""
    
    vectorization_patterns = {
        'original_already_vectorized': [],      # Compiler vectorized original, explains low speedup
        'llm_broke_vectorization': [],          # Original vectorized, but LLM version wasn't
        'llm_enabled_vectorization': [],        # Original not vectorized, LLM version was
        'both_not_vectorized': [],             # Neither version vectorized by compiler
        'both_vectorized': [],                 # Both versions vectorized by compiler
        'failed_functions': []                 # Functions that failed to vectorize
    }
    
    for result in results['results']:
        function_name = result['function']
        success = result['success']
        
        if success:
            # Get vectorization info from the successful attempt
            vectorization_info = None
            for attempt in result['attempts']:
                if attempt.get('success', False):
                    vectorization_info = attempt.get('vectorization_info', {})
                    break
            
            if vectorization_info:
                original_vec = vectorization_info.get('original_vectorized', False)
                vectorized_vec = vectorization_info.get('vectorized_vectorized', False)
                
                if original_vec and vectorized_vec:
                    vectorization_patterns['both_vectorized'].append(function_name)
                elif original_vec and not vectorized_vec:
                    vectorization_patterns['llm_broke_vectorization'].append(function_name)
                elif not original_vec and vectorized_vec:
                    vectorization_patterns['llm_enabled_vectorization'].append(function_name)
                else:
                    vectorization_patterns['both_not_vectorized'].append(function_name)
                
                # Special case: if original was vectorized, this might explain poor performance
                if original_vec:
                    vectorization_patterns['original_already_vectorized'].append(function_name)
        else:
            # For failed functions, try to get vectorization info from any attempt that has it
            vectorization_info = None
            for attempt in result['attempts']:
                if attempt.get('vectorization_info'):
                    vectorization_info = attempt.get('vectorization_info', {})
                    break
            
            if vectorization_info:
                original_vec = vectorization_info.get('original_vectorized', False)
                vectorized_vec = vectorization_info.get('vectorized_vectorized', False)
                
                if original_vec and vectorized_vec:
                    vectorization_patterns['both_vectorized'].append(function_name)
                elif original_vec and not vectorized_vec:
                    vectorization_patterns['llm_broke_vectorization'].append(function_name)
                elif not original_vec and vectorized_vec:
                    vectorization_patterns['llm_enabled_vectorization'].append(function_name)
                else:
                    vectorization_patterns['both_not_vectorized'].append(function_name)
                
                # Special case: if original was vectorized, this might explain poor performance
                if original_vec:
                    vectorization_patterns['original_already_vectorized'].append(function_name)
            
            # Always add failed functions to the failed category
            vectorization_patterns['failed_functions'].append(function_name)
    
    return vectorization_patterns

def analyze_poor_performance_reasons(performance: Dict[str, List[Dict]], 
                                   attempts_dir: str) -> Dict[str, List[str]]:
    """Analyze why certain functions have poor performance"""
    
    reasons = {
        'overhead_dominates': [],      # Vectorization overhead > computation
        'sequential_dependencies': [], # Cannot be effectively vectorized
        'gather_scatter_heavy': [],    # Irregular memory access patterns
        'branch_divergence': [],       # Control flow prevents vectorization
        'small_computation': []        # Computation too simple for vectorization
    }
    
    # Analyze regression, no_speedup and minimal improvement cases
    poor_performers = performance.get('regression', []) + performance.get('no_speedup', []) + performance.get('minimal', [])
    
    for case in poor_performers:
        func = case['function']
        speedup = case['speedup']
        
        # Updated categorization based on PE results
        # Functions with performance regression: s231, s277, s222, s232, s221, s141
        if func in ['s231', 's277']:
            reasons['gather_scatter_heavy'].append(func)
        elif func in ['s222', 's232', 's221']:
            reasons['branch_divergence'].append(func)
        elif func in ['s141']:
            reasons['overhead_dominates'].append(func)
        elif speedup < 0.8:
            reasons['overhead_dominates'].append(func)
        elif func in ['s31111', 's261', 's161']:
            reasons['small_computation'].append(func)
        else:
            reasons['sequential_dependencies'].append(func)
    
    return reasons

def generate_report(results_file: str, attempts_dir: str) -> str:
    """Generate comprehensive failure analysis report"""
    
    results = load_results(results_file)
    failures = analyze_failures(results)
    performance = analyze_performance(results)
    failure_categories = categorize_failure_reasons(failures)
    poor_performance_reasons = analyze_poor_performance_reasons(performance, attempts_dir)
    vectorization_patterns = analyze_compiler_vectorization(results)
    
    report = []
    report.append("# TSVC Vectorizer-PE Experiment Analysis Report\n")
    
    # Overall statistics
    total_functions = len(results['results'])
    failed_functions = len([r for r in results['results'] if not r['success']])
    
    # Count truly successful functions (passing checksum AND showing improvement)
    truly_successful = 0
    for result in results['results']:
        if result['success'] and result.get('final_performance_data'):
            perf = result['final_performance_data']
            if abs(perf.get('checksum_diff', float('inf'))) < 1e-6 and perf.get('speedup', 0) > 1.0:
                truly_successful += 1
    
    # Count functions that passed checksum but had no improvement or regression
    checksum_passed_but_no_improvement = 0
    for result in results['results']:
        if result['success'] and result.get('final_performance_data'):
            perf = result['final_performance_data']
            if abs(perf.get('checksum_diff', float('inf'))) < 1e-6 and perf.get('speedup', 0) <= 1.0:
                checksum_passed_but_no_improvement += 1
    
    report.append(f"## Overall Statistics")
    report.append(f"- Total functions tested: {total_functions}")
    report.append(f"- Successfully vectorized (checksum pass + speedup > 1.0x): {truly_successful}")
    report.append(f"- Vectorized but no improvement (checksum pass + speedup <= 1.0x): {checksum_passed_but_no_improvement}")
    report.append(f"- Failed to vectorize: {failed_functions}")
    report.append(f"- True success rate: {truly_successful/total_functions*100:.1f}%\n")
    
    # Failure analysis
    report.append("## Failure Analysis\n")
    
    report.append("### Failed Functions by Type:")
    for error_type, error_list in failures.items():
        if error_list:
            report.append(f"- **{error_type.replace('_', ' ').title()}**: {len(error_list)} cases")
            functions = list(set(e['function'] for e in error_list))
            report.append(f"  - Functions: {', '.join(functions)}")
    
    report.append("\n### Failure Categories:")
    for category, functions in failure_categories.items():
        if functions:
            unique_functions = list(set(functions))
            report.append(f"- **{category.replace('_', ' ').title()}**: {unique_functions}")
    
    # Performance analysis
    report.append("\n## Performance Analysis\n")
    
    report.append("### Performance Distribution:")
    for category, cases in performance.items():
        if cases:
            report.append(f"- **{category.replace('_', ' ').title()}**: {len(cases)} functions")
            if category in ['no_speedup', 'minimal']:
                functions = [f"{c['function']} ({c['speedup']:.2f}x)" for c in sorted(cases, key=lambda x: x['speedup'])]
                report.append(f"  - {', '.join(functions)}")
    
    report.append("\n### Poor Performance Reasons:")
    for reason, functions in poor_performance_reasons.items():
        if functions:
            report.append(f"- **{reason.replace('_', ' ').title()}**: {functions}")
    
    # Compiler vectorization analysis
    report.append("\n## Compiler Vectorization Analysis\n")
    
    report.append("### Vectorization Patterns:")
    for pattern, functions in vectorization_patterns.items():
        if functions:
            report.append(f"- **{pattern.replace('_', ' ').title()}**: {len(functions)} functions")
            report.append(f"  - Functions: {', '.join(functions)}")
    
    report.append("\n### Performance Impact of Compiler Vectorization:")
    
    # Analyze functions where original was already vectorized
    already_vectorized = set(vectorization_patterns.get('original_already_vectorized', []))
    low_speedup_already_vectorized = []
    good_speedup_already_vectorized = []
    
    for category, cases in performance.items():
        for case in cases:
            if case['function'] in already_vectorized:
                if case['speedup'] < 1.5:
                    low_speedup_already_vectorized.append(f"{case['function']} ({case['speedup']:.2f}x)")
                else:
                    good_speedup_already_vectorized.append(f"{case['function']} ({case['speedup']:.2f}x)")
    
    if low_speedup_already_vectorized:
        report.append(f"- **Low speedup despite manual vectorization (original already vectorized)**: {', '.join(low_speedup_already_vectorized)}")
    if good_speedup_already_vectorized:
        report.append(f"- **Good speedup even with original vectorized**: {', '.join(good_speedup_already_vectorized)}")
    
    # Analyze LLM vectorization success
    llm_enabled = vectorization_patterns.get('llm_enabled_vectorization', [])
    llm_broke = vectorization_patterns.get('llm_broke_vectorization', [])
    
    if llm_enabled:
        report.append(f"- **LLM enabled compiler vectorization**: {', '.join(llm_enabled)}")
    if llm_broke:
        report.append(f"- **LLM broke compiler vectorization**: {', '.join(llm_broke)}")
    
    # Detailed function analysis
    report.append("\n## Detailed Function Analysis\n")
    
    # Failed cases
    report.append("### Failed Cases:")
    failed_funcs = [r for r in results['results'] if not r['success']]
    for func_result in failed_funcs:
        func_name = func_result['function']
        report.append(f"\n#### {func_name}")
        report.append(f"- Total iterations: {func_result['total_iterations']}")
        
        for attempt in func_result['attempts']:
            error_type = attempt.get('error_type', 'unknown')
            error_msg = attempt.get('error_message', '')
            report.append(f"- Iteration {attempt.get('iteration', 0)}: {error_type}")
            if error_msg and len(error_msg) < 200:
                report.append(f"  - {error_msg}")
    
    # Poor performance cases
    report.append("\n### Poor Performance Cases:")
    poor_cases = sorted(performance['no_speedup'] + performance['minimal'], 
                       key=lambda x: x['speedup'])
    
    for case in poor_cases:
        func_name = case['function']
        speedup = case['speedup']
        report.append(f"\n#### {func_name}")
        report.append(f"- Speedup: {speedup:.2f}x")
        report.append(f"- Iterations: {case['iterations']}")
        report.append(f"- Original function vectorized by compiler: {case['original_vectorized']}")
        report.append(f"- LLM vectorized function vectorized by compiler: {case['vectorized_vectorized']}")
        
        # Show missed vectorization reasons
        if case['original_missed_reasons']:
            report.append(f"- Original function missed reasons: {len(case['original_missed_reasons'])} issues")
        if case['vectorized_missed_reasons']:
            report.append(f"- Vectorized function missed reasons: {len(case['vectorized_missed_reasons'])} issues")
    
    # Recommendations
    report.append("\n## Recommendations\n")
    
    report.append("### For Failed Cases:")
    report.append("1. **Data Dependencies**: Implement more sophisticated dependency analysis")
    report.append("2. **Control Flow**: Develop better predication and masking strategies")
    report.append("3. **Memory Patterns**: Improve gather/scatter optimization")
    report.append("4. **Compilation**: Fix C standard compliance issues")
    
    report.append("\n### For Poor Performance Cases:")
    report.append("1. **Overhead Analysis**: Profile vectorization overhead vs. computation")
    report.append("2. **Alternative Approaches**: Consider different vectorization strategies")
    report.append("3. **Compiler Optimization**: Leverage compiler auto-vectorization when manual fails")
    report.append("4. **Algorithm Restructuring**: Explore algorithmic changes for better vectorization")
    
    report.append("\n### Compiler Vectorization Insights:")
    report.append("1. **Original Already Vectorized**: When compiler already vectorizes the original, manual vectorization may show minimal gains")
    report.append("2. **LLM Breaking Vectorization**: Some LLM implementations prevent compiler from vectorizing - investigate simpler approaches")
    report.append("3. **LLM Enabling Vectorization**: LLM can sometimes restructure code to enable compiler vectorization")
    report.append("4. **Hybrid Approach**: Consider letting compiler vectorize when it can, manual only when compiler fails")
    
    return '\n'.join(report)

def main():
    import sys
    
    # Allow path to be specified as command line argument
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        attempts_dir = sys.argv[1].replace("tsvc_vectorization_results.json", "tsvc_vectorized_attempts")
    else:
        # Default to PE experiment results
        results_file = "/home/qinxiao/workspace/PE/tsvc_vectorization_results.json"
        attempts_dir = "/home/qinxiao/workspace/PE/tsvc_vectorized_attempts"
    
    report = generate_report(results_file, attempts_dir)
    print(report)

if __name__ == "__main__":
    main()