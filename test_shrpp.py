#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import json
import shrpp_core

def run_t31():
    core = shrpp_core.SHRPPCore(dimension=5)
    N = 100
    fib_times = core.fibonacci_time(N)
    periodic_times = np.arange(N) * shrpp_core.TAU0
    omegas = np.linspace(0.01, 10.0, 2000)
    A_per = shrpp_core.resonance_spectrum(periodic_times, omegas)
    A_fib = shrpp_core.resonance_spectrum(fib_times, omegas)
    max_per = float(np.max(A_per))
    max_fib = float(np.max(A_fib))
    ratio = max_per / max_fib
    return {
        "max_periodic": max_per,
        "max_fibonacci": max_fib,
        "suppression_ratio": ratio,
    }


def run_t32():
    core = shrpp_core.SHRPPCore(dimension=5)
    F_LEVELS = np.array([1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])
    CUM = np.cumsum(F_LEVELS) * 10
    purities = np.zeros(14)
    rho = core.rho_error.copy()
    prev = 0
    for level in range(14):
        steps = CUM[level] - prev
        rho = core.lindblad_evolve(rho, int(steps), dt=0.001)
        prev = CUM[level]
        purities[level] = core.purity(rho)
    return {
        "purities": [float(p) for p in purities],
        "monotonic": bool(np.all(np.diff(purities) > -1e-6)),
    }


def run_t33():
    core = shrpp_core.SHRPPCore(dimension=5)
    N = 200
    gate_fib = np.zeros(N, dtype=bool)
    gate_fib[[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]] = True
    gate_per = np.zeros(N, dtype=bool)
    gate_per[np.arange(1, N, 10)] = True
    rho_f = core.rho_error.copy()
    rho_p = core.rho_error.copy()
    for t in range(N):
        rho_f = core.lindblad_step(rho_f, dt=0.05 * gate_fib[t])
        rho_p = core.lindblad_step(rho_p, dt=0.05 * gate_per[t])
    p_fib = core.purity(rho_f)
    p_per = core.purity(rho_p)
    return {
        "purity_fibonacci": p_fib,
        "purity_periodic": p_per,
        "improvement": p_fib / p_per,
    }


def run_t34():
    N = 15
    idx = np.arange(N)
    amps = shrpp_core.PHI ** (-shrpp_core.ALPHA * (idx + 1))
    thetas = ((-1.0) ** idx) * shrpp_core.THETA0
    partial = np.zeros(N)
    for n_cut in range(1, N + 1):
        s = np.sum(amps[:n_cut] * np.exp(1j * thetas[:n_cut]))
        partial[n_cut - 1] = np.abs(s)
    residual = float(np.abs(partial[-1] - partial[-2]))
    return {
        "limit_value": float(partial[-1]),
        "residual": residual,
        "partial_sums": [float(p) for p in partial],
    }


def run_t35():
    core = shrpp_core.SHRPPCore(dimension=16)
    m_uni = core.unified_mirror()
    i16 = np.eye(16, dtype=complex)
    inv_err = float(np.linalg.norm(m_uni @ m_uni - i16))
    mirrors = core.mirror_components()
    anti_norms = []
    for i in range(4):
        for j in range(i + 1, 4):
            anti = mirrors[i] @ mirrors[j] + mirrors[j] @ mirrors[i]
            anti_norms.append(float(np.linalg.norm(anti)))
    return {
        "involution_error": inv_err,
        "anticommutation_norms": anti_norms,
    }


def run_t40():
    core = shrpp_core.SHRPPCore(dimension=5)
    m, k = core.generalized_mirror(level=5)
    psi_c = np.zeros(5, dtype=complex)
    psi_c[0] = 1.0
    psi_e = np.zeros(5, dtype=complex)
    psi_e[2] = 1.0
    op_c = np.eye(5) + m / k
    op_e = np.eye(5) - m / k
    return {
        "norm_codespace": float(np.linalg.norm(op_c @ psi_c)),
        "norm_error": float(np.linalg.norm(op_e @ psi_e)),
    }


if __name__ == "__main__":
    results = {
        "t31": run_t31(),
        "t32": run_t32(),
        "t33": run_t33(),
        "t34": run_t34(),
        "t35": run_t35(),
        "t40": run_t40(),
    }
    with open("shrpp_results.json", "w") as f:
        json.dump(results, f, indent=2)
