
API Reference
=============

This section provides detailed documentation for all modules in the CCC Clock Demonstration System.

Core Modules
------------

.. automodule:: bridge_ccc
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: metrology
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: protocol
   :members:
   :undoc-members:
   :show-inheritance:

Dashboard Module
----------------

The dashboard provides real-time monitoring capabilities with the following key functions:

* ``generate_mock_data()``: Simulates realistic CCC measurement data
* ``update_data_buffer()``: Continuously updates measurement buffer
* ``update_plots()``: Refreshes all dashboard visualizations
* ``update_interval()``: Adjusts refresh rate based on user input

Animation Module
----------------

The animation system creates comprehensive visualizations:

* ``create_theta_loop_3d()``: Generates 3D Θ-loop geometry
* ``create_abba_sequence()``: Produces ABBA timing sequences
* ``generate_ccc_signal()``: Simulates CCC measurement signals
* ``animate_frame()``: Renders individual animation frames

Utility Functions
-----------------

Additional utility functions for data processing and analysis:

* ``load_measurement_data()``: Loads experimental data files
* ``calculate_allan_variance()``: Computes frequency stability metrics
* ``analyze_systematic_errors()``: Evaluates error suppression performance
* ``generate_validation_report()``: Creates comprehensive test reports

Error Handling
--------------

The system includes robust error handling for:

* Hardware communication failures
* Data acquisition interruptions  
* Analysis computation errors
* Dashboard connection issues
* Animation rendering problems

All errors are logged with appropriate severity levels and user-friendly messages.

Configuration
-------------

System configuration is managed through:

* ``config.yaml``: Main configuration file
* Environment variables for sensitive parameters
* Command-line arguments for runtime options
* Dashboard settings for visualization preferences

The configuration system supports both development and production deployments.
