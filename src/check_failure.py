#!/usr/bin/env python3
"""
Script to simulate TSVC function execution and identify exact failure points.
Currently focused on s242 but designed to be reusable for other functions.
"""

import numpy as np
import sys
from typing import List, Tuple, Optional

# Configuration - matches TSVC settings
LEN_1D = 32000  # Real TSVC size
ITERATIONS = 1000000  # Real TSVC iterations

class TSVCArrays:
    """Simulate TSVC global arrays with proper initialization"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Initialize arrays as done in TSVC initialise_arrays"""
        # These initialization patterns match TSVC's initialise_arrays function
        self.a = np.zeros(LEN_1D, dtype=np.float32)
        self.b = np.zeros(LEN_1D, dtype=np.float32)
        self.c = np.zeros(LEN_1D, dtype=np.float32)
        self.d = np.zeros(LEN_1D, dtype=np.float32)
        self.e = np.zeros(LEN_1D, dtype=np.float32)
        
        # Standard TSVC initialization patterns
        for i in range(LEN_1D):
            self.a[i] = 1.0
            self.b[i] = 2.0
            self.c[i] = 3.0
            self.d[i] = 4.0
            self.e[i] = 5.0

def s242_original(arrays: TSVCArrays, s1: float = 1.0, s2: float = 2.0, iterations: int = ITERATIONS//5) -> float:
    """Original s242 implementation"""
    arrays.reset()
    
    for nl in range(iterations):
        for i in range(1, LEN_1D):
            arrays.a[i] = arrays.a[i-1] + s1 + s2 + arrays.b[i] + arrays.c[i] + arrays.d[i]
    
    return np.sum(arrays.a)

def s242_vectorized_simulation(arrays: TSVCArrays, s1: float = 1.0, s2: float = 2.0, iterations: int = ITERATIONS//5) -> float:
    """Simulate the vectorized s242 implementation from extracted_function_1.c"""
    arrays.reset()
    
    s1_plus_s2 = s1 + s2
    
    for nl in range(iterations):
        i = 1
        
        # Vectorized loop - process 8 elements at a time
        while i + 7 < LEN_1D:
            # Compute s1 + s2 + b[i] + c[i] + d[i] for 8 elements
            sums = np.zeros(8, dtype=np.float32)
            for j in range(8):
                sums[j] = s1_plus_s2 + arrays.b[i+j] + arrays.c[i+j] + arrays.d[i+j]
            
            # Apply the recurrence sequentially
            for j in range(8):
                arrays.a[i + j] = arrays.a[i + j - 1] + sums[j]
            
            i += 8
        
        # Handle remaining elements
        while i < LEN_1D:
            arrays.a[i] = arrays.a[i - 1] + s1_plus_s2 + arrays.b[i] + arrays.c[i] + arrays.d[i]
            i += 1
    
    return np.sum(arrays.a)

def compare_execution_step_by_step(verbose: bool = False) -> None:
    """Compare original vs vectorized execution step by step"""
    global LEN_1D
    print("=== S242 Failure Analysis ===")
    print(f"LEN_1D = {LEN_1D}")
    print(f"ITERATIONS = {ITERATIONS//5}")
    
    # Test with smaller problem size first
    original_len = LEN_1D
    LEN_1D = 16  # Smaller size for detailed analysis
    
    try:
        arrays_orig = TSVCArrays()
        arrays_vec = TSVCArrays()
        
        print(f"\nTesting with LEN_1D = {LEN_1D}")
        
        # Run original
        checksum_orig = s242_original(arrays_orig, iterations=1)  # Single iteration for analysis
        
        # Run vectorized
        checksum_vec = s242_vectorized_simulation(arrays_vec, iterations=1)
        
        print(f"Original checksum: {checksum_orig}")
        print(f"Vectorized checksum: {checksum_vec}")
        print(f"Difference: {abs(checksum_orig - checksum_vec)}")
        
        # Compare arrays element by element
        print("\nElement-by-element comparison:")
        print("Index\tOriginal\tVectorized\tDifference")
        print("-" * 50)
        
        first_mismatch = None
        for i in range(LEN_1D):
            diff = abs(arrays_orig.a[i] - arrays_vec.a[i])
            if diff > 1e-6 and first_mismatch is None:
                first_mismatch = i
            
            if verbose or diff > 1e-6:
                print(f"{i}\t{arrays_orig.a[i]:.6f}\t{arrays_vec.a[i]:.6f}\t{diff:.6f}")
        
        if first_mismatch is not None:
            print(f"\nFirst mismatch at index {first_mismatch}")
            print(f"Expected: {arrays_orig.a[first_mismatch]}")
            print(f"Got: {arrays_vec.a[first_mismatch]}")
            
            # Analyze the computation leading to this mismatch
            print(f"\nAnalyzing computation for a[{first_mismatch}]:")
            if first_mismatch > 0:
                s1_plus_s2 = 3.0  # 1.0 + 2.0
                expected_sum = s1_plus_s2 + arrays_orig.b[first_mismatch] + arrays_orig.c[first_mismatch] + arrays_orig.d[first_mismatch]
                print(f"Sum components: {s1_plus_s2} + {arrays_orig.b[first_mismatch]} + {arrays_orig.c[first_mismatch]} + {arrays_orig.d[first_mismatch]} = {expected_sum}")
                print(f"Previous a[{first_mismatch-1}]: orig={arrays_orig.a[first_mismatch-1]}, vec={arrays_vec.a[first_mismatch-1]}")
                print(f"Expected a[{first_mismatch}] = {arrays_orig.a[first_mismatch-1]} + {expected_sum} = {arrays_orig.a[first_mismatch-1] + expected_sum}")
        else:
            print("\nNo mismatches found!")
        
        # Test with full size but fewer iterations to avoid timeout
        print(f"\n=== Testing with full LEN_1D = {original_len}, limited iterations ===")
        LEN_1D = original_len
        
        arrays_orig = TSVCArrays()
        arrays_vec = TSVCArrays()
        
        test_iterations = 1000  # Much smaller for testing
        checksum_orig = s242_original(arrays_orig, iterations=test_iterations)
        checksum_vec = s242_vectorized_simulation(arrays_vec, iterations=test_iterations)
        
        print(f"Original checksum: {checksum_orig}")
        print(f"Vectorized checksum: {checksum_vec}")
        print(f"Difference: {abs(checksum_orig - checksum_vec)}")
        if checksum_orig != 0:
            print(f"Relative difference: {abs(checksum_orig - checksum_vec) / checksum_orig * 100:.6f}%")
        
        # Check if arrays are identical
        max_diff = np.max(np.abs(arrays_orig.a - arrays_vec.a))
        print(f"Maximum element difference: {max_diff}")
        
        if max_diff > 1e-6:
            # Find first significant difference
            diffs = np.abs(arrays_orig.a - arrays_vec.a)
            first_idx = np.where(diffs > 1e-6)[0]
            if len(first_idx) > 0:
                idx = first_idx[0]
                print(f"First significant difference at index {idx}")
                print(f"Expected: {arrays_orig.a[idx]}")
                print(f"Got: {arrays_vec.a[idx]}")
        
    finally:
        LEN_1D = original_len

def test_other_function(func_name: str, orig_func, vec_func, test_iterations: int = 1):
    """Generic function to test other TSVC functions"""
    print(f"=== {func_name} Analysis ===")
    
    arrays_orig = TSVCArrays()
    arrays_vec = TSVCArrays()
    
    checksum_orig = orig_func(arrays_orig, iterations=test_iterations)
    checksum_vec = vec_func(arrays_vec, iterations=test_iterations)
    
    print(f"Original checksum: {checksum_orig}")
    print(f"Vectorized checksum: {checksum_vec}")
    print(f"Difference: {abs(checksum_orig - checksum_vec)}")
    
    # Compare arrays element by element
    max_diff = np.max(np.abs(arrays_orig.a - arrays_vec.a))
    print(f"Maximum element difference: {max_diff}")
    
    if max_diff > 1e-6:
        diffs = np.abs(arrays_orig.a - arrays_vec.a)
        first_idx = np.where(diffs > 1e-6)[0]
        if len(first_idx) > 0:
            idx = first_idx[0]
            print(f"First mismatch at index {idx}")
            print(f"Expected: {arrays_orig.a[idx]}")
            print(f"Got: {arrays_vec.a[idx]}")
    
    return max_diff < 1e-6

if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    compare_execution_step_by_step(verbose=verbose)