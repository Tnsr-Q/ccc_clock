"""
Publication-grade styling configuration for CCC Clock visualization suite
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

# Publication-grade matplotlib configuration
def setup_matplotlib_style():
    """Configure matplotlib for publication-quality figures"""
    plt.style.use('default')
    
    # Font and text settings
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
    mpl.rcParams['font.size'] = 12
    mpl.rcParams['axes.labelsize'] = 14
    mpl.rcParams['axes.titlesize'] = 16
    mpl.rcParams['xtick.labelsize'] = 11
    mpl.rcParams['ytick.labelsize'] = 11
    mpl.rcParams['legend.fontsize'] = 12
    mpl.rcParams['figure.titlesize'] = 18
    
    # Figure quality
    mpl.rcParams['figure.dpi'] = 150
    mpl.rcParams['savefig.dpi'] = 300
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.pad_inches'] = 0.1
    
    # Line and marker settings
    mpl.rcParams['lines.linewidth'] = 2.0
    mpl.rcParams['lines.markersize'] = 6
    mpl.rcParams['axes.linewidth'] = 1.2
    mpl.rcParams['grid.linewidth'] = 0.8
    mpl.rcParams['grid.alpha'] = 0.3
    
    # Color and style
    mpl.rcParams['axes.prop_cycle'] = plt.cycler('color', 
        ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

# Plotly template for 3D and interactive plots
def setup_plotly_template():
    """Configure plotly template for publication quality"""
    template = go.layout.Template()
    
    # Layout settings
    template.layout = go.Layout(
        font=dict(family="Times New Roman", size=12, color="#2E2E2E"),
        title=dict(font=dict(size=16, color="#1A1A1A")),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    # Axis settings
    axis_template = dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        ticks='outside',
        tickwidth=1,
        tickcolor='black',
        tickfont=dict(size=11)
    )
    
    template.layout.xaxis = axis_template
    template.layout.yaxis = axis_template
    
    pio.templates["ccc_publication"] = template
    pio.templates.default = "ccc_publication"

# Color palette for consistency
CCC_COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange  
    'success': '#2ca02c',      # Green
    'danger': '#d62728',       # Red
    'warning': '#ff7f0e',      # Orange
    'info': '#17becf',         # Cyan
    'purple': '#9467bd',       # Purple
    'brown': '#8c564b',        # Brown
    'pink': '#e377c2',         # Pink
    'gray': '#7f7f7f',         # Gray
    'olive': '#bcbd22'         # Olive
}

# Parameter set colors for consistency
PARAM_COLORS = {
    'A': CCC_COLORS['success'],    # Green - best performance
    'B': CCC_COLORS['warning'],    # Orange - medium
    'C': CCC_COLORS['danger']      # Red - worst performance
}

# Scientific notation formatter
def sci_notation(x, pos=None):
    """Format numbers in scientific notation for axes"""
    if x == 0:
        return '0'
    exp = int(np.floor(np.log10(abs(x))))
    coeff = x / (10**exp)
    if exp == 0:
        return f'{coeff:.1f}'
    elif exp == 1:
        return f'{x:.0f}'
    else:
        return f'{coeff:.1f}×10$^{{{exp}}}$'

# Common figure sizes
FIGURE_SIZES = {
    'single': (8, 6),
    'wide': (12, 6), 
    'tall': (8, 10),
    'square': (8, 8),
    'panel': (16, 12)
}

def save_figure(fig, name, formats=['png', 'svg']):
    """Save figure in multiple formats with consistent naming"""
    for fmt in formats:
        filename = f"/home/ubuntu/figures/{name}.{fmt}"
        if hasattr(fig, 'savefig'):  # matplotlib
            fig.savefig(filename, format=fmt, dpi=300, bbox_inches='tight')
        else:  # plotly
            if fmt == 'png':
                fig.write_image(filename, width=1200, height=800, scale=2)
            elif fmt == 'svg':
                fig.write_image(filename, width=1200, height=800, format='svg')
            elif fmt == 'html':
                fig.write_html(filename)
    print(f"Saved {name} in formats: {formats}")

# Initialize styles
setup_matplotlib_style()
setup_plotly_template()
