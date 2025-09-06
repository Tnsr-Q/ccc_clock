#!/usr/bin/env python3
"""
CCC Clock Live Wall Dashboard

Real-time monitoring dashboard for CCC Clock demonstration system.
Displays demodulation SNR, parity ratio, and witness channels.
"""

import logging
import threading
import time
from collections import deque
from datetime import datetime, timedelta

import dash
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global data storage
data_buffer = {
    "timestamps": deque(maxlen=1000),
    "snr": deque(maxlen=1000),
    "parity_ratio": deque(maxlen=1000),
    "lo_amplitude": deque(maxlen=1000),
    "polarization": deque(maxlen=1000),
    "b_field": deque(maxlen=1000),
    "temperature": deque(maxlen=1000),
}


# Simulated data generator (replace with actual data source)
def generate_mock_data():
    """Generate realistic mock data for demonstration"""
    timestamp = datetime.now()

    # Simulate realistic CCC clock parameters
    base_snr = 25.0 + 5.0 * np.sin(time.time() / 60) + np.random.normal(0, 2)
    parity_ratio = 0.5 + 0.1 * np.sin(time.time() / 30) + np.random.normal(0, 0.02)
    lo_amp = 1.0 + 0.05 * np.sin(time.time() / 45) + np.random.normal(0, 0.01)
    polarization = 45.0 + 2.0 * np.sin(time.time() / 90) + np.random.normal(0, 0.5)
    b_field = 1e-6 + 1e-8 * np.sin(time.time() / 120) + np.random.normal(0, 1e-9)
    temperature = 295.0 + 0.5 * np.sin(time.time() / 180) + np.random.normal(0, 0.1)

    return {
        "timestamp": timestamp,
        "snr": max(0, base_snr),
        "parity_ratio": np.clip(parity_ratio, 0, 1),
        "lo_amplitude": max(0, lo_amp),
        "polarization": polarization % 360,
        "b_field": max(0, b_field),
        "temperature": temperature,
    }


def update_data_buffer():
    """Continuously update data buffer with new measurements"""
    while True:
        data = generate_mock_data()

        data_buffer["timestamps"].append(data["timestamp"])
        data_buffer["snr"].append(data["snr"])
        data_buffer["parity_ratio"].append(data["parity_ratio"])
        data_buffer["lo_amplitude"].append(data["lo_amplitude"])
        data_buffer["polarization"].append(data["polarization"])
        data_buffer["b_field"].append(data["b_field"])
        data_buffer["temperature"].append(data["temperature"])

        time.sleep(1)  # Update every second


# Start data collection thread
data_thread = threading.Thread(target=update_data_buffer, daemon=True)
data_thread.start()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "CCC Clock Live Wall Dashboard"

# Define app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "CCC Clock Live Wall Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "#2c3e50",
                        "marginBottom": "30px",
                    },
                ),
                html.P(
                    "Real-time monitoring of CCC Clock demonstration system parameters",
                    style={
                        "textAlign": "center",
                        "color": "#7f8c8d",
                        "fontSize": "18px",
                    },
                ),
            ],
            style={
                "backgroundColor": "#ecf0f1",
                "padding": "20px",
                "marginBottom": "20px",
            },
        ),
        # Control panel
        html.Div(
            [
                html.H3("Control Panel", style={"color": "#34495e"}),
                html.Div(
                    [
                        html.Label("Update Interval (seconds):"),
                        dcc.Slider(
                            id="update-interval-slider",
                            min=0.5,
                            max=10,
                            step=0.5,
                            value=2,
                            marks={i: str(i) for i in range(1, 11)},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.Label("Time Window (minutes):"),
                        dcc.Slider(
                            id="time-window-slider",
                            min=1,
                            max=60,
                            step=1,
                            value=10,
                            marks={i: str(i) for i in [1, 5, 10, 15, 30, 60]},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                    style={"width": "48%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={
                "backgroundColor": "#f8f9fa",
                "padding": "15px",
                "marginBottom": "20px",
            },
        ),
        # Main monitoring plots
        html.Div(
            [
                # SNR and Parity Ratio
                html.Div(
                    [
                        dcc.Graph(id="snr-plot"),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Graph(id="parity-plot"),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
            ]
        ),
        # Live CCC Animation Section
        html.Div(
            [
                html.H3("Live CCC Clock Animation", style={"color": "#34495e", "textAlign": "center"}),
                html.Div(
                    [
                        dcc.Graph(id="ccc-animation-plot"),
                    ],
                    style={"width": "100%", "display": "inline-block"},
                ),
            ],
            style={
                "backgroundColor": "#f8f9fa",
                "padding": "15px",
                "marginTop": "20px",
                "marginBottom": "20px",
            },
        ),
        # Witness channels
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="witness-plot-1"),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Graph(id="witness-plot-2"),
                    ],
                    style={"width": "50%", "display": "inline-block"},
                ),
            ]
        ),
        # System status
        html.Div(
            [
                html.H3("System Status", style={"color": "#34495e"}),
                html.Div(id="system-status", style={"fontSize": "16px"}),
            ],
            style={
                "backgroundColor": "#f8f9fa",
                "padding": "15px",
                "marginTop": "20px",
            },
        ),
        # Auto-refresh component
        dcc.Interval(
            id="interval-component",
            interval=2000,  # Update every 2 seconds
            n_intervals=0,
        ),
    ]
)


def create_ccc_live_animation(n_intervals, timestamps, snr_data, parity_data):
    """Create a live animated visualization of the CCC Clock concept"""
    
    # Create a multi-panel animation showing CCC concept
    fig = go.Figure()
    
    # Get current time for animation phase
    current_time = time.time()
    animation_phase = (current_time * 0.5) % (2 * np.pi)  # Slow rotation
    
    # Create circular path representing the operational loop
    theta = np.linspace(0, 2*np.pi, 100)
    r_outer = 1.0
    r_inner = 0.6
    
    # Outer loop
    x_outer = r_outer * np.cos(theta)
    y_outer = r_outer * np.sin(theta)
    
    # Inner loop  
    x_inner = r_inner * np.cos(theta)
    y_inner = r_inner * np.sin(theta)
    
    # Current position on loop
    current_x = r_outer * np.cos(animation_phase)
    current_y = r_outer * np.sin(animation_phase)
    
    # Add the loop structure
    fig.add_trace(go.Scatter(
        x=x_outer, y=y_outer,
        mode='lines',
        line=dict(color='blue', width=3),
        name='Outer Loop',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=x_inner, y=y_inner,
        mode='lines',
        line=dict(color='red', width=3),
        name='Inner Loop',
        showlegend=True
    ))
    
    # Add connecting bridge (animated)
    bridge_x = [r_inner * np.cos(animation_phase), r_outer * np.cos(animation_phase)]
    bridge_y = [r_inner * np.sin(animation_phase), r_outer * np.sin(animation_phase)]
    
    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_y,
        mode='lines+markers',
        line=dict(color='green', width=4),
        marker=dict(size=8, color='green'),
        name='Θ-Bridge',
        showlegend=True
    ))
    
    # Current position marker
    fig.add_trace(go.Scatter(
        x=[current_x], y=[current_y],
        mode='markers',
        marker=dict(size=12, color='orange', symbol='circle'),
        name='Current Position',
        showlegend=True
    ))
    
    # Add ABBA sequence visualization
    abba_phase = int((animation_phase / (2*np.pi)) * 4) % 4
    abba_labels = ['A₁', 'B₁', 'B₂', 'A₂']
    abba_colors = ['lightblue', 'lightcoral', 'lightcoral', 'lightblue']
    
    # Add text annotation for current ABBA state
    fig.add_annotation(
        x=0, y=0,
        text=f"ABBA Phase: {abba_labels[abba_phase]}",
        showarrow=False,
        font=dict(size=16, color=abba_colors[abba_phase]),
        bgcolor="white",
        bordercolor="black",
        borderwidth=2
    )
    
    # Add signal quality indicators based on actual data
    if snr_data and parity_data:
        latest_snr = snr_data[-1]
        latest_parity = parity_data[-1]
        
        # SNR indicator
        snr_color = 'green' if latest_snr > 20 else 'orange' if latest_snr > 10 else 'red'
        fig.add_trace(go.Scatter(
            x=[1.3], y=[0.8],
            mode='markers+text',
            marker=dict(size=20, color=snr_color),
            text=[f"SNR: {latest_snr:.1f}dB"],
            textposition="middle right",
            name='SNR Status',
            showlegend=False
        ))
        
        # Parity indicator
        parity_color = 'green' if abs(latest_parity - 0.5) < 0.1 else 'orange' if abs(latest_parity - 0.5) < 0.2 else 'red'
        fig.add_trace(go.Scatter(
            x=[1.3], y=[0.5],
            mode='markers+text',
            marker=dict(size=20, color=parity_color),
            text=[f"Parity: {latest_parity:.3f}"],
            textposition="middle right",
            name='Parity Status',
            showlegend=False
        ))
    
    # Layout configuration
    fig.update_layout(
        title=dict(
            text="CCC Clock Live Operation Visualization",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis=dict(
            range=[-1.5, 2.0],
            showgrid=True,
            zeroline=True,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            range=[-1.5, 1.5],
            showgrid=True,
            zeroline=True,
            showticklabels=False,
            title=""
        ),
        height=400,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        plot_bgcolor='rgba(240,240,240,0.5)',
        # Animation transitions
        transition={'duration': 500, 'easing': 'linear'},
        hovermode='closest'
    )
    
    return fig


@callback(
    [
        Output("snr-plot", "figure"),
        Output("parity-plot", "figure"),
        Output("witness-plot-1", "figure"),
        Output("witness-plot-2", "figure"),
        Output("ccc-animation-plot", "figure"),
        Output("system-status", "children"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("time-window-slider", "value"),
    ],
)
def update_plots(n, time_window_minutes):
    """Update all plots with latest data"""

    if len(data_buffer["timestamps"]) == 0:
        # Return empty plots if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Waiting for data...")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Initializing..."

    # Convert to pandas for easier manipulation
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=time_window_minutes)

    # Filter data within time window
    timestamps = list(data_buffer["timestamps"])
    indices = [i for i, t in enumerate(timestamps) if t >= cutoff_time]

    if not indices:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No data in time window")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No recent data"

    filtered_times = [timestamps[i] for i in indices]
    filtered_snr = [list(data_buffer["snr"])[i] for i in indices]
    filtered_parity = [list(data_buffer["parity_ratio"])[i] for i in indices]
    filtered_lo = [list(data_buffer["lo_amplitude"])[i] for i in indices]
    filtered_pol = [list(data_buffer["polarization"])[i] for i in indices]
    filtered_b = [list(data_buffer["b_field"])[i] for i in indices]
    filtered_temp = [list(data_buffer["temperature"])[i] for i in indices]

    # SNR Plot with animation
    snr_fig = go.Figure()
    snr_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=filtered_snr,
            mode="lines+markers",
            name="SNR",
            line=dict(color="#e74c3c", width=2),
            marker=dict(size=4),
            connectgaps=True,
        )
    )
    snr_fig.update_layout(
        title="Demodulation SNR (dB)",
        xaxis_title="Time",
        yaxis_title="SNR (dB)",
        template="plotly_white",
        height=300,
        # Add animation and transitions
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        xaxis=dict(
            autorange=True,
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(
            autorange=True,
            fixedrange=False
        ),
        hovermode='closest'
    )

    # Parity Ratio Plot with animation
    parity_fig = go.Figure()
    parity_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=filtered_parity,
            mode="lines+markers",
            name="Parity Ratio",
            line=dict(color="#3498db", width=2),
            marker=dict(size=4),
            connectgaps=True,
        )
    )
    parity_fig.add_hline(
        y=0.5, line_dash="dash", line_color="gray", annotation_text="Expected: 0.5"
    )
    parity_fig.update_layout(
        title="Parity Ratio",
        xaxis_title="Time",
        yaxis_title="Parity Ratio",
        template="plotly_white",
        height=300,
        yaxis=dict(range=[0, 1]),
        # Add animation and transitions
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        xaxis=dict(
            autorange=True,
            rangeslider=dict(visible=True),
            type="date"
        ),
        hovermode='closest'
    )

    # Witness Channels 1 (LO Amplitude & Polarization) with animation
    witness1_fig = go.Figure()
    witness1_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=filtered_lo,
            mode="lines+markers",
            name="LO Amplitude",
            line=dict(color="#f39c12", width=2),
            marker=dict(size=4),
            yaxis="y",
            connectgaps=True,
        )
    )
    witness1_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=filtered_pol,
            mode="lines+markers",
            name="Polarization (°)",
            line=dict(color="#9b59b6", width=2),
            marker=dict(size=4),
            yaxis="y2",
            connectgaps=True,
        )
    )
    witness1_fig.update_layout(
        title="Witness Channels: LO & Polarization",
        xaxis_title="Time",
        yaxis=dict(title="LO Amplitude", side="left"),
        yaxis2=dict(title="Polarization (°)", side="right", overlaying="y"),
        template="plotly_white",
        height=300,
        # Add animation and transitions
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        xaxis=dict(
            autorange=True,
            type="date"
        ),
        hovermode='closest'
    )

    # Witness Channels 2 (B-field & Temperature) with animation
    witness2_fig = go.Figure()
    witness2_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=[b * 1e9 for b in filtered_b],  # Convert to nT
            mode="lines+markers",
            name="B-field (nT)",
            line=dict(color="#1abc9c", width=2),
            marker=dict(size=4),
            yaxis="y",
            connectgaps=True,
        )
    )
    witness2_fig.add_trace(
        go.Scatter(
            x=filtered_times,
            y=filtered_temp,
            mode="lines+markers",
            name="Temperature (K)",
            line=dict(color="#e67e22", width=2),
            marker=dict(size=4),
            yaxis="y2",
            connectgaps=True,
        )
    )
    witness2_fig.update_layout(
        title="Witness Channels: B-field & Temperature",
        xaxis_title="Time",
        yaxis=dict(title="B-field (nT)", side="left"),
        yaxis2=dict(title="Temperature (K)", side="right", overlaying="y"),
        template="plotly_white",
        height=300,
        # Add animation and transitions
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        xaxis=dict(
            autorange=True,
            type="date"
        ),
        hovermode='closest'
    )

    # CCC Clock Live Animation
    ccc_anim_fig = create_ccc_live_animation(n, filtered_times, filtered_snr, filtered_parity)

    # System Status
    latest_snr = filtered_snr[-1] if filtered_snr else 0
    latest_parity = filtered_parity[-1] if filtered_parity else 0

    status_color = (
        "#27ae60" if latest_snr > 20 and abs(latest_parity - 0.5) < 0.1 else "#e74c3c"
    )
    status_text = "NOMINAL" if status_color == "#27ae60" else "ALERT"

    status_div = html.Div(
        [
            html.Span(
                f"Status: {status_text}",
                style={"color": status_color, "fontWeight": "bold", "fontSize": "20px"},
            ),
            html.Br(),
            html.Span(f"Current SNR: {latest_snr:.1f} dB"),
            html.Br(),
            html.Span(f"Current Parity Ratio: {latest_parity:.3f}"),
            html.Br(),
            html.Span(
                f"Last Update: {filtered_times[-1].strftime('%H:%M:%S')}"
                if filtered_times
                else "No data"
            ),
        ]
    )

    return snr_fig, parity_fig, witness1_fig, witness2_fig, ccc_anim_fig, status_div


@callback(
    Output("interval-component", "interval"),
    Input("update-interval-slider", "value"),
)
def update_interval(interval_seconds):
    """Update refresh interval based on slider"""
    return int(interval_seconds * 1000)


if __name__ == "__main__":
    print("Starting CCC Clock Live Wall Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Press Ctrl+C to stop")

    app.run(debug=False, host="0.0.0.0", port=8050)
