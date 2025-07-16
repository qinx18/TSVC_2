#!/usr/bin/env python3
"""
Run multiple LLM vectorization experiments with different seeds for statistical analysis
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
import argparse
import shutil

class MultipleExperimentRunner:
    """Run multiple vectorization experiments with different seeds"""
    
    def __init__(self, base_dir: str, n_runs: int = 5):
        self.base_dir = base_dir
        self.n_runs = n_runs
        self.experiment_dirs = []
        
    def setup_experiment_directories(self):
        """Create separate directories for each experimental run"""
        base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i in range(self.n_runs):
            exp_dir = os.path.join(self.base_dir, f"experiment_run_{i+1}_{base_timestamp}")
            os.makedirs(exp_dir, exist_ok=True)
            self.experiment_dirs.append(exp_dir)
            print(f"Created experiment directory: {exp_dir}")
    
    def modify_vectorizer_for_seed(self, seed: int, output_dir: str):
        """Modify vectorizer.py to use specific seed and output directory"""
        # Read the original vectorizer.py
        vectorizer_path = os.path.join(self.base_dir, "src", "vectorizer.py")
        
        with open(vectorizer_path, 'r') as f:
            content = f.read()
        
        # Add seed parameter to the class initialization
        modified_content = content.replace(
            'self.temperature = 0.7  # Balanced temperature for creative but consistent solutions',
            f'self.temperature = 0.7  # Balanced temperature for creative but consistent solutions\n        self.seed = {seed}'
        )
        
        # Add seed initialization to the class __init__ method
        modified_content = modified_content.replace(
            'self.test_functions = {}',
            f'self.test_functions = {{}}\n        \n        # Set random seed for reproducibility\n        import random\n        import numpy as np\n        random.seed({seed})\n        np.random.seed({seed})'
        )
        
        # Add imports at the top if not already present
        if "import random" not in modified_content[:100]:
            modified_content = modified_content.replace(
                "import anthropic",
                "import anthropic\nimport random\nimport numpy as np"
            )
        
        # Modify paths to use the specific experiment directory
        modified_content = modified_content.replace(
            'tsvc_results_dir = os.path.join(workspace_dir, "tsvc_results")',
            f'tsvc_results_dir = os.path.join("{output_dir}", "tsvc_results")'
        )
        
        modified_content = modified_content.replace(
            'tsvc_attempts_dir = os.path.join(workspace_dir, "tsvc_vectorized_attempts")',
            f'tsvc_attempts_dir = os.path.join("{output_dir}", "tsvc_vectorized_attempts")'
        )
        
        modified_content = modified_content.replace(
            'results_file = os.path.join(workspace_dir, "tsvc_vectorization_results.json")',
            f'results_file = os.path.join("{output_dir}", "tsvc_vectorization_results.json")'
        )
        
        # Write modified vectorizer
        exp_vectorizer_path = os.path.join(output_dir, "vectorizer.py")
        with open(exp_vectorizer_path, 'w') as f:
            f.write(modified_content)
        
        return exp_vectorizer_path
    
    def copy_necessary_files(self, output_dir: str):
        """Copy necessary files to experiment directory"""
        src_dir = os.path.join(self.base_dir, "src")
        
        # Files to copy
        files_to_copy = [
            "tsvc.c",
            "common.h", 
            "common.c",
            "dummy.c",
            "array_defs.h"
        ]
        
        for file_name in files_to_copy:
            src_path = os.path.join(src_dir, file_name)
            dst_path = os.path.join(output_dir, file_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
        
        # Copy Makefile
        makefile_path = os.path.join(self.base_dir, "Makefile")
        if os.path.exists(makefile_path):
            shutil.copy2(makefile_path, output_dir)
    
    def run_single_experiment(self, run_idx: int, seed: int, output_dir: str):
        """Run a single experiment with specified seed"""
        print(f"\\n=== Running Experiment {run_idx + 1}/{self.n_runs} (seed={seed}) ===")
        
        # Setup experiment directory
        self.copy_necessary_files(output_dir)
        
        # Modify vectorizer for this run
        exp_vectorizer_path = self.modify_vectorizer_for_seed(seed, output_dir)
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = output_dir
        
        # Run the experiment
        cmd = [sys.executable, exp_vectorizer_path]
        
        try:
            print(f"Starting experiment in {output_dir}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=output_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Log results
            log_file = os.path.join(output_dir, "experiment_log.txt")
            with open(log_file, 'w') as f:
                f.write(f"Experiment Run {run_idx + 1}\\n")
                f.write(f"Seed: {seed}\\n")
                f.write(f"Duration: {duration:.2f} seconds\\n")
                f.write(f"Return code: {result.returncode}\\n\\n")
                f.write("STDOUT:\\n")
                f.write(result.stdout)
                f.write("\\nSTDERR:\\n")
                f.write(result.stderr)
            
            if result.returncode == 0:
                print(f"✓ Experiment {run_idx + 1} completed successfully ({duration:.1f}s)")
                return True
            else:
                print(f"✗ Experiment {run_idx + 1} failed (return code: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Experiment {run_idx + 1} timed out after 2 hours")
            return False
        except Exception as e:
            print(f"✗ Experiment {run_idx + 1} failed with error: {e}")
            return False
    
    def run_all_experiments(self, function_subset: list = None):
        """Run all experiments"""
        print(f"Starting {self.n_runs} experimental runs...")
        
        # Setup directories
        self.setup_experiment_directories()
        
        successful_runs = 0
        failed_runs = 0
        
        for i, exp_dir in enumerate(self.experiment_dirs):
            seed = 42 + i * 100  # Different seeds for each run
            
            success = self.run_single_experiment(i, seed, exp_dir)
            
            if success:
                successful_runs += 1
            else:
                failed_runs += 1
        
        print(f"\\n=== Experiment Summary ===")
        print(f"Total runs: {self.n_runs}")
        print(f"Successful: {successful_runs}")
        print(f"Failed: {failed_runs}")
        print(f"Success rate: {successful_runs/self.n_runs:.1%}")
        
        return successful_runs, failed_runs
    
    def check_results(self):
        """Check which experiments produced results"""
        results_summary = []
        
        for i, exp_dir in enumerate(self.experiment_dirs):
            results_file = os.path.join(exp_dir, "tsvc_vectorization_results.json")
            
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        data = json.load(f)
                    
                    n_functions = len(data.get('results', []))
                    n_successful = sum(1 for r in data.get('results', []) if r.get('success', False))
                    
                    results_summary.append({
                        'run': i + 1,
                        'dir': exp_dir,
                        'functions': n_functions,
                        'successful': n_successful,
                        'success_rate': n_successful / n_functions if n_functions > 0 else 0
                    })
                    
                except Exception as e:
                    print(f"Error reading {results_file}: {e}")
        
        return results_summary

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run multiple LLM vectorization experiments')
    parser.add_argument('--runs', type=int, default=5,
                       help='Number of experimental runs (default: 5)')
    parser.add_argument('--base-dir', type=str, 
                       default='/home/qinxiao/workspace/TSVC_2',
                       help='Base directory for experiments')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check existing results, don\'t run new experiments')
    
    args = parser.parse_args()
    
    runner = MultipleExperimentRunner(args.base_dir, args.runs)
    
    if args.check_only:
        print("Checking existing results...")
        results = runner.check_results()
        
        if results:
            print(f"\\nFound {len(results)} completed experiments:")
            for r in results:
                print(f"Run {r['run']}: {r['successful']}/{r['functions']} functions "
                      f"({r['success_rate']:.1%}) - {r['dir']}")
        else:
            print("No completed experiments found.")
    else:
        print(f"Running {args.runs} experiments...")
        successful, failed = runner.run_all_experiments()
        
        if successful > 0:
            print("\\nChecking results...")
            results = runner.check_results()
            
            if results:
                print(f"\\nCompleted experiments summary:")
                for r in results:
                    print(f"Run {r['run']}: {r['successful']}/{r['functions']} functions "
                          f"({r['success_rate']:.1%})")
            
            print(f"\\nNext steps:")
            print(f"1. Run statistical analysis:")
            print(f"   python statistical_analysis.py --pattern '{args.base_dir}/experiment_run_*/tsvc_vectorization_results.json'")
            print(f"2. Generate statistical report with confidence intervals")

if __name__ == "__main__":
    main()