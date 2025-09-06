
Quick Start Guide
=================

This guide will get you up and running with the CCC Clock Demonstration System in minutes.

Basic Usage
-----------

1. **Run System Validation**::

    python -m pytest tests/test_acceptance.py -v

   This validates all core functionality and performance metrics.

2. **Launch Live Dashboard**::

    python dashboard.py

   Open http://localhost:8050 to view the real-time monitoring interface.

3. **Generate Animation**::

    python animate_theta_abba.py

   Creates a 25-second animation showing the Θ-loop geometry and ABBA protocol.

4. **Explore Analysis Notebooks**::

    jupyter notebook notebooks/

   Interactive analysis of sensitivity, bridge residuals, and protocol validation.

Key Components
--------------

**Core Library**
The main CCC implementation is in the ``src/`` directory:

* ``bridge_ccc.py``: Θ-loop bridge implementation
* ``metrology.py``: Precision measurement tools
* ``protocol.py``: ABBA protocol implementation

**Live Dashboard**
Real-time monitoring of:

* Demodulation SNR
* Parity ratio tracking
* Witness channel monitoring (LO amplitude, polarization, B-field, temperature)

**Animation System**
Visualizes:

* Θ-loop geometry in 3D
* ABBA sequence timing
* Signal demodulation process
* Lock-in detection

Example Usage
-------------

**Basic CCC Measurement**::

    from src.bridge_ccc import CCCBridge
    from src.protocol import ABBAProtocol
    
    # Initialize system
    bridge = CCCBridge(sensitivity=1.2e-18)
    protocol = ABBAProtocol(cycle_time=4.0)
    
    # Run measurement
    result = bridge.measure_with_protocol(protocol)
    print(f"Fractional frequency: {result.frequency:.2e}")
    print(f"SNR: {result.snr:.1f} dB")

**Dashboard Integration**::

    # The dashboard automatically connects to the measurement system
    # and provides real-time visualization of all parameters
    python dashboard.py

**Custom Analysis**::

    import numpy as np
    from src.metrology import analyze_stability
    
    # Load measurement data
    data = np.load('measurement_data.npy')
    
    # Analyze stability
    allan_var = analyze_stability(data)
    print(f"Allan variance: {allan_var:.2e}")

Performance Validation
----------------------

The system includes comprehensive validation:

* **A1**: Sensitivity ≥ 1.0 × 10⁻¹⁸ ✓
* **A2**: SNR ≥ 20 dB ✓  
* **A3**: Systematic suppression ≥ 30 dB ✓
* **A4**: Parity ratio = 0.500 ± 0.010 ✓
* **A5**: Bridge residual ≤ 5% ✓

All criteria are automatically validated during testing.

Next Steps
----------

* Review the full API documentation
* Explore the analysis notebooks
* Customize the dashboard for your specific needs
* Integrate with your measurement hardware
* Contribute improvements via GitHub
