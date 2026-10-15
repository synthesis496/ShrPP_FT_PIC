#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np
import json
import time
import shrpp_core


def run_benchmark():
    DIMS = [8, 16, 32, 64, 128, 256]
    TIMES = []
    TIMES_STD = []
    for dim in DIMS:
        core = shrpp_core.SHRPPCore(dimension=dim)
        rho_b = np.zeros((dim, dim), dtype=complex)
        rho_b[0, 0] = 1.0
        runs = []
        for _ in range(5):
            start = time.perf_counter()
            rho_t = rho_b.copy()
            for _ in range(50):
                rho_t = core.lindblad_step(rho_t, dt=0.001)
            runs.append(time.perf_counter() - start)
        TIMES.append(float(np.mean(runs)))
        TIMES_STD.append(float(np.std(runs)))
    LOG_D = np.log(np.array(DIMS, dtype=float))
    LOG_T = np.log(np.array(TIMES))
    COEFFS = np.polyfit(LOG_D, LOG_T, 1)
    return {
        "dimensions": DIMS,
        "times": TIMES,
        "std": TIMES_STD,
        "scaling_exponent": float(COEFFS[0]),
    }


if __name__ == "__main__":
    results = run_benchmark()
    with open("shrpp_benchmark.json", "w") as f:
        json.dump(results, f, indent=2)
