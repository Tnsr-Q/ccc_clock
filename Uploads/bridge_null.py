#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import warnings
from typing import List, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------
# 1️⃣  Core data structure
# --------------------------------------------------------------
class BridgeEdge:
    def __init__(self, N: np.ndarray, D: np.ndarray, dtype=np.complex128):
        self.N = np.asarray(N, dtype=dtype)
        self.D = np.asarray(D, dtype=dtype)
        self.check()

    def check(self) -> None:
        assert self.N.shape == self.D.shape
        assert self.N.shape[0] == self.N.shape[1]
        if not np.allclose(self.N, self.N.conj().T, atol=1e-12):
            raise ValueError("N must be Hermitian")
        if not np.allclose(self.D, self.D.conj().T, atol=1e-12):
            raise ValueError("D must be Hermitian")


# --------------------------------------------------------------
# 2️⃣  Matrix exponential (SciPy if present, otherwise fallback)
# --------------------------------------------------------------
def _expm(A: np.ndarray) -> np.ndarray:
    try:
        from scipy.linalg import expm
        return expm(A)
    except Exception:  # pragma: no cover
        normA = np.linalg.norm(A, ord=2)
        k = max(0, int(np.ceil(np.log2(normA / 0.5)))) if normA > 0 else 0
        A_scaled = A / (2 ** k)
        term = np.eye(A.shape[0], dtype=A.dtype)
        S = term.copy()
        for m in range(1, 33):
            term = term @ (A_scaled / m)
            S += term
        for _ in range(k):
            S = S @ S
        return S


# --------------------------------------------------------------
# 3️⃣  Residual (Frobenius norm)
# --------------------------------------------------------------
def cycle_residual_fro(edges: List[BridgeEdge], R: float, eps: float = 1e-2) -> float:
    U = None
    for e in edges:
        B = e.N - R * e.D
        Ue = _expm(-eps * B)
        U = Ue if U is None else (Ue @ U)
    if U is None:
        return 0.0
    I = np.eye(U.shape[0], dtype=U.dtype)
    return float(np.linalg.norm(U - I, ord='fro'))


# --------------------------------------------------------------
# 4️⃣  Diagnostics & Utilities
# --------------------------------------------------------------
def _regularise_D(edges: List[BridgeEdge]) -> None:
    for i, e in enumerate(edges):
        w = np.linalg.eigvalsh(e.D)
        min_eig = np.min(w)
        if min_eig <= 0:
            delta = 1e-6 * max(1.0, np.linalg.norm(e.D, ord=2))
            e.D = e.D + delta * np.eye(e.D.shape[0])
            warnings.warn(
                f"Edge {i}: D not PD (min eig = {min_eig:.2e}); "
                f"regularised with δ={delta:.2e}"
            )


def commutator_diagnostics(edges: List[BridgeEdge]) -> Dict[str, float]:
    m = len(edges)
    max_NN = max_DD = max_ND = 0.0
    for i in range(m):
        for j in range(i + 1, m):
            max_NN = max(max_NN,
                         np.linalg.norm(edges[i].N @ edges[j].N - edges[j].N @ edges[i].N, ord=2))
            max_DD = max(max_DD,
                         np.linalg.norm(edges[i].D @ edges[j].D - edges[j].D @ edges[i].D, ord=2))
    for i in range(m):
        for j in range(m):
            max_ND = max(max_ND,
                         np.linalg.norm(edges[i].N @ edges[j].D - edges[j].D @ edges[i].N, ord=2))
    return dict(max_NN_comm=max_NN, max_DD_comm=max_DD, max_ND_comm=max_ND)


def is_effectively_commuting(comm_diag: Dict[str, float], atol: float = 1e-12) -> bool:
    return (comm_diag["max_NN_comm"] < atol and
            comm_diag["max_DD_comm"] < atol and
            comm_diag["max_ND_comm"] < atol)


def residual_lower_bound(eps: float, comm_diag: Dict[str, float]) -> float:
    return eps * comm_diag["max_ND_comm"]


def _scale_edges(edges: List[BridgeEdge]) -> float:
    max_norm = 0.0
    for e in edges:
        max_norm = max(max_norm, np.linalg.norm(e.N, ord=2), np.linalg.norm(e.D, ord=2))
    if max_norm == 0.0:
        return 1.0
    scale = 1.0 / np.sqrt(max_norm)
    for e in edges:
        e.N *= scale
        e.D *= scale
    return scale


def aggregate_center_R0(edges: List[BridgeEdge]) -> Tuple[float, float]:
    A = None
    m = 0
    for e in edges:
        w, V = np.linalg.eigh(e.D)
        Dmh = V @ np.diag(1.0 / np.sqrt(w)) @ V.conj().T
        S = Dmh @ e.N @ Dmh
        A = S if A is None else (A + S)
        m += 1
    vals = np.linalg.eigvalsh(A)
    lam_min, lam_max = float(vals[0]), float(vals[-1])
    R0 = (lam_max + lam_min) / (2.0 * m)
    halfspan = (lam_max - lam_min) / (2.0 * m)
    return R0, halfspan


def alpha_hat_from_history(history, max_ND_comm):
    ratios = [h["residual"] / (h["eps"] * max_ND_comm + 1e-300) for h in history if h["eps"] > 0]
    return float(np.median(ratios)) if ratios else 1.0


# New: Slope/curvature SE near the minimum
def local_se(edges, R_hat, eps=1e-3, h=1e-3, noise_floor=0.0):
    f = lambda R: cycle_residual_fro(edges, R, eps=eps)
    f_m = f(R_hat - h)
    f_0 = f(R_hat)
    f_p = f(R_hat + h)
    slope = (f_p - f_m) / (2 * h)
    curv = (f_p - 2 * f_0 + f_m) / (h * h)
    se = np.sqrt((noise_floor + 1e-18) / (slope * slope + 1e-18))
    return dict(slope=slope, curvature=curv, se=se)


# New: Edge aggregation function
def aggregate_edge(edges, w=None):
    m = len(edges)
    if w is None:
        w = np.ones(m) / m
    Nagg = sum(w[i] * edges[i].N for i in range(m))
    Dagg = sum(w[i] * edges[i].D for i in range(m))
    return BridgeEdge(Nagg, Dagg)


# --------------------------------------------------------------
# 5️⃣  Brent + adaptive bracketing
# --------------------------------------------------------------
def _brent_scalar(f, a, b, c, *, param_tol=1e-6,
                  obj_tol=1e-12, max_iter=200, min_iter=5):
    x = w = v = b
    fx = fw = fv = f(x)
    d = e = 0.0
    eps = np.sqrt(np.finfo(float).eps)
    for it in range(max_iter):
        xm = 0.5 * (a + c)
        tol1 = eps * abs(x) + param_tol
        tol2 = 2.0 * tol1
        if abs(x - xm) <= (tol2 - 0.5 * (c - a)) and it >= min_iter:
            break
        if abs(e) > tol1:
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = 2.0 * (q - r)
            if q > 0:
                p = -p
            q = abs(q)
            etemp = e
            e = d
            if (abs(p) < abs(0.5 * q * etemp) and p > q * (a - x) and p < q * (c - x)):
                d = p / q
                u = x + d
                if (u - a) < tol2 or (c - u) < tol2:
                    d = np.sign(xm - x) * tol1
            else:
                e = (c - x) if (x >= xm) else (a - x)
                d = 0.5 * e
        else:
            e = (c - x) if (x >= xm) else (a - x)
            d = 0.5 * e
        u = x + (d if abs(d) >= tol1 else np.sign(d) * tol1)
        fu = f(u)
        if fu <= fx:
            if u >= x:
                a = x
            else:
                c = x
            v, w, x = w, x, u
            fv, fw, fx = fw, fx, fu
        else:
            if u < x:
                a = u
            else:
                c = u
            if fu <= fw or w == x:
                v, w = w, u
                fv, fw = fw, fu
            elif fu <= fv or v == x or v == w:
                v, fv = u, fu
        if it >= min_iter and abs(fx - (f_opt := fx)) < obj_tol:
            break
    return x, fx, it + 1


def _adaptive_bracket(f, R0, halfspan,
                     expand_factor=2.0, max_expansions=12,
                     rel_margin=1e-3):
    a = R0 - 3 * halfspan
    b = R0
    c = R0 + 3 * halfspan
    f_a, f_b, f_c = f(a), f(b), f(c)
    for _ in range(max_expansions):
        max_end = max(f_a, f_c)
        if f_b <= max_end * (1.0 - rel_margin):
            break
        halfspan *= expand_factor
        a = R0 - 3 * halfspan
        c = R0 + 3 * halfspan
        f_a, f_c = f(a), f(c)
    return a, b, c


# --------------------------------------------------------------
# 6️⃣  Main driver
# --------------------------------------------------------------
def bridge_null_refined(edges: List[BridgeEdge],
                       *,
                       eps_start: float = 1e-2,
                       eps_target: float = 1e-9,
                       eps_factor: float = 0.5,
                       residual_tol: float = 1e-9,
                       param_tol: float = 1e-7,
                       scale_matrices: bool = True) -> Tuple[float, Dict]:
    _regularise_D(edges)
    comm_diag = commutator_diagnostics(edges)
    if scale_matrices:
        scale = _scale_edges(edges)
        print(f"🔧  Uniform scaling factor applied: {scale:.3e}")
    if is_effectively_commuting(comm_diag):
        print("🚀  All commutators ≈ 0 → an exact bridge-null exists.")
    else:
        print("⚠️  Non-zero commutators detected:")
        print(f"    max_NN = {comm_diag['max_NN_comm']:.3e}, "
              f"max_DD = {comm_diag['max_DD_comm']:.3e}, "
              f"max_ND = {comm_diag['max_ND_comm']:.3e}")
    R0, halfspan = aggregate_center_R0(edges)
    eps = eps_start
    history = []
    while eps >= eps_target:
        obj = lambda R: cycle_residual_fro(edges, R, eps=eps)
        a, b, c = _adaptive_bracket(obj, R0, halfspan)
        R_opt, f_opt, iters = _brent_scalar(
            obj, a, b, c,
            param_tol=param_tol,
            obj_tol=residual_tol * 0.5,
            min_iter=5,
        )
        bound = residual_lower_bound(eps, comm_diag)
        print(f"   eps = {eps:.1e} | residual = {f_opt:.3e} | "
              f"first-order bound ≈ {bound:.3e}")
        history.append(dict(eps=eps, R=R_opt, residual=f_opt,
                           iters=iters, bound=bound))
        if f_opt <= residual_tol:
            break
        R0 = R_opt
        eps *= eps_factor
    
    # 1) Dynamic convergence tolerance
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
        "converged": final["residual"] <= tol_dyn, # Use dynamic tolerance
        "alpha_hat": alpha_hat,
        "dynamic_tol": tol_dyn
    }
    
    # Update note based on dynamic convergence
    if not info["converged"]:
        info["note"] = (
            "The first-order bound (ε·max_ND_comm) is larger than the "
            "requested tolerance. To improve you must either "
            "(A) make the matrices more commuting or "
            "(B) reduce ε further (possible until floating-point limits)."
        )
    else:
        info["note"] = f"Converged to commutator floor (α≈{alpha_hat:.2f})."
        
    return final["R"], info


# --------------------------------------------------------------
# 7️⃣  Toy generators
# --------------------------------------------------------------
def make_random_edges(n: int, m: int) -> List[BridgeEdge]:
    edges = []
    for _ in range(m):
        A = np.random.randn(n, n)
        D = A.T @ A + 0.2 * np.eye(n)
        B = np.random.randn(n, n)
        N = B.T @ B
        edges.append(BridgeEdge(N, D))
    return edges


def make_commuting_edges(n: int, m: int) -> List[BridgeEdge]:
    Q, _ = np.linalg.qr(np.random.randn(n, n))
    eig_N = np.sort(np.random.rand(n))[::-1] + 0.1
    eig_D = np.sort(np.random.rand(n))[::-1] + 0.2
    N0 = Q @ np.diag(eig_N) @ Q.T.conj()
    D0 = Q @ np.diag(eig_D) @ Q.T.conj()
    return [BridgeEdge(N0.copy(), D0.copy()) for _ in range(m)]


# --------------------------------------------------------------
# 8️⃣  Command‑line interface (optional)
# --------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge‑null finder with diagnostic floor"
    )
    parser.add_argument("--commuting", action="store_true",
                        help="Generate a commuting toy problem (exact null).")
    parser.add_argument("--dim", type=int, default=2,
                        help="Matrix dimension (default 2).")
    parser.add_argument("--edges", type=int, default=3,
                        help="Number of edges (default 3).")
    parser.add_argument("--eps_target", type=float, default=1e-9,
                        help="Desired residual tolerance.")
    parser.add_argument("--max_eps", type=float, default=1e-2,
                        help="Starting epsilon (default 1e-2).")
    parser.add_argument("--factor", type=float, default=0.5,
                        help="ε reduction factor per continuation step.")
    parser.add_argument("--demo_exact", action="store_true",
                        help="Run the exact null demo with an aggregate edge.")
    args = parser.parse_args()
    np.random.seed(42)
    if args.commuting:
        edges = make_commuting_edges(args.dim, args.edges)
    else:
        edges = make_random_edges(args.dim, args.edges)
    
    if args.demo_exact:
        agg_edge = aggregate_edge(edges)
        edges = [agg_edge] * args.edges
        
    R_star, info = bridge_null_refined(
        edges,
        eps_start=args.max_eps,
        eps_target=args.eps_target,
        eps_factor=args.factor,
        residual_tol=args.eps_target,
        param_tol=1e-7,
        scale_matrices=True,
    )
    
    # Calculate local SE
    se_info = local_se(edges, R_star, eps=info["final_eps"])
    
    print("\n=== Result Summary ===")
    print(f"R* = {R_star:.12f}")
    print(f"Final residual   = {info['final_residual']:.3e}")
    print(f"Final ε          = {info['final_eps']:.1e}")
    print(f"Converged?       = {info['converged']}")
    print("Note:", info["note"])
    print(f"Empirical α ≈ {info['alpha_hat']:.2f}")
    print(f"Dynamic tolerance= {info['dynamic_tol']:.3e}")
    print(f"SE(R*)           = {se_info['se']:.3e}")
    print(f"Local Slope      = {se_info['slope']:.3e}")
    print(f"Local Curvature  = {se_info['curvature']:.3e}")
    
    # --------------------------------------------------------------
    # Plotting the residual curve for the *last* ε
    # --------------------------------------------------------------
    R0, halfspan = aggregate_center_R0(edges)
    R_grid = np.linspace(R0 - 4 * halfspan, R0 + 4 * halfspan, 400)
    resid_grid = [cycle_residual_fro(edges, R, eps=info["final_eps"]) for R in R_grid]

    plt.figure(figsize=(9, 5))
    plt.plot(R_grid, resid_grid, label=f"Residual (ε={info['final_eps']:.1e})")
    plt.axvline(R_star, color="r", linestyle="--", label=f"R* = {R_star:.6f}")
    plt.axhline(0, color="k", lw=0.5, alpha=0.6)
    plt.xlabel("R")
    plt.ylabel("Residual (Frobenius norm)")
    plt.title("Bridge‑null residual landscape – final ε")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()