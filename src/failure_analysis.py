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
        'not_vectorized': []
    }
    
    for result in results['results']:
        function_name = result['function']
        success = result['success']
        
        if not success:
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
        'no_speedup': [],      # <= 1.0x
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
            if speedup is not None:
                entry = {
                    'function': function_name,
                    'speedup': speedup,
                    'iterations': result['total_iterations']
                }
                
                if speedup <= 1.0:
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
    
    # Known patterns based on function characteristics
    dependency_functions = ['s2111', 's233', 's242']  # Wavefront patterns
    control_flow_functions = ['s244', 's342', 's161']  # Complex conditionals
    memory_pattern_functions = ['s116', 's277', 's281']  # Irregular memory access
    
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
    
    # Analyze no_speedup and minimal improvement cases
    poor_performers = performance['no_speedup'] + performance['minimal']
    
    for case in poor_performers:
        func = case['function']
        speedup = case['speedup']
        
        # Heuristic categorization based on function patterns
        if func in ['s116', 's141', 's161', 's281', 's342']:
            if speedup < 0.7:
                reasons['overhead_dominates'].append(func)
            else:
                reasons['sequential_dependencies'].append(func)
        elif func in ['s2251', 's277', 's343']:
            reasons['gather_scatter_heavy'].append(func)
        elif func in ['s221', 's222', 's232']:
            reasons['branch_divergence'].append(func)
        else:
            reasons['small_computation'].append(func)
    
    return reasons

def generate_report(results_file: str, attempts_dir: str) -> str:
    """Generate comprehensive failure analysis report"""
    
    results = load_results(results_file)
    failures = analyze_failures(results)
    performance = analyze_performance(results)
    failure_categories = categorize_failure_reasons(failures)
    poor_performance_reasons = analyze_poor_performance_reasons(performance, attempts_dir)
    
    report = []
    report.append("# TSVC Vectorizer-PE Experiment Analysis Report\n")
    
    # Overall statistics
    total_functions = len(results['results'])
    failed_functions = sum(len(v) for v in failures.values())
    successful_functions = total_functions - len([r for r in results['results'] if not r['success']])
    
    report.append(f"## Overall Statistics")
    report.append(f"- Total functions tested: {total_functions}")
    report.append(f"- Successfully vectorized: {successful_functions}")
    report.append(f"- Failed to vectorize: {len([r for r in results['results'] if not r['success']])}")
    report.append(f"- Success rate: {successful_functions/total_functions*100:.1f}%\n")
    
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
    
    return '\n'.join(report)

def main():
    import sys
    
    # Allow path to be specified as command line argument
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        attempts_dir = sys.argv[1].replace("tsvc_vectorization_results.json", "tsvc_vectorized_attempts")
    else:
        # Default to PE experiment results
        results_file = "/home/qinxiao/workspace/vectorizer-PE/tsvc_vectorization_results.json"
        attempts_dir = "/home/qinxiao/workspace/vectorizer-PE/tsvc_vectorized_attempts"
    
    report = generate_report(results_file, attempts_dir)
    print(report)

if __name__ == "__main__":
    main()