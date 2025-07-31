# TSVC Vectorizer Statistical Analysis Report

## Overall Statistics
- Total functions tested: 50
- Successfully vectorized (checksum pass + speedup >= 1.0x): 47
- Vectorized but no improvement (checksum pass + speedup < 1.0x): 2
- Failed to vectorize: 1
- True success rate: 75.2%
- Average speedup (all attempts): 3.42x ± 4.61x
- Confidence level: 95%

## Performance Analysis

### Performance Distribution:
- **Regression**: 6 functions
  - s277 (0.64x), s342 (0.69x), s231 (0.77x), s222 (0.82x), s141 (0.83x), s221 (0.89x)
- **Minimal**: 12 functions
  - s3112 (1.01x), s112 (1.04x), s451 (1.05x), s343 (1.14x), s232 (1.15x), s123 (1.23x), s258 (1.31x), s321 (1.31x), s341 (1.40x), s1213 (1.44x), s114 (1.46x), s161 (1.49x)
- **Moderate**: 10 functions
- **Good**: 20 functions
- **Excellent**: 1 functions

## Statistical Categories

### Variable Success: 13 functions
- Functions: s1213, s126, s2251, s231, s232, s242, s244, s277, s31111, s321
- ... and 3 more

### Consistent High Performance: 21 functions
- Functions: s1113, s115, s1161, s1244, s126, s212, s235, s241, s242, s244
- ... and 11 more

### Variable Performance: 9 functions
- Functions: s1213, s2233, s231, s232, s256, s3110, s31111, s321, s322

### Stable Functions: 23 functions
- Functions: s1113, s112, s114, s115, s1161, s123, s1244, s212, s221, s222
- ... and 13 more

### Highly Variable: 9 functions
- Functions: s1213, s2233, s231, s232, s256, s3110, s31111, s321, s322

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
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 31.64x ± 26.60x
- **Speedup 95% CI**: 12.61x - 50.66x
- **Coefficient of variation**: 0.84
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s293
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 8.05x ± 2.40x
- **Speedup 95% CI**: 6.33x - 9.77x
- **Coefficient of variation**: 0.30
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s275
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 7.14x ± 0.63x
- **Speedup 95% CI**: 6.69x - 7.59x
- **Coefficient of variation**: 0.09
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s115
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 6.70x ± 0.13x
- **Speedup 95% CI**: 6.61x - 6.79x
- **Coefficient of variation**: 0.02
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 100.0%

### s1244
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 6.30x ± 0.32x
- **Speedup 95% CI**: 6.07x - 6.54x
- **Coefficient of variation**: 0.05
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s332
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.78x ± 0.47x
- **Speedup 95% CI**: 5.45x - 6.12x
- **Coefficient of variation**: 0.08
- **Successful runs**: 10/10
- **Average iterations**: 1.9 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s292
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.10x ± 0.85x
- **Speedup 95% CI**: 4.49x - 5.71x
- **Coefficient of variation**: 0.17
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1161
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 4.81x ± 0.25x
- **Speedup 95% CI**: 4.63x - 4.99x
- **Coefficient of variation**: 0.05
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s291
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 4.56x ± 0.54x
- **Speedup 95% CI**: 4.17x - 4.94x
- **Coefficient of variation**: 0.12
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s442
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.96x ± 0.30x
- **Speedup 95% CI**: 3.74x - 4.17x
- **Coefficient of variation**: 0.07
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s212
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.92x ± 0.28x
- **Speedup 95% CI**: 3.72x - 4.12x
- **Coefficient of variation**: 0.07
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s481
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.21x ± 1.00x
- **Speedup 95% CI**: 2.50x - 3.93x
- **Coefficient of variation**: 0.31
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 20.0%

### s235
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.02x ± 1.30x
- **Speedup 95% CI**: 2.09x - 3.95x
- **Coefficient of variation**: 0.43
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s281
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.00x ± 0.35x
- **Speedup 95% CI**: 2.75x - 3.25x
- **Coefficient of variation**: 0.12
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 20.0%

### s211
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.61x ± 1.10x
- **Speedup 95% CI**: 1.83x - 3.40x
- **Coefficient of variation**: 0.42
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s261
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.54x ± 1.12x
- **Speedup 95% CI**: 1.74x - 3.34x
- **Coefficient of variation**: 0.44
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s323
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.33x ± 0.05x
- **Speedup 95% CI**: 2.29x - 2.37x
- **Coefficient of variation**: 0.02
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s318
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.20x ± 0.49x
- **Speedup 95% CI**: 1.85x - 2.55x
- **Coefficient of variation**: 0.22
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s233
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.09x ± 0.87x
- **Speedup 95% CI**: 1.46x - 2.71x
- **Coefficient of variation**: 0.42
- **Successful runs**: 10/10
- **Average iterations**: 1.5 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3110
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.78x ± 1.15x
- **Speedup 95% CI**: 0.96x - 2.61x
- **Coefficient of variation**: 0.64
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s161
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.49x ± 0.53x
- **Speedup 95% CI**: 1.11x - 1.87x
- **Coefficient of variation**: 0.36
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s114
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.46x ± 0.04x
- **Speedup 95% CI**: 1.43x - 1.48x
- **Coefficient of variation**: 0.03
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s123
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.23x ± 0.07x
- **Speedup 95% CI**: 1.18x - 1.27x
- **Coefficient of variation**: 0.06
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s343
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.14x ± 0.08x
- **Speedup 95% CI**: 1.08x - 1.19x
- **Coefficient of variation**: 0.07
- **Successful runs**: 10/10
- **Average iterations**: 1.6 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s112
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.04x ± 0.03x
- **Speedup 95% CI**: 1.02x - 1.06x
- **Coefficient of variation**: 0.03
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s1113
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 5.40x ± 0.16x
- **Speedup 95% CI**: 5.28x - 5.52x
- **Coefficient of variation**: 0.03
- **Successful runs**: 9/10
- **Average iterations**: 1.9 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2233
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 4.99x ± 4.40x
- **Speedup 95% CI**: 1.85x - 8.14x
- **Coefficient of variation**: 0.88
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 10.0%

### s482
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 3.48x ± 1.15x
- **Speedup 95% CI**: 2.66x - 4.31x
- **Coefficient of variation**: 0.33
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 20.0%

### s241
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 3.18x ± 0.92x
- **Speedup 95% CI**: 2.52x - 3.83x
- **Coefficient of variation**: 0.29
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s116
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.77x ± 0.82x
- **Speedup 95% CI**: 1.18x - 2.35x
- **Coefficient of variation**: 0.47
- **Successful runs**: 10/10
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s258
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.31x ± 0.24x
- **Speedup 95% CI**: 1.14x - 1.48x
- **Coefficient of variation**: 0.18
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s451
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.05x ± 0.02x
- **Speedup 95% CI**: 1.03x - 1.07x
- **Coefficient of variation**: 0.02
- **Successful runs**: 9/10
- **Average iterations**: 1.6 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3112
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.01x ± 0.01x
- **Speedup 95% CI**: 1.00x - 1.01x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.4 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s341
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 80.0% (95% CI: 49.0% - 94.3%)
- **Average speedup**: 1.40x ± 0.44x
- **Speedup 95% CI**: 1.08x - 1.71x
- **Coefficient of variation**: 0.31
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s31111
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 70.0% (95% CI: 39.7% - 89.2%)
- **Average speedup**: 3.23x ± 3.47x
- **Speedup 95% CI**: 0.74x - 5.71x
- **Coefficient of variation**: 1.08
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2251
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 70.0% (95% CI: 39.7% - 89.2%)
- **Average speedup**: 1.73x ± 0.77x
- **Speedup 95% CI**: 1.18x - 2.28x
- **Coefficient of variation**: 0.44
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s126
- **Runs**: 10
- **Checksum pass rate**: 50.0% (95% CI: 23.7% - 76.3%)
- **True success rate**: 50.0% (95% CI: 23.7% - 76.3%)
- **Average speedup**: 5.90x ± 2.53x
- **Speedup 95% CI**: 2.75x - 9.04x
- **Coefficient of variation**: 0.43
- **Successful runs**: 5/10
- **Average iterations**: 2.4 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s322
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 40.0% (95% CI: 16.8% - 68.7%)
- **Average speedup**: 1.52x ± 1.20x
- **Speedup 95% CI**: 0.66x - 2.38x
- **Coefficient of variation**: 0.79
- **Successful runs**: 10/10
- **Average iterations**: 1.7 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s232
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 40.0% (95% CI: 16.8% - 68.7%)
- **Average speedup**: 1.15x ± 0.62x
- **Speedup 95% CI**: 0.71x - 1.59x
- **Coefficient of variation**: 0.54
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s231
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 40.0% (95% CI: 16.8% - 68.7%)
- **Average speedup**: 0.77x ± 0.54x
- **Speedup 95% CI**: 0.39x - 1.16x
- **Coefficient of variation**: 0.70
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 10.0%

### s1213
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 30.0% (95% CI: 10.8% - 60.3%)
- **Average speedup**: 1.44x ± 0.89x
- **Speedup 95% CI**: 0.80x - 2.07x
- **Coefficient of variation**: 0.62
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s321
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 30.0% (95% CI: 10.8% - 60.3%)
- **Average speedup**: 1.31x ± 1.25x
- **Speedup 95% CI**: 0.36x - 2.27x
- **Coefficient of variation**: 0.95
- **Successful runs**: 9/10
- **Average iterations**: 1.5 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s244
- **Runs**: 10
- **Checksum pass rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 3.87x ± 0.14x
- **Speedup 95% CI**: 2.60x - 5.14x
- **Coefficient of variation**: 0.04
- **Successful runs**: 2/10
- **Average iterations**: 2.6 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s242
- **Runs**: 10
- **Checksum pass rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 2.30x ± 0.03x
- **Speedup 95% CI**: 2.05x - 2.55x
- **Coefficient of variation**: 0.01
- **Successful runs**: 2/10
- **Average iterations**: 2.8 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s342
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 0.69x ± 0.28x
- **Speedup 95% CI**: 0.48x - 0.89x
- **Coefficient of variation**: 0.41
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s277
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 0.64x ± 0.26x
- **Speedup 95% CI**: 0.45x - 0.83x
- **Coefficient of variation**: 0.41
- **Successful runs**: 10/10
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s141
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 10.0% (95% CI: 1.8% - 40.4%)
- **Average speedup**: 0.83x ± 0.21x
- **Speedup 95% CI**: 0.67x - 0.99x
- **Coefficient of variation**: 0.25
- **Successful runs**: 9/10
- **Average iterations**: 1.9 ± 1.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s221
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average speedup**: 0.89x ± 0.01x
- **Speedup 95% CI**: 0.88x - 0.90x
- **Coefficient of variation**: 0.02
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s222
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average speedup**: 0.82x ± 0.05x
- **Speedup 95% CI**: 0.79x - 0.86x
- **Coefficient of variation**: 0.06
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2111
- **Runs**: 10
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

## Stability Analysis

### Stable Performance (CV < 0.2): 23 functions
- s1113, s112, s114, s115, s1161, s123, s1244, s212, s221, s222, s242, s244, s258, s275, s281, s291, s292, s3112, s323, s332, s343, s442, s451

### Variable Performance (CV > 0.5): 9 functions
- s1213, s2233, s231, s232, s256, s3110, s31111, s321, s322

## Failed Cases Analysis

### Complete Failures: 1 functions
- Functions: s2111

### Partial Failures: 7 functions
- s1113: 9/10 runs succeeded
- s126: 5/10 runs succeeded
- s141: 9/10 runs succeeded
- s242: 2/10 runs succeeded
- s244: 2/10 runs succeeded
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