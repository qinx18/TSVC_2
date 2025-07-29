import subprocess
import os
import tempfile
import re
from typing import Dict, Tuple, Optional

class Alive2Verifier:
    """
    Integrates Alive2 formal verification to validate vectorized transformations.
    
    This class provides methods to:
    1. Compile C code to LLVM IR
    2. Run Alive2 to verify transformation correctness
    3. Parse Alive2 output for verification results
    """
    
    def __init__(self, alive2_path: str = None):
        """
        Initialize the Alive2 verifier.
        
        Args:
            alive2_path: Path to alive-tv executable. If None, tries common locations.
        """
        # Try different possible locations for alive-tv
        possible_paths = [
            alive2_path,
            "alive-tv",
            "/home/qinxiao/workspace/alive2/build/alive-tv",
            "/usr/local/bin/alive-tv",
            "/usr/bin/alive-tv"
        ]
        
        self.alive2_path = None
        for path in possible_paths:
            if path and self._check_executable_exists(path):
                self.alive2_path = path
                break
        
        if not self.alive2_path:
            raise RuntimeError("alive-tv executable not found. Please install Alive2 with LLVM support.")
        
        self.clang_path = "clang"
        
        # Verify tools are available
        self._verify_tools()
    
    def _check_executable_exists(self, path: str) -> bool:
        """Check if an executable exists and is runnable."""
        try:
            result = subprocess.run([path, "--help"], capture_output=True, 
                                  text=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _verify_tools(self):
        """Verify that required tools (clang, alive-tv) are available."""
        # Check clang
        try:
            result = subprocess.run([self.clang_path, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"clang not found or not working")
        except FileNotFoundError:
            raise RuntimeError(f"clang not found. Please install LLVM/Clang.")
        
        # Check alive-tv
        try:
            result = subprocess.run([self.alive2_path, "--help"], 
                                  capture_output=True, text=True)
            if result.returncode != 0 and "USAGE:" not in result.stderr:
                raise RuntimeError(f"alive-tv not found or not working")
        except FileNotFoundError:
            raise RuntimeError(f"alive-tv not found at {self.alive2_path}. "
                             f"Please install Alive2 or provide correct path.")
    
    def compile_to_llvm_ir(self, c_code: str, func_name: str, 
                          include_dirs: list = None) -> Tuple[bool, str, str]:
        """
        Compile C code to LLVM IR.
        
        Args:
            c_code: C source code
            func_name: Name of the function to extract
            include_dirs: List of include directories
            
        Returns:
            Tuple of (success, ir_code, error_message)
        """
        include_dirs = include_dirs or []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_code)
            c_file = f.name
        
        try:
            # Compile to LLVM IR
            ir_file = c_file.replace('.c', '.ll')
            
            compile_cmd = [
                self.clang_path,
                '-S',                    # Generate assembly (LLVM IR with -emit-llvm)
                '-emit-llvm',           # Emit LLVM IR instead of machine code
                '-O0',                  # No optimization to preserve structure
                '-Xclang', '-disable-O0-optnone',  # Allow optimizations in Alive2
                '-std=c99',
                '-mavx2',               # Enable AVX2 for intrinsics
                '-mfma',                # Enable FMA
            ]
            
            # Add include directories
            for inc_dir in include_dirs:
                compile_cmd.extend(['-I', inc_dir])
            
            compile_cmd.extend(['-o', ir_file, c_file])
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, "", f"Compilation failed: {result.stderr}"
            
            # Read the IR file
            with open(ir_file, 'r') as f:
                full_ir = f.read()
            
            # Extract only the function we're interested in
            ir_code = self._extract_function_from_ir(full_ir, func_name)
            
            return True, ir_code, ""
            
        finally:
            # Cleanup
            if os.path.exists(c_file):
                os.remove(c_file)
            if os.path.exists(ir_file):
                os.remove(ir_file)
    
    def _extract_function_from_ir(self, full_ir: str, func_name: str) -> str:
        """Extract a specific function from LLVM IR."""
        lines = full_ir.split('\n')
        
        # Find the function definition
        func_start = None
        brace_count = 0
        in_function = False
        extracted_lines = []
        
        # First, collect necessary declarations and metadata
        for line in lines:
            if line.strip().startswith('target ') or \
               line.strip().startswith('declare ') or \
               line.strip().startswith('!') or \
               line.strip().startswith('attributes #'):
                extracted_lines.append(line)
        
        extracted_lines.append("")  # Add blank line
        
        # Now extract the function
        for i, line in enumerate(lines):
            if f"define" in line and f"@{func_name}(" in line:
                func_start = i
                in_function = True
            
            if in_function:
                extracted_lines.append(line)
                
                # Count braces to find end of function
                brace_count += line.count('{')
                brace_count -= line.count('}')
                
                if brace_count == 0 and func_start is not None and i > func_start:
                    break
        
        return '\n'.join(extracted_lines)
    
    def verify_transformation(self, original_ir: str, vectorized_ir: str,
                            timeout: int = 30) -> Dict[str, any]:
        """
        Use Alive2 to verify that vectorized code is equivalent to original.
        
        Args:
            original_ir: LLVM IR of original function
            vectorized_ir: LLVM IR of vectorized function
            timeout: Timeout in seconds for Alive2
            
        Returns:
            Dictionary with verification results
        """
        # Save IR files
        with tempfile.NamedTemporaryFile(mode='w', suffix='_src.ll', delete=False) as f:
            f.write(original_ir)
            src_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_tgt.ll', delete=False) as f:
            f.write(vectorized_ir)
            tgt_file = f.name
        
        try:
            # Run Alive2
            cmd = [
                self.alive2_path,
                src_file,
                tgt_file,
                '--disable-undef-input',     # Disable undef inputs for cleaner results
                '--disable-poison-input',    # Disable poison inputs
                '--smt-to', str(timeout * 1000)  # Timeout in milliseconds
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=timeout + 5)
            
            # Parse the output
            return self._parse_alive2_output(result.stdout, result.stderr)
            
        except subprocess.TimeoutExpired:
            return {
                'verified': False,
                'timeout': True,
                'error': 'Verification timed out',
                'counterexample': None
            }
        finally:
            # Cleanup
            if os.path.exists(src_file):
                os.remove(src_file)
            if os.path.exists(tgt_file):
                os.remove(tgt_file)
    
    def _parse_alive2_output(self, stdout: str, stderr: str) -> Dict[str, any]:
        """Parse Alive2 output to determine verification result."""
        
        # Check for successful verification
        if "Transformation seems to be correct!" in stdout:
            return {
                'verified': True,
                'timeout': False,
                'error': None,
                'counterexample': None,
                'output': stdout
            }
        
        # Check for counterexample
        if "ERROR: Target is more poisonous than source" in stdout or \
           "ERROR:" in stdout:
            # Extract counterexample
            counterexample = self._extract_counterexample(stdout)
            return {
                'verified': False,
                'timeout': False,
                'error': 'Found counterexample',
                'counterexample': counterexample,
                'output': stdout
            }
        
        # Check for other errors
        if stderr:
            return {
                'verified': False,
                'timeout': False,
                'error': f'Alive2 error: {stderr}',
                'counterexample': None,
                'output': stdout
            }
        
        # Unknown result
        return {
            'verified': False,
            'timeout': False,
            'error': 'Unknown verification result',
            'counterexample': None,
            'output': stdout
        }
    
    def _extract_counterexample(self, output: str) -> Optional[str]:
        """Extract counterexample from Alive2 output."""
        lines = output.split('\n')
        
        # Look for counterexample section
        counter_start = None
        for i, line in enumerate(lines):
            if "ERROR:" in line:
                counter_start = i
                break
        
        if counter_start is None:
            return None
        
        # Extract lines after ERROR until next section or end
        counter_lines = []
        for i in range(counter_start, min(counter_start + 20, len(lines))):
            counter_lines.append(lines[i])
        
        return '\n'.join(counter_lines)
    
    def create_verification_wrapper(self, original_c: str, vectorized_c: str,
                                  func_name: str, include_dirs: list = None) -> Dict[str, any]:
        """
        High-level method to verify a vectorization transformation.
        
        Args:
            original_c: Original C code
            vectorized_c: Vectorized C code  
            func_name: Function name to verify
            include_dirs: Include directories for compilation
            
        Returns:
            Verification results dictionary
        """
        # Compile original to IR
        success, orig_ir, error = self.compile_to_llvm_ir(
            original_c, func_name, include_dirs)
        
        if not success:
            return {
                'verified': False,
                'error': f'Failed to compile original: {error}',
                'stage': 'compilation_original'
            }
        
        # Compile vectorized to IR
        success, vec_ir, error = self.compile_to_llvm_ir(
            vectorized_c, func_name + "_vectorized", include_dirs)
        
        if not success:
            return {
                'verified': False,
                'error': f'Failed to compile vectorized: {error}',
                'stage': 'compilation_vectorized'
            }
        
        # Run verification
        result = self.verify_transformation(orig_ir, vec_ir)
        result['stage'] = 'verification'
        
        return result


class ChecksumValidator:
    """
    Implements checksum-based validation for vectorized code.
    
    This provides a secondary validation mechanism that:
    1. Computes checksums for array outputs
    2. Compares checksums between original and vectorized versions
    3. Provides detailed mismatch information
    """
    
    def __init__(self):
        self.checksum_tolerance = 1e-6  # Tolerance for floating-point comparison
    
    def generate_checksum_test(self, func_name: str, arrays_used: list) -> str:
        """
        Generate C code to compute checksums for validation.
        
        Args:
            func_name: Name of the function
            arrays_used: List of arrays used by the function
            
        Returns:
            C code for checksum computation
        """
        checksum_code = f"""
// Checksum validation for {func_name}
#include <math.h>
#include <stdio.h>

typedef struct {{
    double array_checksums[10];  // Checksums for each array
    int num_arrays;
    const char* array_names[10];
}} checksum_result_t;

checksum_result_t compute_checksums_{func_name}() {{
    checksum_result_t result = {{0}};
    result.num_arrays = 0;
    
"""
        
        # Add checksum computation for each array
        for array in arrays_used:
            if array in ['a', 'b', 'c', 'd', 'e']:
                # 1D array
                checksum_code += f"""    // Checksum for array {array}
    {{
        double sum = 0.0;
        for (int i = 0; i < LEN_1D; i++) {{
            sum += {array}[i];
        }}
        result.array_checksums[result.num_arrays] = sum;
        result.array_names[result.num_arrays] = "{array}";
        result.num_arrays++;
    }}
    
"""
            elif array in ['aa', 'bb', 'cc']:
                # 2D array
                checksum_code += f"""    // Checksum for array {array}
    {{
        double sum = 0.0;
        for (int i = 0; i < LEN_2D; i++) {{
            for (int j = 0; j < LEN_2D; j++) {{
                sum += {array}[i][j];
            }}
        }}
        result.array_checksums[result.num_arrays] = sum;
        result.array_names[result.num_arrays] = "{array}";
        result.num_arrays++;
    }}
    
"""
        
        checksum_code += """    return result;
}

int validate_checksums(checksum_result_t orig, checksum_result_t vec, double tolerance) {
    if (orig.num_arrays != vec.num_arrays) {
        printf("ERROR: Different number of arrays (%d vs %d)\\n", 
               orig.num_arrays, vec.num_arrays);
        return 0;
    }
    
    int all_match = 1;
    for (int i = 0; i < orig.num_arrays; i++) {
        double diff = fabs(orig.array_checksums[i] - vec.array_checksums[i]);
        if (diff > tolerance) {
            printf("CHECKSUM MISMATCH for %s: %.10f vs %.10f (diff: %.2e)\\n",
                   orig.array_names[i], orig.array_checksums[i], 
                   vec.array_checksums[i], diff);
            all_match = 0;
        }
    }
    
    return all_match;
}
"""
        
        return checksum_code