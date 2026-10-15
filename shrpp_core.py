#Copyright (c) 2026.Chutiphong Bunloed
#All Rights Reserved.

import numpy as np

PHI = (1 + np.sqrt(5)) / 2
TAU0 = 1.0
ALPHA = 0.5
THETA0 = 0.3
GAMMA = 1.0
K0 = 1.0


class SHRPPCore:
    def __init__(self, dimension, alpha=ALPHA, gamma=GAMMA, k0=K0):
        self.d = dimension
        self.alpha = alpha
        self.gamma = gamma
        self.k0 = k0
        self.phi = PHI
        self.tau0 = TAU0
        self.theta0 = THETA0
        self.I = np.eye(dimension, dtype=complex)
        self.H = np.zeros((dimension, dimension), dtype=complex)
        self.L_heal = np.zeros((dimension, dimension), dtype=complex)
        for i in range(min(3, dimension - 2)):
            self.L_heal[i, i + 2] = 1.0
        self.L_heal_dag = self.L_heal.conj().T
        self.rho_error = np.zeros((dimension, dimension), dtype=complex)
        self.rho_error[0, 0] = 1.0

    def fibonacci_sequence(self, n_max):
        seq = np.zeros(n_max, dtype=np.int64)
        seq[:1] = 1
        seq[1:2] = 1
        for i in range(2, n_max):
            seq[i] = seq[i - 1] + seq[i - 2]
        return seq

    def fibonacci_time(self, n_max):
        return self.fibonacci_sequence(n_max) * self.tau0

    def fibonacci_amplitudes(self, n_max):
        return self.phi ** (-self.alpha * (np.arange(n_max) + 1))

    def fibonacci_phases(self, n_max):
        return ((-1.0) ** np.arange(n_max)) * self.theta0

    def lindblad_step(self, rho, dt):
        drho = -1j * (self.H @ rho - rho @ self.H)
        drho = drho + self.gamma * (
            self.L_heal @ rho @ self.L_heal_dag
            - 0.5 * (self.L_heal_dag @ self.L_heal @ rho + rho @ self.L_heal_dag @ self.L_heal)
        )
        rho_new = rho + drho * dt
        return rho_new / np.trace(rho_new)

    def lindblad_evolve(self, rho_init, steps, dt):
        rho = rho_init.copy()
        for _ in range(steps):
            rho = self.lindblad_step(rho, dt)
        return rho

    def purity(self, rho):
        return float(np.real(np.trace(rho @ rho)))

    def unified_mirror(self):
        sx = np.array([[0, 1], [1, 0]], dtype=complex)
        sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sz = np.array([[1, 0], [0, -1]], dtype=complex)
        i2 = np.eye(2, dtype=complex)
        m_sym = np.kron(np.kron(np.kron(sx, i2), i2), i2)
        m_fold = np.kron(np.kron(np.kron(sy, i2), i2), i2)
        t_op = np.kron(np.kron(np.kron(sz, sx), i2), i2)
        t_mir = np.kron(np.kron(np.kron(sz, sy), i2), i2)
        return (m_sym + m_fold + t_op + t_mir) / 2.0

    def mirror_components(self):
        sx = np.array([[0, 1], [1, 0]], dtype=complex)
        sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sz = np.array([[1, 0], [0, -1]], dtype=complex)
        i2 = np.eye(2, dtype=complex)
        m_sym = np.kron(np.kron(np.kron(sx, i2), i2), i2)
        m_fold = np.kron(np.kron(np.kron(sy, i2), i2), i2)
        t_op = np.kron(np.kron(np.kron(sz, sx), i2), i2)
        t_mir = np.kron(np.kron(np.kron(sz, sy), i2), i2)
        return [m_sym, m_fold, t_op, t_mir]

    def generalized_mirror(self, level):
        f_level = int(np.round(self.phi ** level / np.sqrt(5)))
        k = f_level * self.k0
        m = np.zeros((self.d, self.d), dtype=complex)
        half = self.d // 2
        for i in range(half):
            m[i, i] = -k
        for i in range(half, self.d):
            m[i, i] = k
        return m, k


def resonance_amplitude(times, omega):
    return float(np.abs(np.sum(np.exp(1j * omega * times))))


def resonance_spectrum(times, omegas):
    return np.array([resonance_amplitude(times, w) for w in omegas])


def fib_spectral_function(omegas, n_max, alpha, theta0, tau0):
    idx = np.arange(n_max)
    amps = PHI ** (-alpha * (idx + 1))
    thetas = ((-1.0) ** idx) * theta0
    seq = np.zeros(n_max, dtype=np.int64)
    seq[:1] = 1
    seq[1:2] = 1
    for i in range(2, n_max):
        seq[i] = seq[i - 1] + seq[i - 2]
    times = seq * tau0
    phases = np.outer(omegas, times)
    return np.sum(amps * np.exp(1j * thetas) * np.exp(1j * phases), axis=1)
