# TSVC Vectorizer Statistical Analysis Report

## Overall Statistics
- Total functions tested: 50
- Successfully vectorized (checksum pass + speedup >= 1.0x): 47
- Vectorized but no improvement (checksum pass + speedup < 1.0x): 2
- Failed to vectorize: 1
- True success rate: 75.6%
- Average speedup (all attempts): 3.49x ± 4.97x
- Confidence level: 95%

## Performance Analysis

### Performance Distribution:
- **Regression**: 7 functions
  - s277 (0.60x), s342 (0.70x), s231 (0.82x), s222 (0.82x), s141 (0.82x), s221 (0.89x), s321 (0.90x)
- **Minimal**: 10 functions
  - s3112 (1.00x), s112 (1.05x), s451 (1.05x), s343 (1.12x), s232 (1.20x), s123 (1.23x), s258 (1.36x), s341 (1.39x), s114 (1.46x), s1213 (1.49x)
- **Moderate**: 13 functions
- **Good**: 18 functions
- **Excellent**: 1 functions

## Statistical Categories

### Variable Success: 20 functions
- Functions: s1113, s116, s1213, s126, s141, s2233, s2251, s231, s232, s241
- ... and 10 more

### Consistent High Performance: 20 functions
- Functions: s1113, s115, s1161, s1244, s126, s212, s241, s242, s244, s256
- ... and 10 more

### Variable Performance: 8 functions
- Functions: s1213, s2233, s231, s232, s256, s3110, s31111, s322

### Stable Functions: 25 functions
- Functions: s1113, s112, s114, s115, s1161, s123, s1244, s212, s221, s222
- ... and 15 more

### Highly Variable: 8 functions
- Functions: s1213, s2233, s231, s232, s256, s3110, s31111, s322

### Compiler Consistent: 50 functions
- Functions: s1113, s112, s114, s115, s116, s1161, s1213, s123, s1244, s126
- ... and 40 more

## Compiler Vectorization Analysis

### Vectorization Patterns:
- **Original Already Vectorized**: 4 functions
  - Functions: s112, s2233, s231, s235
- **LLM Broke Vectorization**: 4 functions
  - Functions: s112, s2233, s231, s235
- **LLM Enabled Vectorization**: 1 functions
  - Functions: s115
- **Both Not Vectorized**: 45 functions

## Function-Level Statistical Analysis

### s256
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 34.30x ± 26.75x
- **Speedup 95% CI**: 13.74x - 54.87x
- **Coefficient of variation**: 0.78
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s293
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 7.97x ± 2.53x
- **Speedup 95% CI**: 6.02x - 9.92x
- **Coefficient of variation**: 0.32
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s275
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 7.07x ± 0.62x
- **Speedup 95% CI**: 6.59x - 7.55x
- **Coefficient of variation**: 0.09
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s115
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.68x ± 0.12x
- **Speedup 95% CI**: 6.59x - 6.77x
- **Coefficient of variation**: 0.02
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 100.0%

### s1244
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.27x ± 0.33x
- **Speedup 95% CI**: 6.02x - 6.53x
- **Coefficient of variation**: 0.05
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s332
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 5.89x ± 0.35x
- **Speedup 95% CI**: 5.62x - 6.16x
- **Coefficient of variation**: 0.06
- **Successful runs**: 9/9
- **Average iterations**: 1.9 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s292
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 5.08x ± 0.90x
- **Speedup 95% CI**: 4.39x - 5.77x
- **Coefficient of variation**: 0.18
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1161
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 4.81x ± 0.26x
- **Speedup 95% CI**: 4.60x - 5.01x
- **Coefficient of variation**: 0.05
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s291
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 4.60x ± 0.55x
- **Speedup 95% CI**: 4.17x - 5.03x
- **Coefficient of variation**: 0.12
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s212
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.98x ± 0.21x
- **Speedup 95% CI**: 3.82x - 4.14x
- **Coefficient of variation**: 0.05
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s442
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.96x ± 0.31x
- **Speedup 95% CI**: 3.72x - 4.20x
- **Coefficient of variation**: 0.08
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s482
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.80x ± 0.61x
- **Speedup 95% CI**: 3.33x - 4.27x
- **Coefficient of variation**: 0.16
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s481
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.32x ± 1.00x
- **Speedup 95% CI**: 2.55x - 4.09x
- **Coefficient of variation**: 0.30
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s281
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.99x ± 0.37x
- **Speedup 95% CI**: 2.71x - 3.27x
- **Coefficient of variation**: 0.12
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s235
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.92x ± 1.34x
- **Speedup 95% CI**: 1.89x - 3.95x
- **Coefficient of variation**: 0.46
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s211
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.70x ± 1.13x
- **Speedup 95% CI**: 1.83x - 3.57x
- **Coefficient of variation**: 0.42
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s261
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.41x ± 1.10x
- **Speedup 95% CI**: 1.56x - 3.25x
- **Coefficient of variation**: 0.46
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s323
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.33x ± 0.06x
- **Speedup 95% CI**: 2.28x - 2.37x
- **Coefficient of variation**: 0.02
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s318
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.23x ± 0.51x
- **Speedup 95% CI**: 1.84x - 2.62x
- **Coefficient of variation**: 0.23
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s233
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.97x ± 0.84x
- **Speedup 95% CI**: 1.32x - 2.62x
- **Coefficient of variation**: 0.43
- **Successful runs**: 9/9
- **Average iterations**: 1.6 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3110
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.85x ± 1.20x
- **Speedup 95% CI**: 0.92x - 2.77x
- **Coefficient of variation**: 0.65
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s161
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.52x ± 0.55x
- **Speedup 95% CI**: 1.09x - 1.94x
- **Coefficient of variation**: 0.36
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s114
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.46x ± 0.04x
- **Speedup 95% CI**: 1.42x - 1.49x
- **Coefficient of variation**: 0.03
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s258
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.36x ± 0.18x
- **Speedup 95% CI**: 1.22x - 1.50x
- **Coefficient of variation**: 0.13
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s123
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.23x ± 0.07x
- **Speedup 95% CI**: 1.17x - 1.28x
- **Coefficient of variation**: 0.06
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s343
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.12x ± 0.08x
- **Speedup 95% CI**: 1.06x - 1.18x
- **Coefficient of variation**: 0.07
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s112
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.05x ± 0.03x
- **Speedup 95% CI**: 1.02x - 1.07x
- **Coefficient of variation**: 0.03
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s1113
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 5.44x ± 0.11x
- **Speedup 95% CI**: 5.36x - 5.53x
- **Coefficient of variation**: 0.02
- **Successful runs**: 8/9
- **Average iterations**: 1.9 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2233
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 5.04x ± 4.66x
- **Speedup 95% CI**: 1.46x - 8.63x
- **Coefficient of variation**: 0.92
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 11.1%

### s241
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 3.18x ± 0.97x
- **Speedup 95% CI**: 2.44x - 3.93x
- **Coefficient of variation**: 0.30
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s116
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.80x ± 0.87x
- **Speedup 95% CI**: 1.13x - 2.46x
- **Coefficient of variation**: 0.48
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s451
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.05x ± 0.02x
- **Speedup 95% CI**: 1.03x - 1.07x
- **Coefficient of variation**: 0.02
- **Successful runs**: 8/9
- **Average iterations**: 1.7 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3112
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.00x ± 0.01x
- **Speedup 95% CI**: 1.00x - 1.01x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s341
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 77.8% (95% CI: 45.3% - 93.7%)
- **Average speedup**: 1.39x ± 0.47x
- **Speedup 95% CI**: 1.03x - 1.75x
- **Coefficient of variation**: 0.33
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s31111
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **Average speedup**: 3.47x ± 3.59x
- **Speedup 95% CI**: 0.72x - 6.23x
- **Coefficient of variation**: 1.03
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2251
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **Average speedup**: 1.66x ± 0.78x
- **Speedup 95% CI**: 1.06x - 2.25x
- **Coefficient of variation**: 0.47
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s126
- **Runs**: 9
- **Checksum pass rate**: 55.6% (95% CI: 26.7% - 81.1%)
- **True success rate**: 55.6% (95% CI: 26.7% - 81.1%)
- **Average speedup**: 5.90x ± 2.53x
- **Speedup 95% CI**: 2.75x - 9.04x
- **Coefficient of variation**: 0.43
- **Successful runs**: 5/9
- **Average iterations**: 2.3 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s322
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 44.4% (95% CI: 18.9% - 73.3%)
- **Average speedup**: 1.61x ± 1.24x
- **Speedup 95% CI**: 0.66x - 2.56x
- **Coefficient of variation**: 0.77
- **Successful runs**: 9/9
- **Average iterations**: 1.7 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s232
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 44.4% (95% CI: 18.9% - 73.3%)
- **Average speedup**: 1.20x ± 0.63x
- **Speedup 95% CI**: 0.71x - 1.69x
- **Coefficient of variation**: 0.53
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s231
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 44.4% (95% CI: 18.9% - 73.3%)
- **Average speedup**: 0.82x ± 0.55x
- **Speedup 95% CI**: 0.39x - 1.24x
- **Coefficient of variation**: 0.68
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 11.1%

### s1213
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 33.3% (95% CI: 12.1% - 64.6%)
- **Average speedup**: 1.49x ± 0.93x
- **Speedup 95% CI**: 0.78x - 2.20x
- **Coefficient of variation**: 0.62
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s244
- **Runs**: 9
- **Checksum pass rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 3.87x ± 0.14x
- **Speedup 95% CI**: 2.60x - 5.14x
- **Coefficient of variation**: 0.04
- **Successful runs**: 2/9
- **Average iterations**: 2.6 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s242
- **Runs**: 9
- **Checksum pass rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 2.30x ± 0.03x
- **Speedup 95% CI**: 2.05x - 2.55x
- **Coefficient of variation**: 0.01
- **Successful runs**: 2/9
- **Average iterations**: 2.8 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s321
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 0.90x ± 0.08x
- **Speedup 95% CI**: 0.84x - 0.96x
- **Coefficient of variation**: 0.09
- **Successful runs**: 8/9
- **Average iterations**: 1.6 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s342
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 0.70x ± 0.30x
- **Speedup 95% CI**: 0.47x - 0.93x
- **Coefficient of variation**: 0.43
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s141
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 11.1% (95% CI: 2.0% - 43.5%)
- **Average speedup**: 0.82x ± 0.22x
- **Speedup 95% CI**: 0.64x - 1.01x
- **Coefficient of variation**: 0.27
- **Successful runs**: 8/9
- **Average iterations**: 1.8 ± 1.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s277
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 11.1% (95% CI: 2.0% - 43.5%)
- **Average speedup**: 0.60x ± 0.23x
- **Speedup 95% CI**: 0.42x - 0.78x
- **Coefficient of variation**: 0.39
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s221
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average speedup**: 0.89x ± 0.01x
- **Speedup 95% CI**: 0.88x - 0.90x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s222
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average speedup**: 0.82x ± 0.05x
- **Speedup 95% CI**: 0.78x - 0.86x
- **Coefficient of variation**: 0.06
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2111
- **Runs**: 9
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

## Stability Analysis

### Stable Performance (CV < 0.2): 25 functions
- s1113, s112, s114, s115, s1161, s123, s1244, s212, s221, s222, s242, s244, s258, s275, s281, s291, s292, s3112, s321, s323, s332, s343, s442, s451, s482

### Variable Performance (CV > 0.5): 8 functions
- s1213, s2233, s231, s232, s256, s3110, s31111, s322

## Failed Cases Analysis

### Complete Failures: 1 functions
- Functions: s2111

### Partial Failures: 7 functions
- s1113: 8/9 runs succeeded
- s126: 5/9 runs succeeded
- s141: 8/9 runs succeeded
- s242: 2/9 runs succeeded
- s244: 2/9 runs succeeded
- ... and 2 more

### No Performance Improvement: 2 functions
Functions that passed correctness but had speedup < 1.0x:
- s222 (0.82x), s221 (0.89x)


## Statistical Recommendations

1. **High-confidence functions**: Focus on functions with true success rate CI > 80%
2. **Variable functions**: Investigate sources of variability (CV > 0.5)
3. **Consistent performers**: Leverage functions with stable speedups (CV < 0.2)
4. **Compiler interaction**: Monitor functions with variable compiler vectorization
5. **Sample size**: Consider more runs for functions with wide confidence intervals
6. **Performance threshold**: Functions with speedup < 1.0x are considered failures