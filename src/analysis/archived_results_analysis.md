# TSVC Vectorizer Statistical Analysis Report

## Overall Statistics
- Total functions tested: 50
- Successfully vectorized (checksum pass + speedup >= 1.0x): 46
- Vectorized but no improvement (checksum pass + speedup < 1.0x): 2
- Failed to vectorize: 2
- True success rate: 75.8%
- Average speedup (all attempts): 3.49x ± 4.84x
- Confidence level: 95%

## Performance Analysis

### Performance Distribution:
- **Regression**: 7 functions
  - s277 (0.57x), s342 (0.84x), s232 (0.85x), s222 (0.86x), s221 (0.89x), s321 (0.91x), s141 (0.96x)
- **Minimal**: 8 functions
  - s3112 (1.00x), s231 (1.02x), s451 (1.02x), s112 (1.03x), s343 (1.19x), s161 (1.22x), s123 (1.23x), s114 (1.46x)
- **Moderate**: 14 functions
- **Good**: 18 functions
- **Excellent**: 1 functions

## Statistical Categories

### Variable Success: 21 functions
- Functions: s116, s1213, s123, s126, s222, s2251, s231, s232, s233, s241
- ... and 11 more

### Consistent High Performance: 19 functions
- Functions: s1113, s115, s1161, s1244, s126, s211, s212, s2233, s242, s256
- ... and 9 more

### Variable Performance: 6 functions
- Functions: s116, s2233, s235, s256, s3110, s31111

### Stable Functions: 23 functions
- Functions: s1113, s112, s114, s115, s1161, s123, s1244, s126, s141, s161
- ... and 13 more

### Highly Variable: 6 functions
- Functions: s116, s2233, s235, s256, s3110, s31111

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
- **Average speedup**: 33.29x ± 25.75x
- **Speedup 95% CI**: 13.49x - 53.08x
- **Coefficient of variation**: 0.77
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s275
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 7.21x ± 0.47x
- **Speedup 95% CI**: 6.84x - 7.57x
- **Coefficient of variation**: 0.07
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s115
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.71x ± 0.08x
- **Speedup 95% CI**: 6.65x - 6.77x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 100.0%

### s293
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.65x ± 2.92x
- **Speedup 95% CI**: 4.41x - 8.89x
- **Coefficient of variation**: 0.44
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1244
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.37x ± 0.02x
- **Speedup 95% CI**: 6.36x - 6.39x
- **Coefficient of variation**: 0.00
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2233
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 6.13x ± 4.69x
- **Speedup 95% CI**: 2.53x - 9.73x
- **Coefficient of variation**: 0.76
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 11.1%

### s1113
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 5.71x ± 0.37x
- **Speedup 95% CI**: 5.42x - 5.99x
- **Coefficient of variation**: 0.07
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s292
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 5.30x ± 0.40x
- **Speedup 95% CI**: 5.00x - 5.61x
- **Coefficient of variation**: 0.07
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s332
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 5.15x ± 1.18x
- **Speedup 95% CI**: 4.24x - 6.06x
- **Coefficient of variation**: 0.23
- **Successful runs**: 9/9
- **Average iterations**: 1.7 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s291
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 4.84x ± 0.69x
- **Speedup 95% CI**: 4.31x - 5.37x
- **Coefficient of variation**: 0.14
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1161
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 4.74x ± 0.11x
- **Speedup 95% CI**: 4.65x - 4.82x
- **Coefficient of variation**: 0.02
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s212
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 4.11x ± 0.06x
- **Speedup 95% CI**: 4.07x - 4.16x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s442
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.86x ± 0.18x
- **Speedup 95% CI**: 3.72x - 3.99x
- **Coefficient of variation**: 0.05
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s211
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.25x ± 1.01x
- **Speedup 95% CI**: 2.47x - 4.03x
- **Coefficient of variation**: 0.31
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s481
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.15x ± 0.99x
- **Speedup 95% CI**: 2.39x - 3.91x
- **Coefficient of variation**: 0.31
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s281
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 3.09x ± 0.11x
- **Speedup 95% CI**: 3.01x - 3.17x
- **Coefficient of variation**: 0.03
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s235
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.60x ± 1.43x
- **Speedup 95% CI**: 1.50x - 3.70x
- **Coefficient of variation**: 0.55
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 11.1%

### s322
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.52x ± 0.98x
- **Speedup 95% CI**: 1.77x - 3.27x
- **Coefficient of variation**: 0.39
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s261
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 2.15x ± 1.06x
- **Speedup 95% CI**: 1.33x - 2.96x
- **Coefficient of variation**: 0.50
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s258
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.63x ± 0.40x
- **Speedup 95% CI**: 1.33x - 1.94x
- **Coefficient of variation**: 0.25
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s341
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.54x ± 0.18x
- **Speedup 95% CI**: 1.41x - 1.67x
- **Coefficient of variation**: 0.11
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3110
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.53x ± 1.03x
- **Speedup 95% CI**: 0.74x - 2.32x
- **Coefficient of variation**: 0.67
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s114
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.46x ± 0.01x
- **Speedup 95% CI**: 1.45x - 1.47x
- **Coefficient of variation**: 0.00
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s161
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.22x ± 0.15x
- **Speedup 95% CI**: 1.10x - 1.33x
- **Coefficient of variation**: 0.12
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s112
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **Average speedup**: 1.03x ± 0.01x
- **Speedup 95% CI**: 1.02x - 1.04x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s482
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 3.47x ± 1.21x
- **Speedup 95% CI**: 2.54x - 4.40x
- **Coefficient of variation**: 0.35
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 22.2%

### s318
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 2.29x ± 1.00x
- **Speedup 95% CI**: 1.52x - 3.06x
- **Coefficient of variation**: 0.44
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s323
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 2.17x ± 0.49x
- **Speedup 95% CI**: 1.80x - 2.54x
- **Coefficient of variation**: 0.22
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s233
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.64x ± 0.37x
- **Speedup 95% CI**: 1.36x - 1.92x
- **Coefficient of variation**: 0.22
- **Successful runs**: 9/9
- **Average iterations**: 1.6 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s123
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.23x ± 0.10x
- **Speedup 95% CI**: 1.15x - 1.31x
- **Coefficient of variation**: 0.08
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s343
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **Average speedup**: 1.19x ± 0.26x
- **Speedup 95% CI**: 0.97x - 1.40x
- **Coefficient of variation**: 0.22
- **Successful runs**: 8/9
- **Average iterations**: 1.2 ± 0.7
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
- **Average iterations**: 1.6 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s241
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 77.8% (95% CI: 45.3% - 93.7%)
- **Average speedup**: 3.00x ± 1.31x
- **Speedup 95% CI**: 2.00x - 4.01x
- **Coefficient of variation**: 0.44
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s116
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 77.8% (95% CI: 45.3% - 93.7%)
- **Average speedup**: 1.86x ± 0.95x
- **Speedup 95% CI**: 1.07x - 2.66x
- **Coefficient of variation**: 0.51
- **Successful runs**: 8/9
- **Average iterations**: 1.8 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s451
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 77.8% (95% CI: 45.3% - 93.7%)
- **Average speedup**: 1.02x ± 0.02x
- **Speedup 95% CI**: 1.01x - 1.04x
- **Coefficient of variation**: 0.02
- **Successful runs**: 8/9
- **Average iterations**: 1.3 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s126
- **Runs**: 9
- **Checksum pass rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **True success rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **Average speedup**: 7.66x ± 0.31x
- **Speedup 95% CI**: 7.34x - 7.98x
- **Coefficient of variation**: 0.04
- **Successful runs**: 6/9
- **Average iterations**: 2.1 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2251
- **Runs**: 9
- **Checksum pass rate**: 88.9% (95% CI: 56.5% - 98.0%)
- **True success rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **Average speedup**: 1.57x ± 0.75x
- **Speedup 95% CI**: 0.95x - 2.20x
- **Coefficient of variation**: 0.48
- **Successful runs**: 8/9
- **Average iterations**: 1.4 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s231
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 66.7% (95% CI: 35.4% - 87.9%)
- **Average speedup**: 1.02x ± 0.50x
- **Speedup 95% CI**: 0.64x - 1.41x
- **Coefficient of variation**: 0.49
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s1213
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 55.6% (95% CI: 26.7% - 81.1%)
- **Average speedup**: 1.90x ± 0.90x
- **Speedup 95% CI**: 1.20x - 2.59x
- **Coefficient of variation**: 0.48
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s342
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 55.6% (95% CI: 26.7% - 81.1%)
- **Average speedup**: 0.84x ± 0.21x
- **Speedup 95% CI**: 0.67x - 1.00x
- **Coefficient of variation**: 0.26
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s321
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 33.3% (95% CI: 12.1% - 64.6%)
- **Average speedup**: 0.91x ± 0.17x
- **Speedup 95% CI**: 0.77x - 1.04x
- **Coefficient of variation**: 0.19
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s31111
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 2.67x ± 3.63x
- **Speedup 95% CI**: -0.13x - 5.46x
- **Coefficient of variation**: 1.36
- **Successful runs**: 9/9
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s242
- **Runs**: 9
- **Checksum pass rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 2.21x ± 0.01x
- **Speedup 95% CI**: 2.14x - 2.27x
- **Coefficient of variation**: 0.00
- **Successful runs**: 2/9
- **Average iterations**: 2.8 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s222
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 22.2% (95% CI: 6.3% - 54.7%)
- **Average speedup**: 0.86x ± 0.12x
- **Speedup 95% CI**: 0.77x - 0.95x
- **Coefficient of variation**: 0.14
- **Successful runs**: 9/9
- **Average iterations**: 1.9 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s232
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 11.1% (95% CI: 2.0% - 43.5%)
- **Average speedup**: 0.85x ± 0.36x
- **Speedup 95% CI**: 0.57x - 1.13x
- **Coefficient of variation**: 0.43
- **Successful runs**: 9/9
- **Average iterations**: 1.2 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s277
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 11.1% (95% CI: 2.0% - 43.5%)
- **Average speedup**: 0.57x ± 0.19x
- **Speedup 95% CI**: 0.43x - 0.72x
- **Coefficient of variation**: 0.33
- **Successful runs**: 9/9
- **Average iterations**: 1.8 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s141
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average speedup**: 0.96x ± 0.03x
- **Speedup 95% CI**: 0.94x - 0.99x
- **Coefficient of variation**: 0.04
- **Successful runs**: 9/9
- **Average iterations**: 1.4 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s221
- **Runs**: 9
- **Checksum pass rate**: 100.0% (95% CI: 70.1% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average speedup**: 0.89x ± 0.01x
- **Speedup 95% CI**: 0.89x - 0.90x
- **Coefficient of variation**: 0.01
- **Successful runs**: 9/9
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2111
- **Runs**: 9
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 11.1%

### s244
- **Runs**: 9
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **True success rate**: 0.0% (95% CI: 0.0% - 29.9%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

## Stability Analysis

### Stable Performance (CV < 0.2): 23 functions
- s1113, s112, s114, s115, s1161, s123, s1244, s126, s141, s161, s212, s221, s222, s242, s275, s281, s291, s292, s3112, s321, s341, s442, s451

### Variable Performance (CV > 0.5): 6 functions
- s116, s2233, s235, s256, s3110, s31111

## Failed Cases Analysis

### Complete Failures: 2 functions
- Functions: s2111, s244

### Partial Failures: 6 functions
- s116: 8/9 runs succeeded
- s126: 6/9 runs succeeded
- s2251: 8/9 runs succeeded
- s242: 2/9 runs succeeded
- s343: 8/9 runs succeeded
- ... and 1 more

### No Performance Improvement: 2 functions
Functions that passed correctness but had speedup < 1.0x:
- s221 (0.89x), s141 (0.96x)


## Statistical Recommendations

1. **High-confidence functions**: Focus on functions with true success rate CI > 80%
2. **Variable functions**: Investigate sources of variability (CV > 0.5)
3. **Consistent performers**: Leverage functions with stable speedups (CV < 0.2)
4. **Compiler interaction**: Monitor functions with variable compiler vectorization
5. **Sample size**: Consider more runs for functions with wide confidence intervals
6. **Performance threshold**: Functions with speedup < 1.0x are considered failures