#!/usr/bin/env python3
import json
import sys

def load_results(filepath):
    """Load vectorization results from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_function_data(results):
    """Extract relevant data for each function"""
    function_data = {}
    for result in results.get('results', []):
        func_name = result.get('function')
        final_perf = result.get('final_performance_data') or {}
        function_data[func_name] = {
            'success': result.get('success', False),
            'speedup': final_perf.get('speedup') if final_perf else None,
            'checksum_diff': final_perf.get('checksum_diff') if final_perf else None,
            'error_types': [],
            'iterations': result.get('total_iterations', 0)
        }
        
        # Collect error types from all attempts
        for attempt in result.get('attempts', []):
            if not attempt.get('success', False):
                error_type = attempt.get('error_type', 'unknown')
                if error_type not in function_data[func_name]['error_types']:
                    function_data[func_name]['error_types'].append(error_type)
    
    return function_data

def compare_results(file1_path, file2_path):
    """Compare two vectorization result files"""
    # Load both files
    data1 = load_results(file1_path)
    data2 = load_results(file2_path)
    
    # Extract function data
    funcs1 = extract_function_data(data1)
    funcs2 = extract_function_data(data2)
    
    # Get all unique function names
    all_functions = set(funcs1.keys()) | set(funcs2.keys())
    
    # Compare results
    comparison = []
    for func in sorted(all_functions):
        func1_data = funcs1.get(func, {})
        func2_data = funcs2.get(func, {})
        
        comparison.append({
            'function': func,
            'in_file1': func in funcs1,
            'in_file2': func in funcs2,
            'success_file1': func1_data.get('success', False),
            'success_file2': func2_data.get('success', False),
            'speedup_file1': func1_data.get('speedup'),
            'speedup_file2': func2_data.get('speedup'),
            'errors_file1': func1_data.get('error_types', []),
            'errors_file2': func2_data.get('error_types', []),
            'checksum_diff_file1': func1_data.get('checksum_diff'),
            'checksum_diff_file2': func2_data.get('checksum_diff')
        })
    
    return comparison, data1, data2

def print_detailed_comparison(comparison, data1, data2):
    """Print detailed comparison results"""
    print("="*100)
    print("VECTORIZATION RESULTS COMPARISON")
    print("="*100)
    print(f"\nFile 1: {data1.get('experiment', 'Unknown')}")
    print(f"File 2: {data2.get('experiment', 'Unknown')}")
    print()
    
    # Success rate summary
    success1 = sum(1 for c in comparison if c['success_file1'])
    success2 = sum(1 for c in comparison if c['success_file2'])
    total = len(comparison)
    
    print(f"Overall Success Rates:")
    print(f"  File 1: {success1}/{total} ({success1/total*100:.1f}%)")
    print(f"  File 2: {success2}/{total} ({success2/total*100:.1f}%)")
    print()
    
    # Functions that succeeded in one but failed in the other
    print("FUNCTIONS WITH DIFFERENT SUCCESS STATUS:")
    print("-"*80)
    changed_success = [c for c in comparison if c['success_file1'] != c['success_file2']]
    
    for comp in changed_success:
        print(f"\n{comp['function']}:")
        print(f"  File 1: {'SUCCESS' if comp['success_file1'] else 'FAILED'} - Speedup: {comp['speedup_file1']}")
        if comp['errors_file1']:
            print(f"          Errors: {', '.join(comp['errors_file1'])}")
        print(f"  File 2: {'SUCCESS' if comp['success_file2'] else 'FAILED'} - Speedup: {comp['speedup_file2']}")
        if comp['errors_file2']:
            print(f"          Errors: {', '.join(comp['errors_file2'])}")
    
    # Functions with significant speedup differences
    print("\n\nFUNCTIONS WITH SIGNIFICANT SPEEDUP DIFFERENCES (>20% difference):")
    print("-"*80)
    speedup_diffs = []
    for comp in comparison:
        if comp['success_file1'] and comp['success_file2']:
            s1 = comp['speedup_file1'] or 0
            s2 = comp['speedup_file2'] or 0
            if s1 > 0 and s2 > 0:
                diff_pct = abs(s1 - s2) / max(s1, s2) * 100
                if diff_pct > 20:
                    speedup_diffs.append((comp, diff_pct))
    
    for comp, diff_pct in sorted(speedup_diffs, key=lambda x: x[1], reverse=True):
        print(f"\n{comp['function']}:")
        print(f"  File 1 speedup: {comp['speedup_file1']:.2f}x")
        print(f"  File 2 speedup: {comp['speedup_file2']:.2f}x")
        print(f"  Difference: {diff_pct:.1f}%")
    
    # Functions with different error types
    print("\n\nFUNCTIONS WITH DIFFERENT ERROR TYPES:")
    print("-"*80)
    error_changes = [c for c in comparison if c['errors_file1'] != c['errors_file2'] and (c['errors_file1'] or c['errors_file2'])]
    
    for comp in error_changes:
        print(f"\n{comp['function']}:")
        print(f"  File 1 errors: {', '.join(comp['errors_file1']) if comp['errors_file1'] else 'None'}")
        print(f"  File 2 errors: {', '.join(comp['errors_file2']) if comp['errors_file2'] else 'None'}")
    
    # Summary table
    print("\n\nSUMMARY TABLE:")
    print("-"*100)
    print(f"{'Function':<15} {'File1 Status':<15} {'File1 Speedup':<15} {'File2 Status':<15} {'File2 Speedup':<15}")
    print("-"*100)
    
    for comp in sorted(comparison, key=lambda x: x['function']):
        status1 = 'SUCCESS' if comp['success_file1'] else 'FAILED'
        status2 = 'SUCCESS' if comp['success_file2'] else 'FAILED'
        speedup1 = f"{comp['speedup_file1']:.2f}x" if comp['speedup_file1'] else 'N/A'
        speedup2 = f"{comp['speedup_file2']:.2f}x" if comp['speedup_file2'] else 'N/A'
        
        # Highlight rows with differences
        if comp['success_file1'] != comp['success_file2']:
            print(f"*{comp['function']:<14} {status1:<15} {speedup1:<15} {status2:<15} {speedup2:<15}")
        else:
            print(f" {comp['function']:<15} {status1:<15} {speedup1:<15} {status2:<15} {speedup2:<15}")

if __name__ == "__main__":
    file1 = "/home/qinxiao/workspace/vectorizer/tsvc_vectorization_results.json"
    file2 = "/home/qinxiao/workspace/tsvc_vectorization_results.json"
    
    comparison, data1, data2 = compare_results(file1, file2)
    print_detailed_comparison(comparison, data1, data2)