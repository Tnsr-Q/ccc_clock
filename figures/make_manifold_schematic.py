"""
Figure 1: 14-D Operational Manifold Schematic
Shows the operational manifold with rulers/protractors and Θ-loop
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
from matplotlib.collections import LineCollection
import sys
sys.path.append('/home/ubuntu/figures')
from style_config import *

def create_manifold_schematic():
    setup_matplotlib_style()
    fig, ax = plt.subplots(1, 1, figsize=FIGURE_SIZES['wide'])
    
    # Create coordinate system in (ln r*, θ) space
    ln_r_range = np.linspace(-2, 2, 100)
    theta_range = np.linspace(0, 2*np.pi, 100)
    
    # Draw coordinate grid
    for ln_r in np.linspace(-2, 2, 9):
        ax.axvline(ln_r, color='lightgray', alpha=0.5, linewidth=0.5)
    for theta in np.linspace(0, 2*np.pi, 13):
        ax.axhline(theta, color='lightgray', alpha=0.5, linewidth=0.5)
    
    # Draw the Θ-only loop path (closed loop in operational space)
    theta_loop = np.linspace(0, 2*np.pi, 100)
    ln_r_loop = 0.5 * np.sin(3*theta_loop) + 0.2 * np.cos(5*theta_loop)
    
    # Main loop path
    ax.plot(ln_r_loop, theta_loop, color=CCC_COLORS['primary'], linewidth=4, 
            label='Θ-only Loop Path', zorder=10)
    
    # Add arrow indicators for loop direction
    n_arrows = 8
    for i in range(n_arrows):
        idx = int(i * len(theta_loop) / n_arrows)
        if idx < len(theta_loop) - 5:
            dx = ln_r_loop[idx+5] - ln_r_loop[idx]
            dy = theta_loop[idx+5] - theta_loop[idx]
            ax.arrow(ln_r_loop[idx], theta_loop[idx], dx*0.3, dy*0.3,
                    head_width=0.1, head_length=0.05, fc=CCC_COLORS['primary'], 
                    ec=CCC_COLORS['primary'], zorder=11)
    
    # Add rulers and protractors to show measurement geometry
    # Ruler along ln r* axis
    ruler_y = -0.5
    ruler_x = np.linspace(-1.5, 1.5, 7)
    for x in ruler_x:
        ax.plot([x, x], [ruler_y-0.05, ruler_y+0.05], 'k-', linewidth=1)
    ax.plot([-1.5, 1.5], [ruler_y, ruler_y], 'k-', linewidth=2)
    ax.text(0, ruler_y-0.3, 'ln r* ruler', ha='center', fontsize=10)
    
    # Protractor for θ measurements
    protractor_center = (-1.5, np.pi)
    protractor_radius = 0.4
    protractor_angles = np.linspace(0, 2*np.pi, 13)
    for angle in protractor_angles:
        x_end = protractor_center[0] + protractor_radius * np.cos(angle)
        y_end = protractor_center[1] + protractor_radius * np.sin(angle)
        ax.plot([protractor_center[0], x_end], [protractor_center[1], y_end], 
                'k-', linewidth=1, alpha=0.7)
    
    # Protractor arc
    arc_angles = np.linspace(0, 2*np.pi, 100)
    arc_x = protractor_center[0] + protractor_radius * np.cos(arc_angles)
    arc_y = protractor_center[1] + protractor_radius * np.sin(arc_angles)
    ax.plot(arc_x, arc_y, 'k-', linewidth=2)
    ax.text(protractor_center[0]-0.7, protractor_center[1], 'θ protractor', 
            ha='center', fontsize=10, rotation=90)
    
    # Add curvature visualization - field lines showing non-commuting geometry
    X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(0, 2*np.pi, 20))
    # Curvature field (simplified representation)
    U = 0.1 * np.sin(Y) * np.exp(-X**2/2)
    V = 0.1 * np.cos(X) * (1 + 0.3*np.sin(2*Y))
    
    ax.quiver(X, Y, U, V, alpha=0.3, scale=2, color='gray', width=0.002)
    
    # Highlight key points
    # Starting point
    ax.plot(ln_r_loop[0], theta_loop[0], 'o', markersize=10, 
            color=CCC_COLORS['success'], label='Loop Start', zorder=12)
    
    # Point of maximum curvature
    max_curve_idx = np.argmax(np.abs(np.gradient(np.gradient(ln_r_loop))))
    ax.plot(ln_r_loop[max_curve_idx], theta_loop[max_curve_idx], 's', 
            markersize=10, color=CCC_COLORS['danger'], 
            label='Max Curvature', zorder=12)
    
    # Add holonomy measurement annotation
    ax.annotate('Holonomy\nMeasurement', 
                xy=(ln_r_loop[max_curve_idx], theta_loop[max_curve_idx]),
                xytext=(1.2, 4.5), fontsize=12,
                arrowprops=dict(arrowstyle='->', color=CCC_COLORS['danger'], lw=2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor=CCC_COLORS['danger'], alpha=0.8))
    
    # Add information complexity indicators
    # Complexity "heat map" background
    complexity_x = np.linspace(-2, 2, 50)
    complexity_y = np.linspace(0, 2*np.pi, 50)
    X_comp, Y_comp = np.meshgrid(complexity_x, complexity_y)
    complexity = np.exp(-(X_comp**2 + (Y_comp-np.pi)**2)/2) * (1 + 0.5*np.sin(3*Y_comp))
    
    im = ax.contourf(X_comp, Y_comp, complexity, levels=10, alpha=0.2, 
                     cmap='viridis', zorder=1)
    
    # Add colorbar for complexity
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, aspect=20)
    cbar.set_label('Information Complexity', fontsize=12)
    
    # Formatting
    ax.set_xlabel('ln r* (Operational Radius)', fontsize=14)
    ax.set_ylabel('θ (Operational Angle)', fontsize=14)
    ax.set_title('14-D Operational Manifold: Θ-only Loop in (ln r*, θ) Space', 
                fontsize=16, pad=20)
    
    # Set axis limits and ticks
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-0.8, 2*np.pi + 0.5)
    ax.set_yticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    ax.set_yticklabels(['0', 'π/2', 'π', '3π/2', '2π'])
    
    # Add legend
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Add text box with key information
    textstr = 'Non-commuting geometry:\n[∂/∂r*, ∂/∂θ] ≠ 0\n\nHolonomy ∝ ∮ A·dl\nCurvature → Observable'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    fig = create_manifold_schematic()
    save_figure(fig, 'manifold_schematic', ['png', 'svg'])
    plt.close()
