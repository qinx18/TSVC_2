# Statistical Framework Usage Guide

## Overview

This guide explains how to use the statistical framework for LLM vectorization analysis with confidence intervals, including how to use existing data (like PE) as part of your statistical analysis.

## Quick Start

### 1. Using Existing PE Data as One Test

**Yes, you can use the PE data as one finished test!** The PE experiment results are already in the correct format and can be included in statistical analysis.

```bash
# Analyze PE data alone (single run - limited statistical value)
python statistical_analysis.py --pattern "/home/qinxiao/workspace/PE/tsvc_vectorization_results.json"
```

### 2. Running Additional Experiments

Use the VS Code launch configurations or command line:

**Via VS Code:**
- Press `F5` or `Ctrl+Shift+P` → "Debug: Select and Start Debugging"
- Choose "Run Multiple Experiments (5 runs)" or "Run Multiple Experiments (10 runs)"

**Via Command Line:**
```bash
# Run 5 additional experiments
python run_multiple_experiments.py --runs 5 --base-dir /home/qinxiao/workspace/TSVC_2

# Run 10 additional experiments  
python run_multiple_experiments.py --runs 10 --base-dir /home/qinxiao/workspace/TSVC_2
```

### 3. Combined Statistical Analysis

**After running additional experiments, combine with PE data:**

**Via VS Code:**
- Choose "Statistical Analysis (Including PE)" from debug configurations

**Via Command Line:**
```bash
# Combine PE data with new experiments
python statistical_analysis.py --pattern "/home/qinxiao/workspace/PE/tsvc_vectorization_results.json,/home/qinxiao/workspace/TSVC_2/experiment_run_*/tsvc_vectorization_results.json" --output "combined_analysis.md"
```

## Available VS Code Launch Configurations

### 1. **Run Multiple Experiments (5 runs)**
- Runs 5 new experiments with different seeds
- Creates `experiment_run_1_*` through `experiment_run_5_*` directories
- Each experiment takes ~2 hours (configurable timeout)

### 2. **Run Multiple Experiments (10 runs)**
- Runs 10 new experiments for higher statistical power
- Better confidence intervals but longer execution time

### 3. **Statistical Analysis (Including PE)**
- Analyzes PE data + any new experiments
- Provides confidence intervals across all runs
- Outputs to `statistical_analysis_with_PE.md`

### 4. **Statistical Analysis (Experiments Only)**
- Analyzes only new experiments (excludes PE)
- Useful for comparing different experimental conditions

### 5. **Check Existing Experiments**
- Shows status of completed experiments
- Useful for monitoring progress

## Understanding the Results

### Single Run (PE Data Only)
```
- Functions analyzed: 50
- Average success rate: 92.0% ± 27.4%
- Average speedup: 3.58x ± 7.69x
```

**Limitations:**
- Wide confidence intervals (±27.4% for success rate)
- No statistical significance testing possible
- Cannot distinguish between true performance and random variation

### Multiple Runs (5+ experiments)
```
- Functions analyzed: 50
- Average success rate: 88.0% ± 8.5%
- Average speedup: 3.42x ± 2.15x
```

**Benefits:**
- Narrower confidence intervals (±8.5% vs ±27.4%)
- Statistical significance testing possible
- Can identify truly stable vs. variable functions

## Function-Level Analysis

### High-Confidence Functions
```
### s256
- **Runs**: 6 (PE + 5 new)
- **Success rate**: 100.0% (95% CI: 61.0% - 100.0%)
- **Average speedup**: 52.3x ± 4.2x
- **Speedup 95% CI**: 47.8x - 56.8x
- **Coefficient of variation**: 0.08 (very stable)
```

### Variable Functions
```
### s342
- **Runs**: 6
- **Success rate**: 83.3% (95% CI: 43.6% - 99.2%)
- **Average speedup**: 0.91x ± 0.35x
- **Speedup 95% CI**: 0.51x - 1.31x
- **Coefficient of variation**: 0.38 (moderate variability)
```

## Statistical Interpretation

### Confidence Intervals
- **95% CI**: We are 95% confident the true value lies within this range
- **Narrow CI**: More precise estimate (need more runs)
- **Wide CI**: Less precise estimate (acceptable for single run)

### Coefficient of Variation (CV)
- **CV < 0.2**: Stable function (consistent performance)
- **CV 0.2-0.5**: Moderate variability
- **CV > 0.5**: High variability (investigate causes)

### Success Rate Interpretation
- **CI above 80%**: High-confidence function for deployment
- **CI spanning 50%**: Uncertain - need more data
- **CI below 50%**: Likely problematic function

## Best Practices

### 1. **Start with PE Data**
- Use PE as your baseline (1 run)
- Provides initial insights with existing data

### 2. **Add Strategic Experiments**
- Start with 3-5 additional runs
- Focus on functions showing promise in PE
- Increase to 10+ runs for critical functions

### 3. **Iterative Analysis**
- Run analysis after each batch of experiments
- Identify functions needing more runs
- Stop when confidence intervals are narrow enough

### 4. **Decision Making**
- Deploy functions with CI > 80% success rate
- Investigate functions with CV > 0.5
- Deprioritize functions with CI < 50% success rate

## File Structure After Experiments

```
TSVC_2/
├── src/
│   ├── statistical_analysis.py
│   ├── run_multiple_experiments.py
│   └── statistical_framework_summary.md
├── experiment_run_1_20240716_140000/
│   ├── tsvc_vectorization_results.json
│   ├── experiment_log.txt
│   └── tsvc_vectorized_attempts/
├── experiment_run_2_20240716_140000/
│   └── ...
└── statistical_analysis_with_PE.md
```

## Troubleshooting

### Common Issues

1. **No experiments found**
   ```bash
   # Check if experiments exist
   python run_multiple_experiments.py --check-only
   ```

2. **Pattern not matching**
   ```bash
   # Use absolute paths
   python statistical_analysis.py --pattern "/full/path/to/results.json"
   ```

3. **Single run limitations**
   - Wide confidence intervals are expected
   - Statistical significance testing not possible
   - More runs needed for robust conclusions

### Performance Considerations

- Each experiment takes ~2 hours
- 5 experiments = ~10 hours total
- 10 experiments = ~20 hours total
- Run overnight or in batches

## Advanced Usage

### Custom Confidence Levels
```bash
python statistical_analysis.py --confidence 0.99  # 99% confidence intervals
```

### Specific Function Analysis
```bash
# Filter results for specific functions (modify script)
python statistical_analysis.py --pattern "results.json" --functions "s256,s1113,s115"
```

### Batch Processing
```bash
# Run multiple analysis types
for confidence in 0.90 0.95 0.99; do
    python statistical_analysis.py --confidence $confidence --output "analysis_${confidence}.md"
done
```

## Next Steps

1. **Immediate**: Run PE-only analysis to understand current baseline
2. **Short-term**: Add 3-5 experiments for key functions
3. **Long-term**: Build comprehensive statistical database with 10+ runs per function
4. **Optimization**: Focus additional runs on functions with wide confidence intervals

## Example Workflow

```bash
# Step 1: Analyze existing PE data
python statistical_analysis.py --pattern "/home/qinxiao/workspace/PE/tsvc_vectorization_results.json"

# Step 2: Run additional experiments
python run_multiple_experiments.py --runs 5

# Step 3: Combined analysis
python statistical_analysis.py --pattern "/home/qinxiao/workspace/PE/tsvc_vectorization_results.json,/home/qinxiao/workspace/TSVC_2/experiment_run_*/tsvc_vectorization_results.json"

# Step 4: Make decisions based on confidence intervals
```

This framework transforms single-run results into statistically robust analysis with proper uncertainty quantification.