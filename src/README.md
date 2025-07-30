# TSVC Vectorization Framework - Source Directory

This directory contains the organized source code and tools for the TSVC vectorization project.

## Directory Structure

### 📁 core/
**Core TSVC Infrastructure** - Essential files for the vectorization framework
- `tsvc.c` - Main TSVC benchmark suite
- `common.c` - Core functions (includes checksum precision fix)
- `common.h` - Header definitions
- `array_defs.h` - Array size and alignment definitions
- `dummy.c` - Dummy function implementation
- `Makefile` - Build configuration

### 📁 tools/
**Main Vectorization Tools** - Primary executable tools
- `vectorizer.py` - Main LLM-based vectorization framework
- `alive2_verifier.py` - Formal verification integration (used by vectorizer.py)

### 📁 analysis/
**Analysis and Comparison Tools** - Scripts for processing experimental results
- `analyze.py` - Experiment result analysis and failure pattern detection
- `compare_vectorization_results.py` - Compare results between different experiments
- `statistical_analysis.py` - Statistical analysis with confidence intervals
- `run_multiple_experiments.py` - Framework for running multiple experimental runs

### 📁 docs/
**Documentation and Analysis Results** - Reports and usage guides
- `statistical_analysis.md` - Current experimental results and statistical analysis
- `comparison_analysis.md` - Baseline vs. prompt engineering comparison
- `statistical_framework_summary.md` - Statistical framework overview
- `USAGE_GUIDE.md` - How to use the statistical analysis tools

### 📁 archive/
**Backup Files** - Historical versions and backups
- `tsvc_orig.c` - Original TSVC source backup (93KB)

## Quick Start

### Running Vectorization
```bash
cd tools/
python vectorizer.py --functions s1113,s115,s256 --api-key YOUR_API_KEY
```

### Analyzing Results
```bash
cd analysis/
python statistical_analysis.py --pattern "../path/to/results/*.json"
```

### Building TSVC
```bash
cd core/
make
```

## Key Features

- **Checksum Precision Fix**: The `common.c` file includes a critical fix for float precision issues in checksum validation
- **Formal Verification**: Integration with Alive2 for correctness proofs
- **Statistical Analysis**: Comprehensive statistical framework with confidence intervals
- **Modular Design**: Clean separation between core infrastructure, tools, and analysis

## Recent Changes

- **Fixed s1113 bug**: Modified `sum1d()` and `sum2d()` functions to use double precision accumulation
- **Organized structure**: Separated concerns into logical directories
- **Clean codebase**: Removed temporary files and improved organization