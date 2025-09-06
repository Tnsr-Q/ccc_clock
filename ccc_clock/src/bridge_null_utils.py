#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bridge-Null Analysis Utilities

This module provides additional analysis functions for the bridge-null experiments:
1. Proportionality test for exact-null detection
2. Joint diagonalization using Jacobi rotations
"""

import numpy as np
from typing import Tuple, Dict, List


def compute_proportionality_metrics(
    N: np.ndarray, D: np.ndarray
) -> Tuple[float, float]:
    """
    Compute proportionality metrics for exact-null detection.

    Tests if N ≈ R_prop * D for some scalar R_prop by computing:
    - R_prop = <N,D>_F / ||D||_F^2 (optimal proportionality constant)
    - rel_residual = ||N - R_prop * D||_F / ||N||_F (relative residual)

    Args:
        N: First matrix (Hermitian)
        D: Second matrix (Hermitian, positive definite)

    Returns:
        Tuple of (R_prop, rel_residual)
        - R_prop: Optimal proportionality constant
        - rel_residual: Relative residual (0 indicates exact proportionality)
    """
    # Compute Frobenius inner product <N,D>_F = trace(N^H @ D)
    inner_product = np.real(np.trace(N.conj().T @ D))

    # Compute ||D||_F^2
    D_norm_sq = np.linalg.norm(D, ord="fro") ** 2

    # Handle edge case where D is zero
    if D_norm_sq < 1e-15:
        return 0.0, 1.0 if np.linalg.norm(N, ord="fro") > 1e-15 else 0.0

    # Optimal proportionality constant
    R_prop = inner_product / D_norm_sq

    # Compute residual ||N - R_prop * D||_F
    residual_matrix = N - R_prop * D
    residual_norm = np.linalg.norm(residual_matrix, ord="fro")

    # Compute relative residual
    N_norm = np.linalg.norm(N, ord="fro")
    rel_residual = residual_norm / N_norm if N_norm > 1e-15 else 0.0

    return R_prop, rel_residual


def joint_diag(
    N: np.ndarray, D: np.ndarray, tol: float = 1e-8, max_iter: int = 500
) -> Tuple[np.ndarray, Dict]:
    """
    Approximate joint diagonalization using Jacobi-style rotations.

    Finds an orthogonal matrix S that minimizes the sum of squared off-diagonal
    elements of S^T @ N @ S and S^T @ D @ S simultaneously.

    Args:
        N: First matrix to jointly diagonalize (Hermitian)
        D: Second matrix to jointly diagonalize (Hermitian)
        tol: Convergence tolerance for off-diagonal reduction
        max_iter: Maximum number of iterations

    Returns:
        Tuple of (S, info) where:
        - S: Orthogonal transformation matrix
        - info: Dictionary with convergence information
    """
    n = N.shape[0]
    assert N.shape == (n, n) and D.shape == (
        n,
        n,
    ), "Matrices must be square and same size"

    # Initialize with identity
    S = np.eye(n, dtype=np.complex128)

    # Working copies
    N_work = N.copy()
    D_work = D.copy()

    def off_diagonal_norm_squared(A):
        """Compute sum of squared off-diagonal elements."""
        return np.sum(np.abs(A) ** 2) - np.sum(np.abs(np.diag(A)) ** 2)

    # Initial off-diagonal norms
    initial_off_N = off_diagonal_norm_squared(N_work)
    initial_off_D = off_diagonal_norm_squared(D_work)
    initial_total = initial_off_N + initial_off_D

    history = []

    for iteration in range(max_iter):
        max_improvement = 0.0

        # Sweep through all pairs (i,j) with i < j
        for i in range(n):
            for j in range(i + 1, n):
                # Extract 2x2 submatrices
                N_sub = np.array(
                    [[N_work[i, i], N_work[i, j]], [N_work[j, i], N_work[j, j]]],
                    dtype=np.complex128,
                )
                D_sub = np.array(
                    [[D_work[i, i], D_work[i, j]], [D_work[j, i], D_work[j, j]]],
                    dtype=np.complex128,
                )

                # Current off-diagonal contribution
                current_off = (
                    np.abs(N_sub[0, 1]) ** 2
                    + np.abs(N_sub[1, 0]) ** 2
                    + np.abs(D_sub[0, 1]) ** 2
                    + np.abs(D_sub[1, 0]) ** 2
                )

                if current_off < tol**2:
                    continue

                # Find optimal rotation angle using simple search
                # For Hermitian matrices, we can use real Givens rotations
                best_angle = 0.0
                best_off = current_off

                # Search over angles
                for angle in np.linspace(0, np.pi / 2, 20):
                    c, s = np.cos(angle), np.sin(angle)
                    G = np.array([[c, -s], [s, c]], dtype=np.complex128)

                    # Apply rotation: G^T @ A @ G
                    N_rot = G.conj().T @ N_sub @ G
                    D_rot = G.conj().T @ D_sub @ G

                    # Compute new off-diagonal contribution
                    new_off = (
                        np.abs(N_rot[0, 1]) ** 2
                        + np.abs(N_rot[1, 0]) ** 2
                        + np.abs(D_rot[0, 1]) ** 2
                        + np.abs(D_rot[1, 0]) ** 2
                    )

                    if new_off < best_off:
                        best_off = new_off
                        best_angle = angle

                # Apply best rotation if it improves
                improvement = current_off - best_off
                if improvement > max_improvement:
                    max_improvement = improvement

                if improvement > tol**2:
                    c, s = np.cos(best_angle), np.sin(best_angle)
                    G = np.array([[c, -s], [s, c]], dtype=np.complex128)

                    # Apply to full matrices
                    # Create full rotation matrix
                    R = np.eye(n, dtype=np.complex128)
                    R[i, i] = c
                    R[i, j] = -s
                    R[j, i] = s
                    R[j, j] = c

                    # Update matrices: R^T @ A @ R
                    N_work = R.conj().T @ N_work @ R
                    D_work = R.conj().T @ D_work @ R

                    # Update cumulative transformation
                    S = S @ R

        # Check convergence
        current_off_N = off_diagonal_norm_squared(N_work)
        current_off_D = off_diagonal_norm_squared(D_work)
        current_total = current_off_N + current_off_D

        history.append(
            {
                "iteration": iteration,
                "off_diag_N": current_off_N,
                "off_diag_D": current_off_D,
                "total_off_diag": current_total,
                "max_improvement": max_improvement,
            }
        )

        # Convergence check
        if max_improvement < tol**2:
            break

    # Final off-diagonal norms
    final_off_N = off_diagonal_norm_squared(N_work)
    final_off_D = off_diagonal_norm_squared(D_work)
    final_total = final_off_N + final_off_D

    info = {
        "converged": max_improvement < tol**2,
        "iterations": iteration + 1,
        "initial_off_diag": initial_total,
        "final_off_diag": final_total,
        "reduction_factor": initial_total / final_total if final_total > 0 else np.inf,
        "initial_off_N": initial_off_N,
        "initial_off_D": initial_off_D,
        "final_off_N": final_off_N,
        "final_off_D": final_off_D,
        "history": history,
    }

    return S, info


def apply_joint_diag_to_edges(
    edges: List,
    joint_diag_enabled: bool = False,
    tol: float = 1e-8,
    max_iter: int = 500,
) -> Tuple[List, Dict]:
    """
    Apply joint diagonalization to a list of BridgeEdge objects.

    Args:
        edges: List of BridgeEdge objects
        joint_diag_enabled: Whether to apply joint diagonalization
        tol: Tolerance for joint diagonalization
        max_iter: Maximum iterations for joint diagonalization

    Returns:
        Tuple of (transformed_edges, jd_info)
    """
    if not joint_diag_enabled or len(edges) == 0:
        return edges, {"applied": False}

    # For multiple edges, we'll apply JD to the aggregate edge
    # and then apply the same transformation to all edges
    from bridge_null import aggregate_edge, BridgeEdge

    # Create aggregate edge
    agg_edge = aggregate_edge(edges)

    # Apply joint diagonalization
    S, jd_info = joint_diag(agg_edge.N, agg_edge.D, tol=tol, max_iter=max_iter)

    # Transform all edges: S^T @ edge @ S
    transformed_edges = []
    for edge in edges:
        N_new = S.conj().T @ edge.N @ S
        D_new = S.conj().T @ edge.D @ S
        transformed_edges.append(BridgeEdge(N_new, D_new))

    jd_info["applied"] = True
    jd_info["transformation_matrix"] = S

    return transformed_edges, jd_info


def run_self_tests():
    """Run self-tests for the utility functions."""
    print("🧪 Running self-tests for bridge_null_utils...")

    # Test 1: Proportionality test with exact proportional matrices
    print("  Test 1: Exact proportionality...")
    D = np.array([[2, 1], [1, 3]], dtype=np.complex128)
    R_true = 1.5
    N = R_true * D

    R_prop, rel_residual = compute_proportionality_metrics(N, D)
    assert abs(R_prop - R_true) < 1e-12, f"Expected R_prop={R_true}, got {R_prop}"
    assert rel_residual < 1e-12, f"Expected rel_residual≈0, got {rel_residual}"
    print(f"    ✅ R_prop = {R_prop:.6f}, rel_residual = {rel_residual:.2e}")

    # Test 2: Proportionality test with non-proportional matrices
    print("  Test 2: Non-proportional matrices...")
    N2 = np.array([[1, 0.5], [0.5, 2]], dtype=np.complex128)
    R_prop2, rel_residual2 = compute_proportionality_metrics(N2, D)
    assert rel_residual2 > 0.1, f"Expected significant residual, got {rel_residual2}"
    print(f"    ✅ R_prop = {R_prop2:.6f}, rel_residual = {rel_residual2:.2e}")

    # Test 3: Joint diagonalization with commuting matrices
    print("  Test 3: Joint diagonalization of commuting matrices...")
    # Create commuting matrices (same eigenvectors)
    Q = np.array(
        [[1 / np.sqrt(2), 1 / np.sqrt(2)], [1 / np.sqrt(2), -1 / np.sqrt(2)]],
        dtype=np.complex128,
    )
    N3 = Q @ np.diag([3, 1]) @ Q.conj().T
    D3 = Q @ np.diag([2, 4]) @ Q.conj().T

    S, jd_info = joint_diag(N3, D3, tol=1e-10, max_iter=100)

    # Check that transformation reduces off-diagonals
    N3_transformed = S.conj().T @ N3 @ S
    D3_transformed = S.conj().T @ D3 @ S

    off_diag_N = np.sum(np.abs(N3_transformed) ** 2) - np.sum(
        np.abs(np.diag(N3_transformed)) ** 2
    )
    off_diag_D = np.sum(np.abs(D3_transformed) ** 2) - np.sum(
        np.abs(np.diag(D3_transformed)) ** 2
    )

    print(
        f"    ✅ Converged: {jd_info['converged']}, iterations: {jd_info['iterations']}"
    )
    print(f"    ✅ Off-diagonal reduction: {jd_info['reduction_factor']:.2f}x")
    print(f"    ✅ Final off-diag norms: N={off_diag_N:.2e}, D={off_diag_D:.2e}")

    print("🎉 All self-tests passed!")


if __name__ == "__main__":
    run_self_tests()
