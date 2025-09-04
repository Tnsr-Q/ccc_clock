"""
CCC Clock Metrology Module

Implements the core equations for Computational Complexity Cosmology (CCC)
clock theory including operational curvature, SNR calculations, and ABBA
demodulation simulation.

Key equations:
- Operational curvature: R_op = K_dot / (S_e_dot + S_loss_dot)
- Clock observable: (Δf/f)_demod = Γ_Θ * R_op * A_Σ + systematics
- SNR: SNR(τ) = (Γ_Θ * R_op * A_Σ) / (σ_0/√τ)
- Time-to-detect: τ_req = (z_α * σ_0 / (Γ_Θ * R_op * A_Σ))²
"""

import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


@dataclass
class ParameterSet:
    """Parameter set for CCC clock experiments."""

    name: str
    K_dot: float  # Complexity flow rate (bits/s)
    S_loss_dot: float  # Entropy loss rate (bits/s)
    T: float  # Temperature (K)
    description: str

    def __post_init__(self):
        """Validate parameters."""
        if self.K_dot <= 0:
            raise ValueError("K_dot must be positive")
        if self.S_loss_dot <= 0:
            raise ValueError("S_loss_dot must be positive")
        if self.T <= 0:
            raise ValueError("Temperature must be positive")


# Standard parameter sets from mission brief
PARAMETER_SETS = {
    "A": ParameterSet(
        name="A (max signal)",
        K_dot=1e10,  # bits/s
        S_loss_dot=5e7,  # bits/s
        T=77,  # K
        description="Maximum signal configuration with liquid nitrogen cooling",
    ),
    "B": ParameterSet(
        name="B (balanced)",
        K_dot=3e9,  # bits/s
        S_loss_dot=1e-12 * 3e8 / (1.38e-23 * 300),  # 1 pW at 300K converted to bits/s
        T=300,  # K
        description="Balanced configuration at room temperature",
    ),
    "C": ParameterSet(
        name="C (conservative)",
        K_dot=1e9,  # bits/s
        S_loss_dot=10e-12 * 3e8 / (1.38e-23 * 300),  # 10 pW at 300K converted to bits/s
        T=300,  # K
        description="Conservative configuration with higher dissipation",
    ),
}


class CCCMetrology:
    """Main class for CCC clock metrology calculations."""

    def __init__(self, Gamma_Theta: float = 1e-6, kappa: float = 1.0):
        """
        Initialize CCC metrology calculator.

        Args:
            Gamma_Theta: Platform transfer factor for Θ-only loops
            kappa: Operational geometry coupling constant
        """
        self.Gamma_Theta = Gamma_Theta
        self.kappa = kappa

    def compute_operational_curvature(
        self, params: ParameterSet, S_e_dot: Optional[float] = None
    ) -> float:
        """
        Compute operational curvature ratio R_op = K_dot / (S_e_dot + S_loss_dot).

        Args:
            params: Parameter set
            S_e_dot: Semantic/mutual information rate (bits/s). If None, uses K_dot/10

        Returns:
            Operational curvature ratio (dimensionless)
        """
        if S_e_dot is None:
            # Default assumption: semantic rate is 10% of complexity rate
            S_e_dot = params.K_dot / 10

        denominator = S_e_dot + params.S_loss_dot
        if denominator <= 0:
            warnings.warn("Denominator S_e_dot + S_loss_dot <= 0, using regularization")
            denominator = max(denominator, 1e-10)

        R_op = params.K_dot / denominator
        return R_op

    def compute_clock_observable(
        self,
        params: ParameterSet,
        A_Sigma: float,
        systematics: float = 0.0,
        S_e_dot: Optional[float] = None,
    ) -> float:
        """
        Compute clock observable (Δf/f)_demod = Γ_Θ * R_op * A_Σ + systematics.

        Args:
            params: Parameter set
            A_Sigma: Loop area in (ln r*, θ) space
            systematics: Systematic error contribution
            S_e_dot: Semantic information rate

        Returns:
            Fractional frequency shift
        """
        R_op = self.compute_operational_curvature(params, S_e_dot)
        signal = self.Gamma_Theta * R_op * A_Sigma
        return signal + systematics

    def compute_snr(
        self,
        params: ParameterSet,
        A_Sigma: float,
        sigma_0: float,
        tau: float,
        S_e_dot: Optional[float] = None,
    ) -> float:
        """
        Compute signal-to-noise ratio SNR(τ) = (Γ_Θ * R_op * A_Σ) / (σ_0/√τ).

        Args:
            params: Parameter set
            A_Sigma: Loop area
            sigma_0: Allan deviation coefficient
            tau: Integration time (s)
            S_e_dot: Semantic information rate

        Returns:
            Signal-to-noise ratio
        """
        R_op = self.compute_operational_curvature(params, S_e_dot)
        signal = self.Gamma_Theta * R_op * A_Sigma
        noise = sigma_0 / np.sqrt(tau)
        return signal / noise

    def compute_time_to_detect(
        self,
        params: ParameterSet,
        A_Sigma: float,
        sigma_0: float,
        z_alpha: float = 3.0,
        S_e_dot: Optional[float] = None,
    ) -> float:
        """
        Compute time-to-detect τ_req = (z_α * σ_0 / (Γ_Θ * R_op * A_Σ))².

        Args:
            params: Parameter set
            A_Sigma: Loop area
            sigma_0: Allan deviation coefficient
            z_alpha: Detection threshold (standard deviations)
            S_e_dot: Semantic information rate

        Returns:
            Required integration time (s)
        """
        R_op = self.compute_operational_curvature(params, S_e_dot)
        signal = self.Gamma_Theta * R_op * A_Sigma

        if signal <= 0:
            return np.inf

        tau_req = (z_alpha * sigma_0 / signal) ** 2
        return tau_req

    def sensitivity_analysis(
        self,
        A_Sigma_range: np.ndarray,
        sigma_0_values: List[float] = [1e-17, 3e-18],
        z_alpha: float = 3.0,
    ) -> Dict:
        """
        Perform comprehensive sensitivity analysis across parameter space.

        Args:
            A_Sigma_range: Array of loop areas to test
            sigma_0_values: List of Allan deviation coefficients
            z_alpha: Detection threshold

        Returns:
            Dictionary with analysis results
        """
        results = {
            "A_Sigma": A_Sigma_range,
            "sigma_0_values": sigma_0_values,
            "parameter_sets": {},
            "acceptance_A1_met": False,
        }

        for param_name, params in PARAMETER_SETS.items():
            param_results = {
                "R_op": self.compute_operational_curvature(params),
                "tau_req_matrix": np.zeros((len(sigma_0_values), len(A_Sigma_range))),
                "snr_matrix": np.zeros((len(sigma_0_values), len(A_Sigma_range))),
            }

            for i, sigma_0 in enumerate(sigma_0_values):
                for j, A_Sigma in enumerate(A_Sigma_range):
                    tau_req = self.compute_time_to_detect(
                        params, A_Sigma, sigma_0, z_alpha
                    )
                    param_results["tau_req_matrix"][i, j] = tau_req

                    # Check A1 acceptance criterion (τ_req ≤ 72h)
                    if tau_req <= 72 * 3600 and sigma_0 == 3e-18:
                        results["acceptance_A1_met"] = True

                    # Compute SNR at 1 day integration
                    snr_1day = self.compute_snr(params, A_Sigma, sigma_0, 24 * 3600)
                    param_results["snr_matrix"][i, j] = snr_1day

            results["parameter_sets"][param_name] = param_results

        return results


class ABBASimulator:
    """Simulator for ABBA demodulation sequences."""

    def __init__(self, f_m: float = 0.5, cycle_time: float = 10.0):
        """
        Initialize ABBA simulator.

        Args:
            f_m: Modulation frequency (Hz)
            cycle_time: Total cycle time (s)
        """
        self.f_m = f_m
        self.cycle_time = cycle_time
        self.dt = cycle_time / 1000  # Time resolution

    def generate_abba_sequence(self, duration: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ABBA modulation sequence.

        Args:
            duration: Total duration (s)

        Returns:
            Tuple of (time_array, modulation_sequence)
        """
        t = np.arange(0, duration, self.dt)

        # ABBA pattern: +1, +1, -1, -1 repeating
        cycle_samples = int(self.cycle_time / self.dt)
        quarter_cycle = cycle_samples // 4

        modulation = np.zeros_like(t)
        for i in range(len(t)):
            cycle_pos = i % cycle_samples
            if cycle_pos < quarter_cycle:  # A
                modulation[i] = 1
            elif cycle_pos < 2 * quarter_cycle:  # B
                modulation[i] = 1
            elif cycle_pos < 3 * quarter_cycle:  # B (reversed)
                modulation[i] = -1
            else:  # A (reversed)
                modulation[i] = -1

        return t, modulation

    def simulate_lock_in_trace(
        self,
        params: ParameterSet,
        A_Sigma: float,
        duration: float = 3600,
        sigma_0: float = 3e-18,
        loop_reversed: bool = False,
        systematics_amplitude: float = 1e-19,
    ) -> Dict:
        """
        Simulate lock-in amplifier trace with ABBA demodulation.

        Args:
            params: Parameter set
            A_Sigma: Loop area
            duration: Measurement duration (s)
            sigma_0: Allan deviation coefficient
            loop_reversed: Whether loop is reversed (sign flip test)
            systematics_amplitude: Amplitude of systematic errors

        Returns:
            Dictionary with simulation results
        """
        metrology = CCCMetrology()

        # Generate time base and modulation
        t, modulation = self.generate_abba_sequence(duration)

        # Compute CCC signal
        R_op = metrology.compute_operational_curvature(params)
        ccc_signal = metrology.Gamma_Theta * R_op * A_Sigma

        # Apply loop reversal (sign flip)
        if loop_reversed:
            ccc_signal *= -1

        # Generate systematic errors (don't flip with loop reversal)
        systematics = systematics_amplitude * np.sin(2 * np.pi * 0.1 * t)  # Slow drift
        systematics += (
            systematics_amplitude
            * 0.5
            * np.sin(2 * np.pi * 1.0 * t)  # Faster oscillation
        )

        # Generate noise
        noise_std = sigma_0 / np.sqrt(self.dt)  # Scale noise for time resolution
        noise = np.random.normal(0, noise_std, len(t))

        # Total signal
        total_signal = ccc_signal * modulation + systematics + noise

        # Lock-in demodulation
        demod_signal = total_signal * modulation

        # Low-pass filter (simple moving average)
        filter_window = int(1.0 / self.dt)  # 1 second window
        demod_filtered = np.convolve(
            demod_signal, np.ones(filter_window) / filter_window, mode="same"
        )

        # Compute running average for SNR estimation
        tau_values = np.logspace(1, np.log10(duration / 10), 50)  # 10s to duration/10
        snr_values = []

        for tau in tau_values:
            window_samples = int(tau / self.dt)
            if window_samples < len(demod_filtered):
                windowed_mean = np.mean(demod_filtered[-window_samples:])
                windowed_std = np.std(demod_filtered[-window_samples:]) / np.sqrt(
                    window_samples
                )
                snr = abs(windowed_mean) / windowed_std if windowed_std > 0 else 0
                snr_values.append(snr)
            else:
                snr_values.append(0)

        return {
            "time": t,
            "modulation": modulation,
            "total_signal": total_signal,
            "demod_filtered": demod_filtered,
            "ccc_signal_amplitude": ccc_signal,
            "loop_reversed": loop_reversed,
            "tau_values": tau_values,
            "snr_values": snr_values,
            "final_demod_value": np.mean(
                demod_filtered[-int(60 / self.dt) :]
            ),  # Last minute average
            "theoretical_snr": metrology.compute_snr(
                params, A_Sigma, sigma_0, duration
            ),
        }

    def demonstrate_sign_flip(
        self, params: ParameterSet, A_Sigma: float, duration: float = 1800
    ) -> Dict:
        """
        Demonstrate sign flip under loop reversal (A3 acceptance criterion).

        Args:
            params: Parameter set
            A_Sigma: Loop area
            duration: Duration for each measurement

        Returns:
            Dictionary with both normal and reversed traces
        """
        # Normal loop
        trace_normal = self.simulate_lock_in_trace(
            params, A_Sigma, duration, loop_reversed=False
        )

        # Reversed loop
        trace_reversed = self.simulate_lock_in_trace(
            params, A_Sigma, duration, loop_reversed=True
        )

        # Verify sign flip
        sign_flip_detected = np.sign(trace_normal["final_demod_value"]) != np.sign(
            trace_reversed["final_demod_value"]
        )

        return {
            "normal": trace_normal,
            "reversed": trace_reversed,
            "sign_flip_detected": sign_flip_detected,
            "ratio": trace_reversed["final_demod_value"]
            / trace_normal["final_demod_value"],
        }


def compute_operational_curvature(
    K_dot: float, S_e_dot: float, S_loss_dot: float
) -> float:
    """Standalone function to compute operational curvature ratio."""
    return K_dot / (S_e_dot + S_loss_dot)


def compute_snr(
    Gamma_Theta: float, R_op: float, A_Sigma: float, sigma_0: float, tau: float
) -> float:
    """Standalone function to compute SNR."""
    signal = Gamma_Theta * R_op * A_Sigma
    noise = sigma_0 / np.sqrt(tau)
    return signal / noise


def compute_time_to_detect(
    Gamma_Theta: float,
    R_op: float,
    A_Sigma: float,
    sigma_0: float,
    z_alpha: float = 3.0,
) -> float:
    """Standalone function to compute time-to-detect."""
    signal = Gamma_Theta * R_op * A_Sigma
    if signal <= 0:
        return np.inf
    return (z_alpha * sigma_0 / signal) ** 2


if __name__ == "__main__":
    # Self-test and validation
    print("🧪 Testing CCC Metrology Module")
    print("=" * 50)

    # Initialize metrology
    metrology = CCCMetrology()

    # Test parameter sets
    print("\n📊 Parameter Set Analysis:")
    for name, params in PARAMETER_SETS.items():
        R_op = metrology.compute_operational_curvature(params)
        print(f"  {params.name}: R_op = {R_op:.2e}")

        # Test time-to-detect for A1 criterion
        A_Sigma = 1e-6  # Example loop area
        sigma_0 = 3e-18
        tau_req = metrology.compute_time_to_detect(params, A_Sigma, sigma_0)
        print(f"    τ_req = {tau_req/3600:.1f} hours (A_Σ={A_Sigma:.0e})")

        if tau_req <= 72 * 3600:
            print(f"    ✅ A1 criterion met!")
        else:
            print(f"    ❌ A1 criterion not met (need larger A_Σ or better params)")

    # Test ABBA simulator
    print("\n🔄 Testing ABBA Simulator:")
    simulator = ABBASimulator(f_m=0.5)

    # Quick sign flip test
    params_test = PARAMETER_SETS["A"]
    sign_flip_demo = simulator.demonstrate_sign_flip(
        params_test, A_Sigma=1e-6, duration=300
    )

    print(f"  Sign flip detected: {sign_flip_demo['sign_flip_detected']}")
    print(f"  Ratio (reversed/normal): {sign_flip_demo['ratio']:.3f}")

    if sign_flip_demo["sign_flip_detected"]:
        print("  ✅ A3 criterion: Sign flip under loop reversal confirmed!")
    else:
        print("  ❌ A3 criterion: Sign flip not detected (may need longer integration)")

    print("\n✅ CCC Metrology module tests completed!")
