#!/usr/bin/env python3
"""
Statistical analysis framework for LLM vectorization experiments
Provides confidence intervals for success rates and performance metrics
"""

import json
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any
import os
from collections import defaultdict
import glob

class VectorizationStatistics:
    """Statistical analysis for LLM vectorization experiments"""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        
    def load_multiple_results(self, results_pattern: str) -> List[Dict[str, Any]]:
        """Load multiple experimental results files"""
        # Support comma-separated patterns/files
        patterns = [p.strip() for p in results_pattern.split(',')]
        all_files = []
        
        for pattern in patterns:
            if os.path.isfile(pattern):
                # Direct file path
                all_files.append(pattern)
            else:
                # Glob pattern
                files = glob.glob(pattern)
                all_files.extend(files)
        
        if not all_files:
            raise FileNotFoundError(f"No files found matching patterns: {results_pattern}")
        
        results = []
        for file_path in sorted(all_files):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    results.append(data)
                    print(f"Loaded {file_path}: {len(data.get('results', []))} functions")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return results
    
    def aggregate_function_data(self, all_results: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Aggregate results by function across multiple runs"""
        function_stats = defaultdict(lambda: {
            'successes': [],
            'speedups': [],
            'original_vectorized': [],
            'vectorized_vectorized': [],
            'checksum_diffs': [],
            'iterations': [],
            'run_metadata': [],
            'true_successes': []  # Success with speedup >= 1.0
        })
        
        for run_idx, result_set in enumerate(all_results):
            for result in result_set.get('results', []):
                func_name = result['function']
                
                # Basic success/failure
                success = result.get('success', False)
                function_stats[func_name]['successes'].append(success)
                function_stats[func_name]['iterations'].append(result.get('total_iterations', 0))
                
                # Performance data and true success determination
                true_success = False
                if success and result.get('final_performance_data'):
                    perf_data = result['final_performance_data']
                    speedup = perf_data.get('speedup')
                    checksum_diff = perf_data.get('checksum_diff', 0.0)
                    
                    if speedup is not None:
                        function_stats[func_name]['speedups'].append(speedup)
                        function_stats[func_name]['checksum_diffs'].append(abs(checksum_diff))
                        # True success: checksum passes AND speedup >= 1.0
                        if abs(checksum_diff) < 1e-6 and speedup >= 1.0:
                            true_success = True
                
                function_stats[func_name]['true_successes'].append(true_success)
                
                # Vectorization info
                for attempt in result.get('attempts', []):
                    if attempt.get('vectorization_info'):
                        vinfo = attempt['vectorization_info']
                        function_stats[func_name]['original_vectorized'].append(
                            vinfo.get('original_vectorized', False)
                        )
                        function_stats[func_name]['vectorized_vectorized'].append(
                            vinfo.get('vectorized_vectorized', False)
                        )
                        break  # Only take first attempt with vectorization info
                
                # Metadata
                function_stats[func_name]['run_metadata'].append({
                    'run_idx': run_idx,
                    'total_iterations': result.get('total_iterations', 0),
                    'speedup_status': result.get('speedup_status', 'unknown')
                })
        
        return dict(function_stats)
    
    def calculate_binomial_ci(self, successes: int, trials: int) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval for binomial proportion"""
        if trials == 0:
            return 0.0, 0.0
        
        if trials == 1:
            # For single trial, use simple bounds
            if successes == 1:
                return 0.025, 1.0  # Wide interval for single success
            else:
                return 0.0, 0.975  # Wide interval for single failure
        
        p = successes / trials
        z = stats.norm.ppf(1 - self.alpha/2)
        
        # Wilson score interval
        center = (p + z**2/(2*trials)) / (1 + z**2/trials)
        margin = z * np.sqrt(p*(1-p)/trials + z**2/(4*trials**2)) / (1 + z**2/trials)
        
        lower = max(0, center - margin)
        upper = min(1, center + margin)
        
        return lower, upper
    
    def calculate_performance_ci(self, values: List[float]) -> Dict[str, float]:
        """Calculate confidence interval for performance metrics"""
        if len(values) < 1:
            return {
                'mean': 0.0,
                'std': 0.0,
                'ci_lower': 0.0,
                'ci_upper': 0.0,
                'n': 0,
                'cv': 0.0
            }
        
        if len(values) == 1:
            return {
                'mean': values[0],
                'std': 0.0,
                'ci_lower': values[0],
                'ci_upper': values[0],
                'n': 1,
                'cv': 0.0  # No variation with single value
            }
        
        values = np.array(values)
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)
        n = len(values)
        
        # t-distribution for small samples
        t_value = stats.t.ppf((1 + self.confidence_level) / 2, n - 1)
        margin_error = t_value * std_val / np.sqrt(n)
        
        return {
            'mean': mean_val,
            'std': std_val,
            'ci_lower': mean_val - margin_error,
            'ci_upper': mean_val + margin_error,
            'n': n,
            'cv': std_val / mean_val if mean_val != 0 else 0.0  # Coefficient of variation
        }
    
    def analyze_function_statistics(self, function_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate comprehensive statistics for each function"""
        results = {}
        
        for func_name, data in function_data.items():
            n_runs = len(data['successes'])
            if n_runs == 0:
                continue
            
            # Success rate analysis (basic success - checksum passes)
            success_count = sum(data['successes'])
            success_rate = success_count / n_runs
            success_ci = self.calculate_binomial_ci(success_count, n_runs)
            
            # True success rate analysis (checksum passes AND speedup >= 1.0)
            true_success_count = sum(data['true_successes'])
            true_success_rate = true_success_count / n_runs
            true_success_ci = self.calculate_binomial_ci(true_success_count, n_runs)
            
            # Performance analysis
            speedup_stats = None
            if data['speedups']:
                speedup_stats = self.calculate_performance_ci(data['speedups'])
            
            # Vectorization consistency
            original_vec_rate = np.mean(data['original_vectorized']) if data['original_vectorized'] else 0.0
            vectorized_vec_rate = np.mean(data['vectorized_vectorized']) if data['vectorized_vectorized'] else 0.0
            
            # Iteration analysis
            iteration_stats = None
            if data['iterations']:
                iteration_stats = self.calculate_performance_ci(data['iterations'])
            
            results[func_name] = {
                'n_runs': n_runs,
                'success_rate': success_rate,
                'success_ci': success_ci,
                'success_count': success_count,
                'true_success_rate': true_success_rate,
                'true_success_ci': true_success_ci,
                'true_success_count': true_success_count,
                'speedup_stats': speedup_stats,
                'original_vectorized_rate': original_vec_rate,
                'vectorized_vectorized_rate': vectorized_vec_rate,
                'iteration_stats': iteration_stats,
                'checksum_stats': self.calculate_performance_ci(data['checksum_diffs']) if data['checksum_diffs'] else None
            }
        
        return results
    
    def categorize_functions(self, function_stats: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Categorize functions based on statistical properties"""
        categories = {
            'high_confidence_success': [],     # Success rate CI > 80%
            'variable_success': [],           # Success rate CI width > 40%
            'consistent_high_performance': [], # Speedup CI > 2.0x
            'variable_performance': [],       # Speedup CV > 0.5
            'stable_functions': [],           # Overall CV < 0.2
            'highly_variable': [],            # Overall CV > 0.5
            'compiler_consistent': [],        # Consistent compiler vectorization
            'compiler_variable': []           # Variable compiler vectorization
        }
        
        for func_name, stats in function_stats.items():
            # Success rate analysis (using true success rate)
            if stats['true_success_ci'][0] > 0.8:
                categories['high_confidence_success'].append(func_name)
            
            ci_width = stats['true_success_ci'][1] - stats['true_success_ci'][0]
            if ci_width > 0.4:
                categories['variable_success'].append(func_name)
            
            # Performance analysis
            if stats['speedup_stats']:
                sp = stats['speedup_stats']
                if sp['ci_lower'] > 2.0:
                    categories['consistent_high_performance'].append(func_name)
                
                if sp['cv'] > 0.5:
                    categories['variable_performance'].append(func_name)
                
                if sp['cv'] < 0.2:
                    categories['stable_functions'].append(func_name)
                elif sp['cv'] > 0.5:
                    categories['highly_variable'].append(func_name)
            
            # Compiler vectorization consistency
            orig_rate = stats['original_vectorized_rate']
            vec_rate = stats['vectorized_vectorized_rate']
            
            if orig_rate == 1.0 or orig_rate == 0.0:  # Always or never vectorized
                categories['compiler_consistent'].append(func_name)
            elif 0.2 < orig_rate < 0.8:  # Variable vectorization
                categories['compiler_variable'].append(func_name)
        
        return categories
    
    def generate_statistical_report(self, function_stats: Dict[str, Dict], 
                                   categories: Dict[str, List[str]]) -> str:
        """Generate comprehensive statistical report"""
        report = []
        report.append("# TSVC Vectorizer Statistical Analysis Report\n")
        
        # Calculate overall statistics
        all_true_success_rates = [stats['true_success_rate'] for stats in function_stats.values()]
        all_speedups = []
        true_success_funcs = []
        failed_funcs = []
        no_improvement_funcs = []
        
        for func_name, stats in function_stats.items():
            if stats['true_success_count'] > 0:
                true_success_funcs.append(func_name)
            if stats['success_count'] == 0:
                failed_funcs.append(func_name)
            elif stats['true_success_count'] == 0 and stats['success_count'] > 0:
                no_improvement_funcs.append(func_name)
                
            if stats['speedup_stats']:
                all_speedups.extend([stats['speedup_stats']['mean']] * stats['speedup_stats']['n'])
        
        overall_true_success_mean = np.mean(all_true_success_rates)
        overall_true_success_std = np.std(all_true_success_rates, ddof=1) if len(all_true_success_rates) > 1 else 0
        
        overall_speedup_mean = np.mean(all_speedups) if all_speedups else 0
        overall_speedup_std = np.std(all_speedups, ddof=1) if len(all_speedups) > 1 else 0
        
        # Overall Statistics section
        report.append(f"## Overall Statistics")
        report.append(f"- Total functions tested: {len(function_stats)}")
        report.append(f"- Successfully vectorized (checksum pass + speedup >= 1.0x): {len(true_success_funcs)}")
        report.append(f"- Vectorized but no improvement (checksum pass + speedup < 1.0x): {len(no_improvement_funcs)}")
        report.append(f"- Failed to vectorize: {len(failed_funcs)}")
        report.append(f"- True success rate: {overall_true_success_mean:.1%}")
        report.append(f"- Average speedup (all attempts): {overall_speedup_mean:.2f}x ± {overall_speedup_std:.2f}x")
        report.append(f"- Confidence level: {self.confidence_level:.0%}\n")
        
        # Performance Analysis
        report.append("## Performance Analysis\n")
        
        # Categorize by performance
        perf_categories = {
            'regression': [],      # < 1.0x
            'no_speedup': [],      # = 1.0x
            'minimal': [],         # 1.0x - 1.5x
            'moderate': [],        # 1.5x - 3.0x
            'good': [],           # 3.0x - 10.0x
            'excellent': []        # > 10.0x
        }
        
        for func_name, stats in function_stats.items():
            if stats['speedup_stats'] and stats['success_count'] > 0:
                mean_speedup = stats['speedup_stats']['mean']
                if mean_speedup < 1.0:
                    perf_categories['regression'].append((func_name, mean_speedup))
                elif mean_speedup == 1.0:
                    perf_categories['no_speedup'].append((func_name, mean_speedup))
                elif mean_speedup < 1.5:
                    perf_categories['minimal'].append((func_name, mean_speedup))
                elif mean_speedup < 3.0:
                    perf_categories['moderate'].append((func_name, mean_speedup))
                elif mean_speedup < 10.0:
                    perf_categories['good'].append((func_name, mean_speedup))
                else:
                    perf_categories['excellent'].append((func_name, mean_speedup))
        
        report.append("### Performance Distribution:")
        for category, funcs in perf_categories.items():
            if funcs:
                report.append(f"- **{category.capitalize()}**: {len(funcs)} functions")
                if category in ['regression', 'no_speedup', 'minimal']:
                    # Show all functions with their speedups for poor performers
                    sorted_funcs = sorted(funcs, key=lambda x: x[1])
                    func_list = ', '.join([f"{f[0]} ({f[1]:.2f}x)" for f in sorted_funcs[:12]])
                    report.append(f"  - {func_list}")
                    if len(funcs) > 12:
                        report.append(f"  - ... and {len(funcs) - 12} more")
        report.append("")
        
        # Category summary
        report.append("## Statistical Categories\n")
        for category, functions in categories.items():
            if functions:
                report.append(f"### {category.replace('_', ' ').title()}: {len(functions)} functions")
                report.append(f"- Functions: {', '.join(functions[:10])}")
                if len(functions) > 10:
                    report.append(f"- ... and {len(functions) - 10} more")
                report.append("")
        
        # Compiler Vectorization Analysis
        report.append("## Compiler Vectorization Analysis\n")
        
        # Analyze compiler vectorization patterns
        original_vectorized = []
        llm_broke_vectorization = []
        llm_enabled_vectorization = []
        both_not_vectorized = []
        
        for func_name, stats in function_stats.items():
            if stats['original_vectorized_rate'] > 0.5 and stats['vectorized_vectorized_rate'] < 0.5:
                llm_broke_vectorization.append(func_name)
            if stats['original_vectorized_rate'] > 0.5:
                original_vectorized.append(func_name)
            if stats['original_vectorized_rate'] < 0.5 and stats['vectorized_vectorized_rate'] > 0.5:
                llm_enabled_vectorization.append(func_name)
            if stats['original_vectorized_rate'] < 0.5 and stats['vectorized_vectorized_rate'] < 0.5:
                both_not_vectorized.append(func_name)
        
        report.append("### Vectorization Patterns:")
        report.append(f"- **Original Already Vectorized**: {len(original_vectorized)} functions")
        if original_vectorized:
            report.append(f"  - Functions: {', '.join(original_vectorized[:10])}")
        report.append(f"- **LLM Broke Vectorization**: {len(llm_broke_vectorization)} functions")
        if llm_broke_vectorization:
            report.append(f"  - Functions: {', '.join(llm_broke_vectorization[:10])}")
        report.append(f"- **LLM Enabled Vectorization**: {len(llm_enabled_vectorization)} functions")
        if llm_enabled_vectorization:
            report.append(f"  - Functions: {', '.join(llm_enabled_vectorization[:10])}")
        report.append(f"- **Both Not Vectorized**: {len(both_not_vectorized)} functions")
        report.append("")
        
        # Function-level detailed analysis
        report.append("## Function-Level Statistical Analysis\n")
        
        # Sort functions by true success rate, then by speedup
        sorted_functions = sorted(function_stats.items(), 
                                key=lambda x: (x[1]['true_success_rate'], 
                                             x[1]['speedup_stats']['mean'] if x[1]['speedup_stats'] else 0), 
                                reverse=True)
        
        for func_name, stats in sorted_functions:
            report.append(f"### {func_name}")
            report.append(f"- **Runs**: {stats['n_runs']}")
            report.append(f"- **Checksum pass rate**: {stats['success_rate']:.1%} "
                         f"(95% CI: {stats['success_ci'][0]:.1%} - {stats['success_ci'][1]:.1%})")
            report.append(f"- **True success rate**: {stats['true_success_rate']:.1%} "
                         f"(95% CI: {stats['true_success_ci'][0]:.1%} - {stats['true_success_ci'][1]:.1%})")
            
            if stats['speedup_stats']:
                sp = stats['speedup_stats']
                report.append(f"- **Average speedup**: {sp['mean']:.2f}x ± {sp['std']:.2f}x")
                report.append(f"- **Speedup 95% CI**: {sp['ci_lower']:.2f}x - {sp['ci_upper']:.2f}x")
                report.append(f"- **Coefficient of variation**: {sp['cv']:.2f}")
                report.append(f"- **Successful runs**: {sp['n']}/{stats['n_runs']}")
            
            if stats['iteration_stats']:
                it = stats['iteration_stats']
                report.append(f"- **Average iterations**: {it['mean']:.1f} ± {it['std']:.1f}")
            
            # Compiler vectorization
            report.append(f"- **Original vectorized rate**: {stats['original_vectorized_rate']:.1%}")
            report.append(f"- **LLM vectorized rate**: {stats['vectorized_vectorized_rate']:.1%}")
            
            report.append("")
        
        # Stability analysis
        report.append("## Stability Analysis\n")
        
        stable_funcs = [f for f, s in function_stats.items() 
                       if s['speedup_stats'] and s['speedup_stats']['cv'] < 0.2]
        variable_funcs = [f for f, s in function_stats.items() 
                         if s['speedup_stats'] and s['speedup_stats']['cv'] > 0.5]
        
        report.append(f"### Stable Performance (CV < 0.2): {len(stable_funcs)} functions")
        if stable_funcs:
            report.append(f"- {', '.join(stable_funcs)}")
        
        report.append(f"\n### Variable Performance (CV > 0.5): {len(variable_funcs)} functions")
        if variable_funcs:
            report.append(f"- {', '.join(variable_funcs)}")
        
        # Failed Cases Analysis
        report.append("\n## Failed Cases Analysis\n")
        
        # Functions that completely failed
        complete_failures = [f for f, s in function_stats.items() if s['success_count'] == 0]
        partial_failures = [f for f, s in function_stats.items() 
                          if 0 < s['success_count'] < s['n_runs']]
        no_improvement = [f for f, s in function_stats.items() 
                         if s['success_count'] > 0 and s['true_success_count'] == 0]
        
        if complete_failures:
            report.append(f"### Complete Failures: {len(complete_failures)} functions")
            report.append(f"- Functions: {', '.join(complete_failures)}")
            report.append("")
        
        if partial_failures:
            report.append(f"### Partial Failures: {len(partial_failures)} functions")
            for func in partial_failures[:5]:
                stats = function_stats[func]
                report.append(f"- {func}: {stats['success_count']}/{stats['n_runs']} runs succeeded")
            if len(partial_failures) > 5:
                report.append(f"- ... and {len(partial_failures) - 5} more")
            report.append("")
        
        if no_improvement:
            report.append(f"### No Performance Improvement: {len(no_improvement)} functions")
            report.append("Functions that passed correctness but had speedup < 1.0x:")
            no_imp_with_speedup = []
            for func in no_improvement:
                if function_stats[func]['speedup_stats']:
                    speedup = function_stats[func]['speedup_stats']['mean']
                    no_imp_with_speedup.append((func, speedup))
            
            sorted_no_imp = sorted(no_imp_with_speedup, key=lambda x: x[1])
            func_list = ', '.join([f"{f[0]} ({f[1]:.2f}x)" for f in sorted_no_imp[:10]])
            report.append(f"- {func_list}")
            if len(sorted_no_imp) > 10:
                report.append(f"- ... and {len(sorted_no_imp) - 10} more")
            report.append("")
        
        # Recommendations
        report.append("\n## Statistical Recommendations\n")
        report.append("1. **High-confidence functions**: Focus on functions with true success rate CI > 80%")
        report.append("2. **Variable functions**: Investigate sources of variability (CV > 0.5)")
        report.append("3. **Consistent performers**: Leverage functions with stable speedups (CV < 0.2)")
        report.append("4. **Compiler interaction**: Monitor functions with variable compiler vectorization")
        report.append("5. **Sample size**: Consider more runs for functions with wide confidence intervals")
        report.append("6. **Performance threshold**: Functions with speedup < 1.0x are considered failures")
        
        return '\n'.join(report)
    
    def run_complete_analysis(self, results_pattern: str) -> str:
        """Run complete statistical analysis pipeline"""
        print("Loading experimental results...")
        all_results = self.load_multiple_results(results_pattern)
        
        print("Aggregating function data...")
        function_data = self.aggregate_function_data(all_results)
        
        print("Calculating statistics...")
        function_stats = self.analyze_function_statistics(function_data)
        
        print("Categorizing functions...")
        categories = self.categorize_functions(function_stats)
        
        print("Generating report...")
        report = self.generate_statistical_report(function_stats, categories)
        
        return report

def main():
    """Main function for statistical analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Statistical analysis of LLM vectorization experiments')
    parser.add_argument('--pattern', type=str, 
                       default='/home/qinxiao/workspace/*/tsvc_vectorization_results.json',
                       help='Pattern for results files')
    parser.add_argument('--confidence', type=float, default=0.95,
                       help='Confidence level (default: 0.95)')
    parser.add_argument('--output', type=str, default='statistical_analysis.md',
                       help='Output file for statistical report')
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = VectorizationStatistics(confidence_level=args.confidence)
    report = analyzer.run_complete_analysis(args.pattern)
    
    # Save report
    with open(args.output, 'w') as f:
        f.write(report)
    
    print(f"Statistical analysis complete. Report saved to: {args.output}")
    print(f"\\nSummary preview:")
    print(report[:500] + "...")

if __name__ == "__main__":
    main()