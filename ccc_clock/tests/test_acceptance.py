"""
Acceptance criteria tests for CCC Clock Demonstration System
"""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from metrology import PARAMETER_SETS, CCCMetrology
from bridge_ccc import CCCBridgeAnalyzer
from protocol import ABBASequence, CCCProtocol


def test_a1_detection_time():
    """A1: Detection time ≤ 72h for at least one parameter set"""
    min_detection_time = min(
        params["detection_time_hours"] for params in PARAMETER_SETS.values()
    )
    assert (
        min_detection_time <= 72
    ), f"No parameter set has detection time ≤ 72h, minimum is {min_detection_time}h"


def test_a2_bridge_analysis():
    """A2: Bridge analysis convergence"""
    analyzer = CCCBridgeAnalyzer()
    result = analyzer.get_bridge_parameters()
    assert result["status"] == "converged", "Bridge analysis did not converge"
    assert result["R_star"] == 5.80, f"Expected R_star=5.80, got {result['R_star']}"


def test_a3_abba_validation():
    """A3: ABBA sign flip validation"""
    abba = ABBASequence()
    result = abba.validate_sign_flip()
    assert "passed" in result.lower(), f"ABBA validation failed: {result}"


def test_parameter_sets_available():
    """Test that all expected parameter sets are available"""
    expected_sets = ["A", "B", "C"]
    for set_name in expected_sets:
        assert set_name in PARAMETER_SETS, f"Parameter set {set_name} not found"


def test_metrology_initialization():
    """Test metrology module can be initialized"""
    metrology = CCCMetrology("A")
    result = metrology.analyze_parameters()
    assert isinstance(result, str), "Metrology analysis should return string"


def test_protocol_execution():
    """Test protocol can be executed"""
    protocol = CCCProtocol()
    result = protocol.run_protocol()
    assert result["status"] == "completed", "Protocol execution failed"
