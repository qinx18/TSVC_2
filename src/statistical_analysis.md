# TSVC Vectorizer Statistical Analysis Report

## Overall Statistics
- Total functions tested: 50
- Successfully vectorized (checksum pass + speedup >= 1.0x): 46
- Vectorized but no improvement (checksum pass + speedup < 1.0x): 2
- Failed to vectorize: 2
- True success rate: 75.0%
- Average speedup (all attempts): 3.50x ± 5.10x
- Confidence level: 95%

## Performance Analysis

### Performance Distribution:
- **Regression**: 8 functions
  - s277 (0.61x), s232 (0.84x), s342 (0.85x), s222 (0.86x), s221 (0.89x), s321 (0.91x), s231 (0.96x), s141 (0.96x)
- **Minimal**: 9 functions
  - s3112 (1.00x), s451 (1.02x), s112 (1.03x), s343 (1.17x), s161 (1.22x), s123 (1.24x), s114 (1.46x), s2251 (1.50x), s3110 (1.50x)
- **Moderate**: 13 functions
- **Good**: 17 functions
- **Excellent**: 1 functions

## Statistical Categories

### Variable Success: 13 functions
- Functions: s116, s1213, s126, s222, s2251, s231, s233, s241, s242, s31111
- ... and 3 more

### Consistent High Performance: 19 functions
- Functions: s1113, s115, s1161, s1244, s126, s211, s212, s2233, s242, s256
- ... and 9 more

### Variable Performance: 7 functions
- Functions: s2233, s231, s235, s241, s256, s3110, s31111

### Stable Functions: 23 functions
- Functions: s1113, s112, s114, s115, s1161, s123, s1244, s126, s141, s161
- ... and 13 more

### Highly Variable: 7 functions
- Functions: s2233, s231, s235, s241, s256, s3110, s31111

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
- **Average speedup**: 35.26x ± 25.06x
- **Speedup 95% CI**: 17.33x - 53.19x
- **Coefficient of variation**: 0.71
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s275
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 7.19x ± 0.45x
- **Speedup 95% CI**: 6.87x - 7.51x
- **Coefficient of variation**: 0.06
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s115
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 6.71x ± 0.07x
- **Speedup 95% CI**: 6.66x - 6.76x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 100.0%

### s1244
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 6.37x ± 0.02x
- **Speedup 95% CI**: 6.36x - 6.38x
- **Coefficient of variation**: 0.00
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s293
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 6.34x ± 2.91x
- **Speedup 95% CI**: 4.26x - 8.43x
- **Coefficient of variation**: 0.46
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1113
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.74x ± 0.37x
- **Speedup 95% CI**: 5.48x - 6.00x
- **Coefficient of variation**: 0.06
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2233
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.62x ± 4.71x
- **Speedup 95% CI**: 2.25x - 8.98x
- **Coefficient of variation**: 0.84
- **Successful runs**: 10/10
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 20.0%

### s292
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.29x ± 0.38x
- **Speedup 95% CI**: 5.02x - 5.56x
- **Coefficient of variation**: 0.07
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s332
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 5.23x ± 1.14x
- **Speedup 95% CI**: 4.41x - 6.05x
- **Coefficient of variation**: 0.22
- **Successful runs**: 10/10
- **Average iterations**: 1.7 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s291
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 4.80x ± 0.66x
- **Speedup 95% CI**: 4.32x - 5.27x
- **Coefficient of variation**: 0.14
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1161
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 4.74x ± 0.10x
- **Speedup 95% CI**: 4.67x - 4.82x
- **Coefficient of variation**: 0.02
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s212
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 4.12x ± 0.06x
- **Speedup 95% CI**: 4.08x - 4.17x
- **Coefficient of variation**: 0.02
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s442
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.89x ± 0.20x
- **Speedup 95% CI**: 3.75x - 4.03x
- **Coefficient of variation**: 0.05
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s481
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.19x ± 0.94x
- **Speedup 95% CI**: 2.52x - 3.86x
- **Coefficient of variation**: 0.30
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s211
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.11x ± 1.05x
- **Speedup 95% CI**: 2.37x - 3.86x
- **Coefficient of variation**: 0.34
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s281
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 3.10x ± 0.11x
- **Speedup 95% CI**: 3.02x - 3.18x
- **Coefficient of variation**: 0.03
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 20.0%

### s235
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.73x ± 1.41x
- **Speedup 95% CI**: 1.72x - 3.74x
- **Coefficient of variation**: 0.52
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 10.0%

### s261
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 2.08x ± 1.02x
- **Speedup 95% CI**: 1.35x - 2.81x
- **Coefficient of variation**: 0.49
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s258
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.61x ± 0.38x
- **Speedup 95% CI**: 1.34x - 1.89x
- **Coefficient of variation**: 0.24
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s341
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.53x ± 0.17x
- **Speedup 95% CI**: 1.41x - 1.65x
- **Coefficient of variation**: 0.11
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3110
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.50x ± 0.98x
- **Speedup 95% CI**: 0.80x - 2.20x
- **Coefficient of variation**: 0.65
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s114
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.46x ± 0.01x
- **Speedup 95% CI**: 1.46x - 1.47x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s161
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.22x ± 0.14x
- **Speedup 95% CI**: 1.12x - 1.31x
- **Coefficient of variation**: 0.11
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s112
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **Average speedup**: 1.03x ± 0.01x
- **Speedup 95% CI**: 1.02x - 1.04x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s482
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 3.57x ± 1.19x
- **Speedup 95% CI**: 2.72x - 4.42x
- **Coefficient of variation**: 0.33
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 20.0%

### s318
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 2.46x ± 1.08x
- **Speedup 95% CI**: 1.68x - 3.23x
- **Coefficient of variation**: 0.44
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s322
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 2.33x ± 1.09x
- **Speedup 95% CI**: 1.55x - 3.12x
- **Coefficient of variation**: 0.47
- **Successful runs**: 10/10
- **Average iterations**: 1.5 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s323
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 2.18x ± 0.46x
- **Speedup 95% CI**: 1.85x - 2.51x
- **Coefficient of variation**: 0.21
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s123
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.24x ± 0.10x
- **Speedup 95% CI**: 1.16x - 1.31x
- **Coefficient of variation**: 0.08
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s343
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.17x ± 0.24x
- **Speedup 95% CI**: 0.99x - 1.36x
- **Coefficient of variation**: 0.21
- **Successful runs**: 9/10
- **Average iterations**: 1.2 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s3112
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **Average speedup**: 1.00x ± 0.01x
- **Speedup 95% CI**: 1.00x - 1.01x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.5 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s116
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 80.0% (95% CI: 49.0% - 94.3%)
- **Average speedup**: 1.84x ± 0.89x
- **Speedup 95% CI**: 1.15x - 2.53x
- **Coefficient of variation**: 0.48
- **Successful runs**: 9/10
- **Average iterations**: 1.7 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s233
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 80.0% (95% CI: 49.0% - 94.3%)
- **Average speedup**: 1.58x ± 0.40x
- **Speedup 95% CI**: 1.29x - 1.87x
- **Coefficient of variation**: 0.26
- **Successful runs**: 10/10
- **Average iterations**: 1.5 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s451
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 80.0% (95% CI: 49.0% - 94.3%)
- **Average speedup**: 1.02x ± 0.02x
- **Speedup 95% CI**: 1.00x - 1.04x
- **Coefficient of variation**: 0.02
- **Successful runs**: 9/10
- **Average iterations**: 1.4 ± 0.7
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s241
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 70.0% (95% CI: 39.7% - 89.2%)
- **Average speedup**: 2.79x ± 1.41x
- **Speedup 95% CI**: 1.78x - 3.80x
- **Coefficient of variation**: 0.50
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s126
- **Runs**: 10
- **Checksum pass rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **True success rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **Average speedup**: 7.66x ± 0.31x
- **Speedup 95% CI**: 7.34x - 7.98x
- **Coefficient of variation**: 0.04
- **Successful runs**: 6/10
- **Average iterations**: 2.2 ± 0.9
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s1213
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **Average speedup**: 1.98x ± 0.89x
- **Speedup 95% CI**: 1.34x - 2.61x
- **Coefficient of variation**: 0.45
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2251
- **Runs**: 10
- **Checksum pass rate**: 90.0% (95% CI: 59.6% - 98.2%)
- **True success rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **Average speedup**: 1.50x ± 0.73x
- **Speedup 95% CI**: 0.93x - 2.06x
- **Coefficient of variation**: 0.49
- **Successful runs**: 9/10
- **Average iterations**: 1.4 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s231
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **Average speedup**: 0.96x ± 0.51x
- **Speedup 95% CI**: 0.59x - 1.33x
- **Coefficient of variation**: 0.54
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 100.0%
- **LLM vectorized rate**: 0.0%

### s342
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 60.0% (95% CI: 31.3% - 83.2%)
- **Average speedup**: 0.85x ± 0.21x
- **Speedup 95% CI**: 0.70x - 1.00x
- **Coefficient of variation**: 0.25
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s321
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 30.0% (95% CI: 10.8% - 60.3%)
- **Average speedup**: 0.91x ± 0.16x
- **Speedup 95% CI**: 0.79x - 1.02x
- **Coefficient of variation**: 0.18
- **Successful runs**: 10/10
- **Average iterations**: 1.4 ± 0.5
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s31111
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 2.48x ± 3.48x
- **Speedup 95% CI**: -0.00x - 4.97x
- **Coefficient of variation**: 1.40
- **Successful runs**: 10/10
- **Average iterations**: 1.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s242
- **Runs**: 10
- **Checksum pass rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 2.21x ± 0.01x
- **Speedup 95% CI**: 2.14x - 2.27x
- **Coefficient of variation**: 0.00
- **Successful runs**: 2/10
- **Average iterations**: 2.8 ± 0.4
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s222
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 20.0% (95% CI: 5.7% - 51.0%)
- **Average speedup**: 0.86x ± 0.11x
- **Speedup 95% CI**: 0.78x - 0.94x
- **Coefficient of variation**: 0.13
- **Successful runs**: 10/10
- **Average iterations**: 1.8 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s232
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 10.0% (95% CI: 1.8% - 40.4%)
- **Average speedup**: 0.84x ± 0.35x
- **Speedup 95% CI**: 0.59x - 1.09x
- **Coefficient of variation**: 0.41
- **Successful runs**: 10/10
- **Average iterations**: 1.2 ± 0.6
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s277
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 10.0% (95% CI: 1.8% - 40.4%)
- **Average speedup**: 0.61x ± 0.22x
- **Speedup 95% CI**: 0.46x - 0.77x
- **Coefficient of variation**: 0.36
- **Successful runs**: 10/10
- **Average iterations**: 1.7 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s141
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average speedup**: 0.96x ± 0.03x
- **Speedup 95% CI**: 0.94x - 0.99x
- **Coefficient of variation**: 0.03
- **Successful runs**: 10/10
- **Average iterations**: 1.5 ± 0.8
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s221
- **Runs**: 10
- **Checksum pass rate**: 100.0% (95% CI: 72.2% - 100.0%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average speedup**: 0.89x ± 0.01x
- **Speedup 95% CI**: 0.89x - 0.90x
- **Coefficient of variation**: 0.01
- **Successful runs**: 10/10
- **Average iterations**: 1.1 ± 0.3
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

### s2111
- **Runs**: 10
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 10.0%

### s244
- **Runs**: 10
- **Checksum pass rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **True success rate**: 0.0% (95% CI: 0.0% - 27.8%)
- **Average iterations**: 3.0 ± 0.0
- **Original vectorized rate**: 0.0%
- **LLM vectorized rate**: 0.0%

## Stability Analysis

### Stable Performance (CV < 0.2): 23 functions
- s1113, s112, s114, s115, s1161, s123, s1244, s126, s141, s161, s212, s221, s222, s242, s275, s281, s291, s292, s3112, s321, s341, s442, s451

### Variable Performance (CV > 0.5): 7 functions
- s2233, s231, s235, s241, s256, s3110, s31111

## Failed Cases Analysis

### Complete Failures: 2 functions
- Functions: s2111, s244

### Partial Failures: 6 functions
- s116: 9/10 runs succeeded
- s126: 6/10 runs succeeded
- s2251: 9/10 runs succeeded
- s242: 2/10 runs succeeded
- s343: 9/10 runs succeeded
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