"""
CCC Clock Dashboard - Live monitoring system for CCC parameters
Starts on http://localhost:8050
"""

import dash
from dash import html, dcc
import plotly.graph_objs as go
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from metrology import PARAMETER_SETS
except ImportError:
    # Fallback if import fails
    PARAMETER_SETS = {
        'A': {'detection_time_hours': 0.8, 'description': 'Fast detection'},
        'B': {'detection_time_hours': 13.1, 'description': 'Balanced approach'}, 
        'C': {'detection_time_hours': 1000, 'description': 'Conservative'}
    }

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("CCC Clock Dashboard", style={'textAlign': 'center'}),
    html.P("Live monitoring system for CCC clock parameters", style={'textAlign': 'center'}),
    
    html.Div([
        html.H3("Parameter Sets"),
        html.Div([
            html.P(f"Set {name}: {params['description']} ({params['detection_time_hours']}h)")
            for name, params in PARAMETER_SETS.items()
        ])
    ]),
    
    dcc.Graph(
        id='parameter-chart',
        figure={
            'data': [
                go.Bar(
                    x=list(PARAMETER_SETS.keys()),
                    y=[params['detection_time_hours'] for params in PARAMETER_SETS.values()],
                    name='Detection Time (hours)'
                )
            ],
            'layout': go.Layout(
                title='CCC Parameter Sets - Detection Time',
                xaxis={'title': 'Parameter Set'},
                yaxis={'title': 'Detection Time (hours)'}
            )
        }
    )
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)