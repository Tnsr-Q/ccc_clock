
Live Dashboard Documentation
============================

The CCC Clock Live Dashboard provides real-time monitoring of all system parameters with interactive controls and professional visualization.

Overview
--------

The dashboard displays:

* **Demodulation SNR**: Real-time signal-to-noise ratio tracking
* **Parity Ratio**: ABBA protocol validation with statistical analysis  
* **Witness Channels**: LO amplitude, polarization, B-field, temperature
* **System Status**: Overall health monitoring with alerts

Features
--------

**Real-time Updates**
- Configurable refresh rates (0.5-10 seconds)
- Adjustable time windows (1-60 minutes)
- Automatic data buffering with 1000-point history

**Interactive Controls**
- Update interval slider
- Time window adjustment
- Parameter threshold settings
- Export functionality for data and plots

**Professional Visualization**
- High-quality Plotly graphics
- Responsive layout for different screen sizes
- Color-coded status indicators
- Statistical overlays and trend analysis

**WebSocket Support**
- Live data streaming capability
- Low-latency updates
- Scalable to multiple clients
- Robust connection handling

Usage
-----

**Starting the Dashboard**::

    python dashboard.py

The dashboard will be available at http://localhost:8050

**Configuration Options**::

    python dashboard.py --port 8050 --host 0.0.0.0 --debug

**Integration with Hardware**

Replace the ``generate_mock_data()`` function with your actual data source::

    def get_real_data():
        # Connect to your measurement hardware
        snr = hardware.get_snr()
        parity = hardware.get_parity_ratio()
        # ... other parameters
        return data_dict

**Custom Layouts**

The dashboard layout can be customized by modifying the ``app.layout`` section:

* Add new plots or controls
* Adjust subplot arrangements  
* Modify styling and themes
* Include additional data sources

Dashboard Components
--------------------

**Control Panel**
- Update interval slider (0.5-10 seconds)
- Time window selector (1-60 minutes)
- System reset and export buttons

**Main Plots**
- SNR time series with trend analysis
- Parity ratio with expected value overlay
- Witness channel dual-axis plots
- Frequency domain lock-in detection

**Status Panel**
- Real-time system health indicator
- Current parameter values
- Last update timestamp
- Alert notifications

**Data Export**
- CSV export of time series data
- PNG export of current plots
- PDF report generation
- Raw data download

Customization
-------------

**Adding New Parameters**

1. Extend the ``data_buffer`` dictionary
2. Update ``generate_mock_data()`` or data source
3. Add new plot in ``update_plots()`` callback
4. Include in layout with appropriate styling

**Styling and Themes**

The dashboard uses Plotly's theming system:

* Modify ``template='plotly_white'`` for different themes
* Customize colors in the ``line=dict(color='#e74c3c')`` parameters
* Adjust layout spacing and fonts in ``update_layout()``

**Performance Optimization**

For high-frequency data:

* Increase ``maxlen`` in data buffers
* Implement data decimation for display
* Use WebSocket streaming for efficiency
* Consider database backend for persistence

Deployment
----------

**Production Deployment**::

    # Using Gunicorn
    pip install gunicorn
    gunicorn dashboard:server -b 0.0.0.0:8050

**Docker Deployment**::

    docker run -p 8050:8050 -v /data:/app/data ccc-clock

**Reverse Proxy Setup**

For HTTPS and domain routing, configure nginx::

    location /dashboard/ {
        proxy_pass http://localhost:8050/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

Troubleshooting
---------------

**Dashboard Won't Start**
- Check port availability: ``netstat -an | grep 8050``
- Verify dependencies: ``pip install plotly dash websockets``
- Check firewall settings

**No Data Displayed**
- Verify data source connection
- Check ``generate_mock_data()`` function
- Review browser console for JavaScript errors

**Performance Issues**
- Reduce update frequency
- Decrease time window
- Check system resources
- Consider data decimation

**WebSocket Connection Failures**
- Verify WebSocket support in browser
- Check network connectivity
- Review server logs for errors
- Test with different browsers
