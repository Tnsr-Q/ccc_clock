
# Bridge-Null Extended Analysis Suite

This document describes the extended analysis suite for the bridge-null problem, implementing three additional experiments while preserving all original functionality.

## Overview

The `experiments_bridge_null.py` script extends the original `bridge_null.py` with three new experiments:

1. **Spectral-Norm Cross-Check**: Compares Frobenius norm vs spectral norm (ord=2) results
2. **Exact-Null Panel**: Tests with identical copies to demonstrate zero residual floor
3. **Weight Tuning**: Optimizes weights to minimize residual floor using projected gradient descent

## New Functions

### 1. Spectral-Norm Functions

- `cycle_residual_spec(edges, R, eps)`: Computes cycle residual using spectral norm (ord=2)
- `bridge_null_spectral(edges, ...)`: Complete bridge-null analysis using spectral norm

### 2. Exact-Null Functions

- `create_identical_copies(edges, m)`: Creates m identical copies from aggregate edge
- Uses existing `aggregate_edge()` function from original code

### 3. Weight Optimization Functions

- `optimize_weights(edges, ...)`: Projected gradient descent on simplex constraint
- Minimizes residual floor by optimizing edge weights

### 4. Visualization Functions

- `plot_norm_comparison()`: Frobenius vs spectral norm comparison
- `plot_exact_null_comparison()`: Heterogeneous vs identical edges comparison  
- `plot_weight_optimization()`: Weight optimization results

## Usage

### Run Complete Analysis Suite

```bash
python experiments_bridge_null.py
```

This runs all three experiments sequentially and saves plots to `figures/` directory.

### Import and Use Individual Functions

```python
from experiments_bridge_null import cycle_residual_spec, optimize_weights, create_identical_copies

# Use spectral norm instead of Frobenius
residual_spec = cycle_residual_spec(edges, R=1.0, eps=1e-3)

# Create identical copies for exact null test
identical_edges = create_identical_copies(original_edges, m=4)

# Optimize weights
optimal_weights, min_residual = optimize_weights(edges)
```

## Key Results

The analysis demonstrates:

1. **Norm Relationship**: Spectral norm typically gives different R* values but similar convergence behavior
2. **Exact Null**: Identical copies achieve near-zero residual floors (limited by numerical precision)
3. **Weight Optimization**: Non-uniform weights can significantly reduce residual floors

## Output Files

- `figures/norm_comparison.png`: Frobenius vs spectral norm landscapes
- `figures/exact_null_comparison.png`: Heterogeneous vs identical edges comparison
- `figures/weight_optimization.png`: Weight optimization results

## Technical Details

### Spectral Norm Implementation
- Uses `np.linalg.norm(U - I, ord=2)` instead of `ord='fro'`
- Preserves all other algorithmic details from original

### Weight Optimization
- Projected gradient descent with simplex constraints
- Finite difference gradients
- Adaptive step size: `α = α₀ / (1 + 0.001 × iteration)`

### Exact Null Panel
- Creates aggregate edge: `N_agg = Σᵢ wᵢNᵢ`, `D_agg = Σᵢ wᵢDᵢ`
- Uses same number of edges as original heterogeneous case
- Demonstrates theoretical zero commutator limit

## Dependencies

- numpy
- matplotlib
- scipy (optional, for matrix exponential)
- Original bridge_null.py module

## Reproducibility

- Fixed random seed (42) for consistent results
- All parameters documented in function signatures
- Console output includes key metrics and convergence information
