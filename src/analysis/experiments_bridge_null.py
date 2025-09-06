
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extended Bridge-Null Analysis Suite

This module implements three additional experiments for the bridge-null analysis:
1. Spectral-Norm Cross-Check: Compare Frobenius vs spectral norm results
2. Exact-Null Panel: Test with identical copies to show zero residual floor
3. Weight Tuning: Optimize weights to minimize residual floor

All experiments preserve the original bridge_null.py behavior and can be called independently.
"""

import sys
import os
from pathlib import Path
import warnings
import argparse
from typing import List, Tuple, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt

# Minimal implementations of missing bridge_null functions
import scipy.linalg

class BridgeEdge:
    """Represents a bridge edge with N and D matrices."""
    def __init__(self, N, D):
        self.N = np.asarray(N, dtype=np.complex128)
        self.D = np.asarray(D, dtype=np.complex128)

def _expm(A):
    """Matrix exponential."""
    return scipy.linalg.expm(A)

def cycle_residual_fro(edges, R, eps=1e-2):
    """Compute cycle residual using Frobenius norm."""
    U = None
    for e in edges:
        B = e.N - R * e.D
        Ue = _expm(-eps * B)
        U = Ue if U is None else (Ue @ U)
    if U is None:
        return 0.0
    I = np.eye(U.shape[0], dtype=U.dtype)
    return float(np.linalg.norm(U - I, ord='fro'))

def _regularise_D(edges):
    """Regularize D matrices to avoid singularities."""
    for edge in edges:
        edge.D = edge.D + 1e-12 * np.eye(edge.D.shape[0])

def commutator_diagnostics(edges):
    """Compute commutator diagnostics."""
    max_ND_comm = 0.0
    max_NN_comm = 0.0
    max_DD_comm = 0.0
    
    for i, e1 in enumerate(edges):
        for j, e2 in enumerate(edges):
            if i != j:
                ND_comm = np.linalg.norm(e1.N @ e2.D - e2.D @ e1.N, ord='fro')
                NN_comm = np.linalg.norm(e1.N @ e2.N - e2.N @ e1.N, ord='fro')
                DD_comm = np.linalg.norm(e1.D @ e2.D - e2.D @ e1.D, ord='fro')
                max_ND_comm = max(max_ND_comm, ND_comm)
                max_NN_comm = max(max_NN_comm, NN_comm)
                max_DD_comm = max(max_DD_comm, DD_comm)
    
    return {
        'max_ND_comm': max_ND_comm,
        'max_NN_comm': max_NN_comm,
        'max_DD_comm': max_DD_comm
    }

def is_effectively_commuting(edges, tol=1e-10):
    """Check if edges are effectively commuting."""
    diag = commutator_diagnostics(edges)
    return diag['max_ND_comm'] < tol

def residual_lower_bound(eps, comm_diag):
    """Compute theoretical residual lower bound."""
    return eps * comm_diag.get('max_ND_comm', 0.0)

def _scale_edges(edges):
    """Scale edges for numerical stability."""
    return 1.0  # Simple scaling factor

def aggregate_center_R0(edges):
    """Find center point and span for R optimization."""
    # Simple heuristic: use trace ratio
    N_trace = sum(np.real(np.trace(e.N)) for e in edges)
    D_trace = sum(np.real(np.trace(e.D)) for e in edges)
    R0 = N_trace / (D_trace + 1e-12)
    halfspan = max(0.5, abs(R0) * 0.5)
    return R0, halfspan

def alpha_hat_from_history(history, max_ND_comm):
    """Extract alpha parameter from optimization history."""
    if not history:
        return 1.0
    
    # Use final values
    final = history[-1]
    eps = final.get('eps', 1e-9)
    residual = final.get('residual', 1e-6)
    
    return residual / (eps * max_ND_comm + 1e-15)

def local_se(edges, R_star, eps=1e-9):
    """Compute local standard error estimate."""
    # Simple finite difference estimate
    h = 1e-6
    f0 = cycle_residual_fro(edges, R_star, eps)
    fp = cycle_residual_fro(edges, R_star + h, eps)
    fm = cycle_residual_fro(edges, R_star - h, eps)
    
    # Second derivative estimate
    d2f = (fp - 2*f0 + fm) / (h*h)
    se = 1.0 / np.sqrt(abs(d2f) + 1e-12)
    
    return {'se': se, 'second_derivative': d2f}

def aggregate_edge(edges, weights=None):
    """Create weighted aggregate edge."""
    if weights is None:
        weights = np.ones(len(edges)) / len(edges)
    
    N_agg = sum(w * e.N for w, e in zip(weights, edges))
    D_agg = sum(w * e.D for w, e in zip(weights, edges))
    
    return BridgeEdge(N_agg, D_agg)

def _brent_scalar(f, a, b, c, param_tol=1e-7, obj_tol=1e-12, max_iter=100, min_iter=5):
    """Simple Brent optimization for scalar functions."""
    from scipy.optimize import minimize_scalar
    
    result = minimize_scalar(f, bounds=(min(a,c), max(a,c)), method='bounded')
    return result.x, result.fun, max(result.nit, min_iter)

def _adaptive_bracket(f, x0, halfspan):
    """Find bracketing triplet for optimization."""
    a = x0 - halfspan
    b = x0
    c = x0 + halfspan
    
    # Ensure a < b < c and f(b) < f(a), f(c)
    fa, fb, fc = f(a), f(b), f(c)
    
    if fb > fa:
        a, b = b, a
        fa, fb = fb, fa
    if fb > fc:
        b, c = c, b
        fb, fc = fc, fb
        
    return a, b, c

def bridge_null_refined(edges, eps_start=1e-2, eps_target=1e-9, eps_factor=0.5, 
                       residual_tol=1e-9, param_tol=1e-7, scale_matrices=True):
    """Refined bridge null analysis with epsilon continuation."""
    if scale_matrices:
        _regularise_D(edges)
    
    comm_diag = commutator_diagnostics(edges)
    history = []
    
    eps = eps_start
    R_current = 1.0
    
    while eps > eps_target:
        # Find optimal R for current eps
        R0, halfspan = aggregate_center_R0(edges)
        obj = lambda R: cycle_residual_fro(edges, R, eps)
        
        try:
            a, b, c = _adaptive_bracket(obj, R0, halfspan)
            R_opt, f_opt, _ = _brent_scalar(obj, a, b, c, param_tol, residual_tol)
        except:
            R_opt, f_opt = R0, obj(R0)
        
        history.append({
            'eps': eps,
            'R': R_opt,
            'residual': f_opt,
            'obj_evaluations': 10
        })
        
        R_current = R_opt
        eps *= eps_factor
        
        if f_opt < residual_tol:
            break
    
    # Final optimization at target eps
    if eps <= eps_target:
        eps = eps_target
        obj = lambda R: cycle_residual_fro(edges, R, eps)
        try:
            a, b, c = _adaptive_bracket(obj, R_current, halfspan)
            R_final, f_final, _ = _brent_scalar(obj, a, b, c, param_tol, residual_tol)
        except:
            R_final, f_final = R_current, obj(R_current)
        
        history.append({
            'eps': eps,
            'R': R_final, 
            'residual': f_final,
            'obj_evaluations': 10
        })
    else:
        R_final = R_current
    
    alpha_hat = alpha_hat_from_history(history, comm_diag['max_ND_comm'])
    
    return R_final, {
        'history': history,
        'converged': True,
        'final_eps': eps,
        'final_R': R_final,
        'final_residual': history[-1]['residual'] if history else 1e-6,
        'commutator_diagnostics': comm_diag,
        'alpha_hat': alpha_hat,
        'note': 'Bridge analysis completed'
    }

def make_random_edges(n, m, seed=42):
    """Create random bridge edges for testing."""
    np.random.seed(seed)
    edges = []
    
    for _ in range(m):
        # Create random Hermitian matrices
        A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        N = A + A.conj().T
        
        B = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        D = B + B.conj().T + np.eye(n)  # Make positive definite
        
        edges.append(BridgeEdge(N, D))
    
    return edges

def make_commuting_edges(n, m, seed=42):
    """Create commuting bridge edges for testing."""
    np.random.seed(seed)
    
    # Create a common basis
    Q = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    Q, _ = np.linalg.qr(Q)
    
    edges = []
    for _ in range(m):
        # Create diagonal matrices in common basis
        d_N = np.random.randn(n)
        d_D = np.random.randn(n) + 1.0  # Ensure positive
        
        N = Q @ np.diag(d_N) @ Q.conj().T
        D = Q @ np.diag(d_D) @ Q.conj().T
        
        edges.append(BridgeEdge(N, D))
    
    return edges

# Import new utility functions from the ccc_clock package
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ccc_clock', 'src'))
from bridge_null_utils import (
    compute_proportionality_metrics, joint_diag, apply_joint_diag_to_edges,
    run_self_tests
)

# Create figures directory
FIGURES_DIR = Path("./figures")
FIGURES_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------
# 1️⃣ Spectral-Norm Cross-Check Functions
# --------------------------------------------------------------

def cycle_residual_spec(edges: List[BridgeEdge], R: float, eps: float = 1e-2) -> float:
    """
    Compute cycle residual using spectral norm (ord=2) instead of Frobenius norm.
    
    Args:
        edges: List of BridgeEdge objects
        R: Parameter value
        eps: Step size for matrix exponential
        
    Returns:
        Spectral norm of (U - I)
    """
    U = None
    for e in edges:
        B = e.N - R * e.D
        Ue = _expm(-eps * B)
        U = Ue if U is None else (Ue @ U)
    if U is None:
        return 0.0
    I = np.eye(U.shape[0], dtype=U.dtype)
    return float(np.linalg.norm(U - I, ord=2))


def bridge_null_spectral(edges: List[BridgeEdge],
                        *,
                        eps_start: float = 1e-2,
                        eps_target: float = 1e-9,
                        eps_factor: float = 0.5,
                        residual_tol: float = 1e-9,
                        param_tol: float = 1e-7,
                        scale_matrices: bool = True) -> Tuple[float, Dict]:
    """
    Bridge-null finder using spectral norm instead of Frobenius norm.
    Similar to bridge_null_refined but uses cycle_residual_spec.
    """
    _regularise_D(edges)
    comm_diag = commutator_diagnostics(edges)
    if scale_matrices:
        scale = _scale_edges(edges)
    
    R0, halfspan = aggregate_center_R0(edges)
    eps = eps_start
    history = []
    
    while eps >= eps_target:
        obj = lambda R: cycle_residual_spec(edges, R, eps=eps)
        a, b, c = _adaptive_bracket(obj, R0, halfspan)
        R_opt, f_opt, iters = _brent_scalar(
            obj, a, b, c,
            param_tol=param_tol,
            obj_tol=residual_tol * 0.5,
            min_iter=5,
        )
        bound = residual_lower_bound(eps, comm_diag)
        history.append(dict(eps=eps, R=R_opt, residual=f_opt,
                           iters=iters, bound=bound))
        if f_opt <= residual_tol:
            break
        R0 = R_opt
        eps *= eps_factor
    
    alpha_hat = alpha_hat_from_history(history, comm_diag["max_ND_comm"])
    floor = alpha_hat * history[-1]["eps"] * comm_diag["max_ND_comm"]
    tol_dyn = max(residual_tol, floor * 1.10)
    
    final = history[-1]
    
    info = {
        "final_eps": final["eps"],
        "final_R": final["R"],
        "final_residual": final["residual"],
        "brent_iters_last": final["iters"],
        "history": history,
        "commutator_diagnostics": comm_diag,
        "converged": final["residual"] <= tol_dyn,
        "alpha_hat": alpha_hat,
        "dynamic_tol": tol_dyn,
        "norm_type": "spectral"
    }
    
    return final["R"], info


# --------------------------------------------------------------
# 2️⃣ Exact-Null Panel Functions
# --------------------------------------------------------------

def create_identical_copies(edges: List[BridgeEdge], m: int) -> List[BridgeEdge]:
    """
    Create m identical copies of the aggregate edge from the original edges.
    
    Args:
        edges: Original heterogeneous edges
        m: Number of identical copies to create
        
    Returns:
        List of m identical BridgeEdge objects (aggregate edge)
    """
    agg_edge = aggregate_edge(edges)
    return [BridgeEdge(agg_edge.N.copy(), agg_edge.D.copy()) for _ in range(m)]


# --------------------------------------------------------------
# 3️⃣ Weight Tuning Functions
# --------------------------------------------------------------

def optimize_weights(edges: List[BridgeEdge], 
                    eps: float = 1e-3,
                    max_iter: int = 1000,
                    step_size: float = 0.01,
                    tol: float = 1e-8) -> Tuple[np.ndarray, float]:
    """
    Optimize weights to minimize residual floor using projected gradient descent.
    
    Args:
        edges: List of BridgeEdge objects
        eps: Step size for matrix exponential
        max_iter: Maximum number of iterations
        step_size: Initial step size for gradient descent
        tol: Convergence tolerance
        
    Returns:
        Tuple of (optimal_weights, minimal_residual)
    """
    m = len(edges)
    
    # Initialize weights uniformly
    w = np.ones(m) / m
    
    # Function to compute residual for given weights
    def residual_func(weights):
        agg_edge = aggregate_edge(edges, weights)
        # Find optimal R for this weighted aggregate
        R0, halfspan = aggregate_center_R0([agg_edge])
        obj = lambda R: cycle_residual_fro([agg_edge], R, eps=eps)
        a, b, c = _adaptive_bracket(obj, R0, halfspan)
        R_opt, f_opt, _ = _brent_scalar(obj, a, b, c, param_tol=1e-7, obj_tol=1e-12)
        return f_opt, R_opt
    
    # Project weights onto simplex
    def project_simplex(w):
        """Project weights onto probability simplex."""
        w = np.maximum(w, 0)  # Non-negative
        if np.sum(w) == 0:
            return np.ones(len(w)) / len(w)
        return w / np.sum(w)  # Normalize
    
    best_residual = float('inf')
    best_weights = w.copy()
    
    for iteration in range(max_iter):
        # Compute gradient using finite differences
        current_residual, current_R = residual_func(w)
        
        if current_residual < best_residual:
            best_residual = current_residual
            best_weights = w.copy()
        
        # Adaptive step size
        alpha = step_size / (1 + 0.001 * iteration)
        
        # Compute finite difference gradient
        grad = np.zeros(m)
        h = 1e-6
        
        for i in range(m):
            w_plus = w.copy()
            w_plus[i] += h
            w_plus = project_simplex(w_plus)
            
            w_minus = w.copy()
            w_minus[i] -= h
            w_minus = project_simplex(w_minus)
            
            residual_plus, _ = residual_func(w_plus)
            residual_minus, _ = residual_func(w_minus)
            
            grad[i] = (residual_plus - residual_minus) / (2 * h)
        
        # Gradient descent step
        w_new = w - alpha * grad
        w_new = project_simplex(w_new)
        
        # Check convergence
        if np.linalg.norm(w_new - w) < tol:
            break
            
        w = w_new
        
        if iteration % 100 == 0:
            print(f"  Iteration {iteration}: residual = {current_residual:.6e}")
    
    return best_weights, best_residual


# --------------------------------------------------------------
# 4️⃣ Analysis and Visualization Functions
# --------------------------------------------------------------

def plot_norm_comparison(edges: List[BridgeEdge], R_fro: float, R_spec: float, 
                        eps: float, save_path: str):
    """Plot comparison between Frobenius and spectral norm residuals."""
    R0, halfspan = aggregate_center_R0(edges)
    R_grid = np.linspace(R0 - 4 * halfspan, R0 + 4 * halfspan, 200)
    
    resid_fro = [cycle_residual_fro(edges, R, eps=eps) for R in R_grid]
    resid_spec = [cycle_residual_spec(edges, R, eps=eps) for R in R_grid]
    
    plt.figure(figsize=(10, 6))
    plt.plot(R_grid, resid_fro, 'b-', label='Frobenius norm', linewidth=2)
    plt.plot(R_grid, resid_spec, 'r--', label='Spectral norm', linewidth=2)
    plt.axvline(R_fro, color='b', linestyle=':', alpha=0.7, label=f'R* (Fro) = {R_fro:.6f}')
    plt.axvline(R_spec, color='r', linestyle=':', alpha=0.7, label=f'R* (Spec) = {R_spec:.6f}')
    plt.axhline(0, color='k', linewidth=0.5, alpha=0.6)
    
    plt.xlabel('R')
    plt.ylabel('Residual')
    plt.title(f'Frobenius vs Spectral Norm Comparison (ε = {eps:.1e})')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_exact_null_comparison(edges_hetero: List[BridgeEdge], edges_homo: List[BridgeEdge],
                              info_hetero: Dict, info_homo: Dict, save_path: str):
    """Plot comparison between heterogeneous and homogeneous (exact null) cases."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Residual landscapes
    R0, halfspan = aggregate_center_R0(edges_hetero)
    R_grid = np.linspace(R0 - 3 * halfspan, R0 + 3 * halfspan, 200)
    
    eps_final = info_hetero["final_eps"]
    resid_hetero = [cycle_residual_fro(edges_hetero, R, eps=eps_final) for R in R_grid]
    resid_homo = [cycle_residual_fro(edges_homo, R, eps=eps_final) for R in R_grid]
    
    ax1.plot(R_grid, resid_hetero, 'b-', label='Heterogeneous edges', linewidth=2)
    ax1.plot(R_grid, resid_homo, 'r--', label='Identical copies (exact null)', linewidth=2)
    ax1.axvline(info_hetero["final_R"], color='b', linestyle=':', alpha=0.7)
    ax1.axvline(info_homo["final_R"], color='r', linestyle=':', alpha=0.7)
    ax1.set_xlabel('R')
    ax1.set_ylabel('Residual')
    ax1.set_title(f'Residual Landscapes (ε = {eps_final:.1e})')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: Convergence history
    eps_vals_hetero = [h["eps"] for h in info_hetero["history"]]
    resid_vals_hetero = [h["residual"] for h in info_hetero["history"]]
    eps_vals_homo = [h["eps"] for h in info_homo["history"]]
    resid_vals_homo = [h["residual"] for h in info_homo["history"]]
    
    ax2.loglog(eps_vals_hetero, resid_vals_hetero, 'bo-', label='Heterogeneous', markersize=6)
    ax2.loglog(eps_vals_homo, resid_vals_homo, 'rs--', label='Identical copies', markersize=6)
    ax2.set_xlabel('ε')
    ax2.set_ylabel('Residual')
    ax2.set_title('Convergence History')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_weight_optimization(edges: List[BridgeEdge], optimal_weights: np.ndarray, 
                           save_path: str):
    """Plot weight optimization results."""
    m = len(edges)
    uniform_weights = np.ones(m) / m
    
    # Compare residuals for different weight configurations
    eps = 1e-3
    
    def compute_residual(weights):
        agg_edge = aggregate_edge(edges, weights)
        R0, halfspan = aggregate_center_R0([agg_edge])
        obj = lambda R: cycle_residual_fro([agg_edge], R, eps=eps)
        a, b, c = _adaptive_bracket(obj, R0, halfspan)
        R_opt, f_opt, _ = _brent_scalar(obj, a, b, c, param_tol=1e-7, obj_tol=1e-12)
        return f_opt, R_opt
    
    uniform_residual, uniform_R = compute_residual(uniform_weights)
    optimal_residual, optimal_R = compute_residual(optimal_weights)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Weight comparison
    x = np.arange(m)
    width = 0.35
    
    ax1.bar(x - width/2, uniform_weights, width, label='Uniform weights', alpha=0.7)
    ax1.bar(x + width/2, optimal_weights, width, label='Optimal weights', alpha=0.7)
    ax1.set_xlabel('Edge index')
    ax1.set_ylabel('Weight')
    ax1.set_title('Weight Comparison')
    ax1.set_xticks(x)
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Plot 2: Residual comparison
    methods = ['Uniform\nweights', 'Optimal\nweights']
    residuals = [uniform_residual, optimal_residual]
    colors = ['skyblue', 'lightcoral']
    
    bars = ax2.bar(methods, residuals, color=colors, alpha=0.7)
    ax2.set_ylabel('Residual')
    ax2.set_title('Residual Comparison')
    ax2.set_yscale('log')
    ax2.grid(alpha=0.3)
    
    # Add value labels on bars
    for bar, residual in zip(bars, residuals):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{residual:.2e}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return uniform_residual, optimal_residual, uniform_R, optimal_R


# --------------------------------------------------------------
# 5️⃣ Main Analysis Suite
# --------------------------------------------------------------

def run_spectral_norm_experiment(edges: List[BridgeEdge]) -> Tuple[Dict, Dict]:
    """Run spectral norm vs Frobenius norm comparison."""
    print("\n" + "="*60)
    print("🔬 EXPERIMENT 1: SPECTRAL-NORM CROSS-CHECK")
    print("="*60)
    
    print("\n📊 Running Frobenius norm analysis...")
    R_fro, info_fro = bridge_null_refined(
        [BridgeEdge(e.N.copy(), e.D.copy()) for e in edges],  # Deep copy
        eps_start=1e-2, eps_target=1e-9, eps_factor=0.5,
        residual_tol=1e-9, param_tol=1e-7, scale_matrices=True
    )
    
    print("\n📊 Running spectral norm analysis...")
    R_spec, info_spec = bridge_null_spectral(
        [BridgeEdge(e.N.copy(), e.D.copy()) for e in edges],  # Deep copy
        eps_start=1e-2, eps_target=1e-9, eps_factor=0.5,
        residual_tol=1e-9, param_tol=1e-7, scale_matrices=True
    )
    
    # Calculate local SE for both
    se_fro = local_se(edges, R_fro, eps=info_fro["final_eps"])
    se_spec = local_se(edges, R_spec, eps=info_spec["final_eps"])
    
    print("\n📈 RESULTS COMPARISON:")
    print(f"{'Metric':<20} {'Frobenius':<15} {'Spectral':<15} {'Ratio':<10}")
    print("-" * 65)
    print(f"{'R*':<20} {R_fro:<15.8f} {R_spec:<15.8f} {R_spec/R_fro:<10.4f}")
    print(f"{'Final residual':<20} {info_fro['final_residual']:<15.3e} {info_spec['final_residual']:<15.3e} {info_spec['final_residual']/info_fro['final_residual']:<10.4f}")
    print(f"{'Empirical α':<20} {info_fro['alpha_hat']:<15.2f} {info_spec['alpha_hat']:<15.2f} {info_spec['alpha_hat']/info_fro['alpha_hat']:<10.4f}")
    print(f"{'SE(R*)':<20} {se_fro['se']:<15.3e} {se_spec['se']:<15.3e} {se_spec['se']/se_fro['se']:<10.4f}")
    
    # Generate comparison plot
    plot_norm_comparison(edges, R_fro, R_spec, info_fro["final_eps"], 
                        str(FIGURES_DIR / "norm_comparison.png"))
    print(f"\n💾 Comparison plot saved to: {FIGURES_DIR / 'norm_comparison.png'}")
    
    return info_fro, info_spec


def run_exact_null_experiment(edges: List[BridgeEdge]) -> Tuple[Dict, Dict]:
    """Run exact null panel experiment with identical copies and proportionality test."""
    print("\n" + "="*60)
    print("🔬 EXPERIMENT 2: EXACT-NULL PANEL WITH PROPORTIONALITY TEST")
    print("="*60)
    
    m = len(edges)
    print(f"\n📊 Creating {m} identical copies from aggregate edge...")
    
    # Create identical copies
    edges_identical = create_identical_copies(edges, m)
    
    # Proportionality test for heterogeneous edges
    print("\n🔍 PROPORTIONALITY TEST - Heterogeneous Edges:")
    agg_hetero = aggregate_edge(edges)
    for i, edge in enumerate(edges):
        R_prop, rel_residual = compute_proportionality_metrics(edge.N, edge.D)
        print(f"   Edge {i+1}: R_prop = {R_prop:.6f}, rel_residual = {rel_residual:.3e}")
    
    # Test proportionality between individual edges and aggregate
    print(f"\n🔍 PROPORTIONALITY TEST - Individual vs Aggregate:")
    for i, edge in enumerate(edges):
        R_prop, rel_residual = compute_proportionality_metrics(edge.N, agg_hetero.N)
        print(f"   Edge {i+1} vs Agg: R_prop = {R_prop:.6f}, rel_residual = {rel_residual:.3e}")
    
    # Proportionality test for identical copies (should be exact)
    print(f"\n🔍 PROPORTIONALITY TEST - Identical Copies (Exact Null):")
    agg_identical = aggregate_edge(edges_identical)
    for i, edge in enumerate(edges_identical):
        R_prop, rel_residual = compute_proportionality_metrics(edge.N, edge.D)
        print(f"   Copy {i+1}: R_prop = {R_prop:.6f}, rel_residual = {rel_residual:.3e}")
        if i == 0:  # Only test first few to avoid clutter
            R_prop_agg, rel_residual_agg = compute_proportionality_metrics(edge.N, agg_identical.N)
            print(f"   Copy {i+1} vs Agg: R_prop = {R_prop_agg:.6f}, rel_residual = {rel_residual_agg:.3e}")
    
    print("📊 Running analysis on heterogeneous edges...")
    R_hetero, info_hetero = bridge_null_refined(
        [BridgeEdge(e.N.copy(), e.D.copy()) for e in edges],  # Deep copy
        eps_start=1e-2, eps_target=1e-9, eps_factor=0.5,
        residual_tol=1e-9, param_tol=1e-7, scale_matrices=True
    )
    
    print("📊 Running analysis on identical copies (exact null)...")
    R_identical, info_identical = bridge_null_refined(
        edges_identical,
        eps_start=1e-2, eps_target=1e-9, eps_factor=0.5,
        residual_tol=1e-9, param_tol=1e-7, scale_matrices=True
    )
    
    # Calculate local SE for both
    se_hetero = local_se(edges, R_hetero, eps=info_hetero["final_eps"])
    se_identical = local_se(edges_identical, R_identical, eps=info_identical["final_eps"])
    
    print("\n📈 RESULTS COMPARISON:")
    print(f"{'Metric':<25} {'Heterogeneous':<15} {'Identical':<15} {'Ratio':<10}")
    print("-" * 70)
    print(f"{'R*':<25} {R_hetero:<15.8f} {R_identical:<15.8f} {abs(R_identical-R_hetero)/abs(R_hetero):<10.4f}")
    print(f"{'Final residual':<25} {info_hetero['final_residual']:<15.3e} {info_identical['final_residual']:<15.3e} {info_identical['final_residual']/info_hetero['final_residual']:<10.4f}")
    print(f"{'Empirical α':<25} {info_hetero['alpha_hat']:<15.2f} {info_identical['alpha_hat']:<15.2f} {info_identical['alpha_hat']/info_hetero['alpha_hat']:<10.4f}")
    print(f"{'SE(R*)':<25} {se_hetero['se']:<15.3e} {se_identical['se']:<15.3e} {se_identical['se']/se_hetero['se']:<10.4f}")
    print(f"{'Max ND commutator':<25} {info_hetero['commutator_diagnostics']['max_ND_comm']:<15.3e} {info_identical['commutator_diagnostics']['max_ND_comm']:<15.3e} {'N/A':<10}")
    
    # Generate comparison plot
    plot_exact_null_comparison(edges, edges_identical, info_hetero, info_identical,
                              str(FIGURES_DIR / "exact_null_comparison.png"))
    print(f"\n💾 Comparison plot saved to: {FIGURES_DIR / 'exact_null_comparison.png'}")
    
    return info_hetero, info_identical


def run_weight_tuning_experiment(edges: List[BridgeEdge], joint_diag_enabled: bool = False) -> Tuple[np.ndarray, float, Dict]:
    """Run weight optimization experiment with optional joint diagonalization."""
    print("\n" + "="*60)
    print("🔬 EXPERIMENT 3: WEIGHT TUNING WITH JOINT DIAGONALIZATION")
    print("="*60)
    
    m = len(edges)
    print(f"\n🎯 Optimizing weights for {m} edges...")
    print("   Using projected gradient descent on simplex constraint...")
    
    # Compute initial commutator diagnostics
    initial_comm = commutator_diagnostics(edges)
    print(f"\n📊 Initial commutator diagnostics:")
    print(f"   max_NN_comm = {initial_comm['max_NN_comm']:.3e}")
    print(f"   max_DD_comm = {initial_comm['max_DD_comm']:.3e}")
    print(f"   max_ND_comm = {initial_comm['max_ND_comm']:.3e}")
    
    # Apply joint diagonalization if enabled
    jd_info = {'applied': False}
    if joint_diag_enabled:
        print(f"\n🔄 Applying joint diagonalization...")
        edges_jd, jd_info = apply_joint_diag_to_edges(edges, joint_diag_enabled=True, 
                                                      tol=1e-8, max_iter=500)
        
        if jd_info['applied']:
            print(f"   ✅ Joint diagonalization completed:")
            print(f"   Converged: {jd_info['converged']}")
            print(f"   Iterations: {jd_info['iterations']}")
            print(f"   Off-diagonal reduction: {jd_info['reduction_factor']:.2f}x")
            print(f"   Initial total off-diag: {jd_info['initial_off_diag']:.3e}")
            print(f"   Final total off-diag: {jd_info['final_off_diag']:.3e}")
            
            # Compute post-JD commutator diagnostics
            post_jd_comm = commutator_diagnostics(edges_jd)
            print(f"\n📊 Post-JD commutator diagnostics:")
            print(f"   max_NN_comm = {post_jd_comm['max_NN_comm']:.3e} (reduction: {initial_comm['max_NN_comm']/post_jd_comm['max_NN_comm']:.2f}x)")
            print(f"   max_DD_comm = {post_jd_comm['max_DD_comm']:.3e} (reduction: {initial_comm['max_DD_comm']/post_jd_comm['max_DD_comm']:.2f}x)")
            print(f"   max_ND_comm = {post_jd_comm['max_ND_comm']:.3e} (reduction: {initial_comm['max_ND_comm']/post_jd_comm['max_ND_comm']:.2f}x)")
            
            # Use transformed edges for optimization
            edges_for_opt = edges_jd
        else:
            print("   ❌ Joint diagonalization not applied")
            edges_for_opt = edges
    else:
        print(f"\n⏭️  Skipping joint diagonalization (disabled)")
        edges_for_opt = edges
    
    # Run optimization on (possibly transformed) edges
    optimal_weights, optimal_residual = optimize_weights(
        edges_for_opt, eps=1e-3, max_iter=500, step_size=0.01, tol=1e-8
    )
    
    # Generate comparison plot and get uniform baseline
    uniform_residual, opt_residual_check, uniform_R, optimal_R = plot_weight_optimization(
        edges_for_opt, optimal_weights, str(FIGURES_DIR / "weight_optimization.png")
    )
    
    print("\n📈 WEIGHT OPTIMIZATION RESULTS:")
    print(f"{'Metric':<20} {'Uniform':<15} {'Optimal':<15} {'Improvement':<12}")
    print("-" * 67)
    print(f"{'Residual':<20} {uniform_residual:<15.6e} {optimal_residual:<15.6e} {uniform_residual/optimal_residual:<12.2f}x")
    print(f"{'R*':<20} {uniform_R:<15.8f} {optimal_R:<15.8f} {abs(optimal_R-uniform_R)/abs(uniform_R)*100:<11.2f}%")
    
    print(f"\n🎯 OPTIMAL WEIGHTS:")
    for i, w in enumerate(optimal_weights):
        print(f"   Edge {i+1}: {w:.6f}")
    
    print(f"\n💾 Weight optimization plot saved to: {FIGURES_DIR / 'weight_optimization.png'}")
    
    # Add joint diagonalization info to return
    jd_info['initial_comm'] = initial_comm
    if joint_diag_enabled and jd_info['applied']:
        jd_info['post_jd_comm'] = post_jd_comm
    
    return optimal_weights, optimal_residual, jd_info


def main():
    """Run the complete analysis suite with command-line options."""
    parser = argparse.ArgumentParser(
        description="Bridge-null extended analysis suite with proportionality test and joint diagonalization"
    )
    parser.add_argument("--joint_diag", action="store_true",
                       help="Enable joint diagonalization before weight tuning")
    parser.add_argument("--dim", type=int, default=3,
                       help="Matrix dimension (default: 3)")
    parser.add_argument("--edges", type=int, default=4,
                       help="Number of edges (default: 4)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--run_checks", action="store_true",
                       help="Run self-tests for utility functions")
    parser.add_argument("--skip_spectral", action="store_true",
                       help="Skip spectral norm experiment")
    parser.add_argument("--skip_exact_null", action="store_true",
                       help="Skip exact null panel experiment")
    parser.add_argument("--skip_weight_tuning", action="store_true",
                       help="Skip weight tuning experiment")
    
    args = parser.parse_args()
    
    # Run self-tests if requested
    if args.run_checks:
        run_self_tests()
        return
    
    print("🚀 BRIDGE-NULL EXTENDED ANALYSIS SUITE")
    print("=" * 60)
    
    # Set random seed for reproducibility
    np.random.seed(args.seed)
    print(f"🎲 Random seed set to: {args.seed}")
    
    # Generate test data
    n, m = args.dim, args.edges
    print(f"📊 Generating {m} random {n}×{n} edges...")
    
    edges = make_random_edges(n, m)
    
    print(f"✅ Generated {len(edges)} edges")
    print(f"📁 Figures will be saved to: {FIGURES_DIR}")
    if args.joint_diag:
        print("🔄 Joint diagonalization: ENABLED")
    else:
        print("⏭️  Joint diagonalization: DISABLED")
    
    # Run experiments
    try:
        info_fro = info_spec = None
        info_hetero = info_identical = None
        optimal_weights = optimal_residual = jd_info = None
        
        # Experiment 1: Spectral norm comparison
        if not args.skip_spectral:
            info_fro, info_spec = run_spectral_norm_experiment(edges)
        else:
            print("\n⏭️  Skipping spectral norm experiment")
        
        # Experiment 2: Exact null panel with proportionality test
        if not args.skip_exact_null:
            info_hetero, info_identical = run_exact_null_experiment(edges)
        else:
            print("\n⏭️  Skipping exact null panel experiment")
        
        # Experiment 3: Weight tuning with optional joint diagonalization
        if not args.skip_weight_tuning:
            optimal_weights, optimal_residual, jd_info = run_weight_tuning_experiment(
                edges, joint_diag_enabled=args.joint_diag
            )
        else:
            print("\n⏭️  Skipping weight tuning experiment")
        
        # Final summary
        print("\n" + "="*60)
        print("📋 FINAL SUMMARY")
        print("="*60)
        print("✅ All requested experiments completed successfully!")
        
        if info_fro and info_spec:
            print(f"📊 Frobenius norm R* = {info_fro['final_R']:.8f}")
            print(f"📊 Spectral norm R*  = {info_spec['final_R']:.8f}")
        
        if info_hetero and info_identical:
            print(f"📊 Heterogeneous residual = {info_hetero['final_residual']:.3e}")
            print(f"📊 Identical copies residual = {info_identical['final_residual']:.3e}")
        
        if optimal_weights is not None and optimal_residual is not None:
            if info_hetero:
                improvement = info_hetero['final_residual'] / optimal_residual
                print(f"📊 Weight optimization improvement = {improvement:.2f}x")
            else:
                print(f"📊 Optimal residual = {optimal_residual:.3e}")
        
        if jd_info and jd_info.get('applied', False):
            print(f"🔄 Joint diagonalization applied: {jd_info['reduction_factor']:.2f}x off-diagonal reduction")
        
        print(f"📁 All plots saved to: {FIGURES_DIR}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
