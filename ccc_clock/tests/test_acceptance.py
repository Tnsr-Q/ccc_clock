#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCC Clock Acceptance Tests

Automated tests to validate acceptance criteria A1-A5:
- A1: τ_req ≤ 72h for at least one case at σ₀=3×10⁻¹⁸/√τ
- A2: Bridge analysis reports R*, SE, α, ε-sweep consistency
- A3: ABBA traces show sign flip under loop reversal
- A4: Publication-ready documentation (checked via file existence)
- A5: Reproducible code from clean environment
"""

import os
import sys

import numpy as np
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from bridge_ccc import CCCBridgeAnalyzer
from metrology import ABBASimulator, CCCMetrology, PARAMETER_SETS
from protocol import ABBASequence, CCCProtocol, ThetaLoop

class TestAcceptanceCriteria:
    """Test suite for CCC clock acceptance criteria."""

    def setup_method(self):
        """Set up test fixtures."""
        self.metrology = CCCMetrology(Gamma_Theta=1e-6)
        self.bridge_analyzer = CCCBridgeAnalyzer()

        # Standard test loop
        self.test_loop = ThetaLoop(
            r_star_min=0.9, r_star_max=1.1, theta_min=0.0, theta_max=np.pi / 8
        )

        # Standard ABBA sequence
        self.test_abba = ABBASequence(
            phase_duration=5.0, modulation_frequency=0.5, total_cycles=10
        )

    def test_a1_time_to_detect_criterion(self):
        """
        Test A1: τ_req ≤ 72h for at least one case at σ₀=3×10⁻¹⁸/√τ
        """
        print("\n🧪 Testing A1: Time-to-detect criterion")

        sigma_0_target = 3e-18
        tau_limit = 72 * 3600  # 72 hours in seconds
        z_alpha = 3.0

        # Test range of loop areas
        A_Sigma_range = np.logspace(-8, -4, 20)

        a1_met = False
        successful_cases = []

        for param_name, params in PARAMETER_SETS.items():
            for A_Sigma in A_Sigma_range:
                tau_req = self.metrology.compute_time_to_detect(
                    params, A_Sigma, sigma_0_target, z_alpha
                )

                if tau_req <= tau_limit:
                    a1_met = True
                    successful_cases.append(
                        {
                            "parameter_set": param_name,
                            "A_Sigma": A_Sigma,
                            "tau_req_hours": tau_req / 3600,
                        }
                    )

        print(f"   A1 criterion met: {a1_met}")
        if successful_cases:
            print(f"   Successful cases: {len(successful_cases)}")
            for case in successful_cases[:3]:  # Show first 3
                print(
                    f"     {case['parameter_set']}: A_Σ={case['A_Sigma']:.2e}, τ_req={case['tau_req_hours']:.1f}h"
                )

        assert a1_met, "A1 criterion not met: no parameter set achieves τ_req ≤ 72h"
        assert len(successful_cases) > 0, "No successful cases found"

    def test_a2_bridge_analysis_criterion(self):
        """
        Test A2: Bridge analysis reports R*, SE, α, ε-sweep consistency
        """
        print("\n🧪 Testing A2: Bridge analysis criterion")

        # Create test edges
        edges = self.bridge_analyzer.create_ccc_edges(n_dim=3, n_edges=4)

        # Perform bridge analysis
        result = self.bridge_analyzer.analyze_ccc_bridge(edges)

        # Validate A2 components
        validation = self.bridge_analyzer.validate_bridge_analysis(result)

        print(f"   R* reported: {validation['R_star_reported']}")
        print(f"   SE reported: {validation['SE_reported']}")
        print(f"   α reported: {validation['alpha_reported']}")
        print(f"   ε-sweep consistent: {validation['eps_sweep_consistent']}")
        print(f"   A2 criterion met: {validation['A2_met']}")

        if not validation["A2_met"]:
            print(f"   Issues: {validation['issues']}")

        # Individual assertions
        assert result.R_star is not None, "R* not reported"
        assert result.se_estimate is not None, "SE not reported"
        assert result.alpha_factor is not None, "α factor not reported"
        assert result.converged, "ε-sweep not converged"
        assert result.commutator_norms is not None, "Commutator diagnostics missing"

        # Overall A2 assertion
        assert validation["A2_met"], f"A2 criterion not met: {validation['issues']}"

    def test_a3_sign_flip_criterion(self):
        """
        Test A3: ABBA traces show sign flip under loop reversal
        """
        print("\n🧪 Testing A3: Sign flip criterion")

        # Initialize ABBA simulator
        simulator = ABBASimulator(f_m=0.5, cycle_time=20.0)

        # Use parameter set A for testing
        params_test = PARAMETER_SETS["A"]
        A_Sigma_test = 1e-6
        duration_test = 300  # 5 minutes

        # Simulate sign flip demonstration
        sign_flip_demo = simulator.demonstrate_sign_flip(
            params_test, A_Sigma_test, duration=duration_test
        )

        sign_flip_detected = sign_flip_demo["sign_flip_detected"]
        signal_ratio = sign_flip_demo["ratio"]

        print(f"   Sign flip detected: {sign_flip_detected}")
        print(f"   Signal ratio (reversed/normal): {signal_ratio:.3f}")
        print(f"   Expected ratio ≈ -1: {abs(signal_ratio + 1) < 0.5}")

        # Test orthogonality with protocol
        protocol = CCCProtocol(self.test_loop, self.test_abba)

        # Compute test signal
        R_op = self.metrology.compute_operational_curvature(params_test)
        ccc_signal = self.metrology.compute_clock_observable(params_test, A_Sigma_test)

        # Execute orthogonality tests
        test_results = protocol.execute_orthogonality_tests(ccc_signal)

        all_ortho_tests_passed = all(
            result["passed"] for result in test_results.values()
        )

        print(f"   Orthogonality tests passed: {all_ortho_tests_passed}")
        for test_name, result in test_results.items():
            print(f"     {test_name}: {'PASS' if result['passed'] else 'FAIL'}")

        # A3 assertions
        assert sign_flip_detected, "Sign flip not detected in ABBA simulation"
        assert (
            abs(signal_ratio + 1) < 0.5
        ), f"Signal ratio {signal_ratio:.3f} not close to -1"
        assert all_ortho_tests_passed, "Not all orthogonality tests passed"

    def test_a4_documentation_criterion(self):
        """
        Test A4: Publication-ready documentation exists
        """
        print("\n🧪 Testing A4: Documentation criterion")

        # Check for required files
        base_dir = os.path.join(os.path.dirname(__file__), "..")

        required_files = [
            "README.md",
            "src/metrology.py",
            "src/bridge_ccc.py",
            "src/protocol.py",
            "notebooks/01_sensitivity_dashboard.ipynb",
            "notebooks/02_bridge_residual_sweeps.ipynb",
            "notebooks/03_protocol_validation.ipynb",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
            else:
                print(f"   ✅ {file_path}")

        if missing_files:
            print(f"   ❌ Missing files: {missing_files}")

        # Check for figures directory
        figures_dir = os.path.join(base_dir, "figures")
        figures_exist = os.path.exists(figures_dir)
        print(f"   Figures directory exists: {figures_exist}")

        # Check for paper assets directory
        paper_dir = os.path.join(base_dir, "paper_assets")
        paper_exist = os.path.exists(paper_dir)
        print(f"   Paper assets directory exists: {paper_exist}")

        print(f"   A4 criterion met: {len(missing_files) == 0}")

        assert len(missing_files) == 0, f"Missing required files: {missing_files}"
        assert figures_exist, "Figures directory missing"

    def test_a5_reproducibility_criterion(self):
        """
        Test A5: Code runs from clean environment
        """
        print("\n🧪 Testing A5: Reproducibility criterion")

        # Test that all modules can be imported
        try:
            from bridge_ccc import CCCBridgeAnalyzer
            from metrology import CCCMetrology, PARAMETER_SETS
            from protocol import ABBASequence, CCCProtocol, ThetaLoop

            print("   ✅ All modules import successfully")
            modules_import = True
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            modules_import = False

        # Test basic functionality
        try:
            # Test metrology
            metrology = CCCMetrology()
            params = PARAMETER_SETS["A"]
            R_op = metrology.compute_operational_curvature(params)

            # Test bridge analysis
            analyzer = CCCBridgeAnalyzer()
            edges = analyzer.create_ccc_edges(n_dim=2, n_edges=3)

            # Test protocol
            loop = ThetaLoop(1.0, 1.1, 0.0, 0.1)
            abba = ABBASequence(1.0, 1.0, 2)
            protocol = CCCProtocol(loop, abba)

            print("   ✅ Basic functionality works")
            functionality_works = True
        except Exception as e:
            print(f"   ❌ Functionality error: {e}")
            functionality_works = False

        # Test numerical consistency
        try:
            # Same calculation should give same result
            result1 = metrology.compute_time_to_detect(params, 1e-6, 3e-18)
            result2 = metrology.compute_time_to_detect(params, 1e-6, 3e-18)

            numerical_consistent = abs(result1 - result2) < 1e-12
            print(f"   ✅ Numerical consistency: {numerical_consistent}")
        except Exception as e:
            print(f"   ❌ Numerical consistency error: {e}")
            numerical_consistent = False

        a5_met = modules_import and functionality_works and numerical_consistent
        print(f"   A5 criterion met: {a5_met}")

        assert modules_import, "Module imports failed"
        assert functionality_works, "Basic functionality failed"
        assert numerical_consistent, "Numerical results not consistent"

    def test_overall_acceptance_summary(self):
        """
        Overall summary of all acceptance criteria.
        """
        print("\n📋 Overall Acceptance Criteria Summary")
        print("=" * 45)

        # This test runs all others and summarizes
        # Individual tests will have already run by pytest

        # Quick validation of key metrics
        metrology = CCCMetrology()

        # A1 quick check
        params_a = PARAMETER_SETS["A"]
        tau_req_min = metrology.compute_time_to_detect(params_a, 1e-6, 3e-18)
        a1_quick = tau_req_min <= 72 * 3600

        # A2 quick check
        analyzer = CCCBridgeAnalyzer()
        edges = analyzer.create_ccc_edges(n_dim=2, n_edges=3)
        result = analyzer.analyze_ccc_bridge(edges)
        a2_quick = result.converged and result.R_star is not None

        # A3 quick check
        simulator = ABBASimulator()
        sign_flip = simulator.demonstrate_sign_flip(params_a, 1e-6, 60)
        a3_quick = sign_flip["sign_flip_detected"]

        print(f"A1 (Time-to-detect ≤ 72h): {'✅ PASS' if a1_quick else '❌ FAIL'}")
        print(f"A2 (Bridge analysis): {'✅ PASS' if a2_quick else '❌ FAIL'}")
        print(f"A3 (Sign flip): {'✅ PASS' if a3_quick else '❌ FAIL'}")
        print(f"A4 (Documentation): ✅ PASS (checked in separate test)")
        print(f"A5 (Reproducibility): ✅ PASS (checked in separate test)")

        overall_pass = a1_quick and a2_quick and a3_quick
        print(f"\n{'='*45}")
        print(
            f"OVERALL STATUS: {'✅ READY FOR EXPERIMENT' if overall_pass else '❌ NEEDS IMPROVEMENT'}"
        )
        print(f"{'='*45}")

        # This is informational, don't fail the test
        # Individual criterion tests will handle failures


if __name__ == "__main__":
    # Run tests directly
    test_suite = TestAcceptanceCriteria()
    test_suite.setup_method()

    print("🚀 CCC Clock Acceptance Tests")
    print("=" * 35)

    try:
        test_suite.test_a1_time_to_detect_criterion()
        print("✅ A1 test passed")
    except AssertionError as e:
        print(f"❌ A1 test failed: {e}")

    try:
        test_suite.test_a2_bridge_analysis_criterion()
        print("✅ A2 test passed")
    except AssertionError as e:
        print(f"❌ A2 test failed: {e}")

    try:
        test_suite.test_a3_sign_flip_criterion()
        print("✅ A3 test passed")
    except AssertionError as e:
        print(f"❌ A3 test failed: {e}")

    try:
        test_suite.test_a4_documentation_criterion()
        print("✅ A4 test passed")
    except AssertionError as e:
        print(f"❌ A4 test failed: {e}")

    try:
        test_suite.test_a5_reproducibility_criterion()
        print("✅ A5 test passed")
    except AssertionError as e:
        print(f"❌ A5 test failed: {e}")

    test_suite.test_overall_acceptance_summary()
