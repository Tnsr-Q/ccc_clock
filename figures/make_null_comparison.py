"""
Figure 6: Exact-Null vs Commutator Floor Comparison
Shows identical edges (exact null) vs heterogeneous edges (commutator floor)
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import sys
sys.path.append('/home/ubuntu/figures')
from style_config import *

def create_null_comparison():
    setup_matplotlib_style()
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=FIGURE_SIZES['panel'])
    
    # Parameter space for residual landscapes
    R1 = np.linspace(1, 10, 100)
    R2 = np.linspace(1, 10, 100)
    R1_grid, R2_grid = np.meshgrid(R1, R2)
    
    # Case 1: Identical edges (exact null)
    # Perfect cancellation - residual should be zero everywhere
    residual_identical = 0.001 * np.ones_like(R1_grid)  # Numerical noise floor
    # Add small random variations to simulate measurement noise
    np.random.seed(42)
    residual_identical += 0.0005 * np.random.randn(*R1_grid.shape)
    
    # Case 2: Heterogeneous edges (commutator floor)
    # Non-zero residual with structure
    R_opt = 5.8
    commutator_floor = 0.01
    residual_heterogeneous = (commutator_floor + 
                             0.1 * ((R1_grid - R_opt)**2 + (R2_grid - R_opt)**2) / 50 +
                             0.005 * np.sin(R1_grid) * np.cos(R2_grid))
    
    # Plot 1: Identical edges residual landscape
    im1 = ax1.contourf(R1_grid, R2_grid, residual_identical, levels=20, 
                      cmap='Blues', alpha=0.8)
    contours1 = ax1.contour(R1_grid, R2_grid, residual_identical, levels=10, 
                           colors='navy', alpha=0.6, linewidths=1)
    ax1.clabel(contours1, inline=True, fontsize=8, fmt='%.4f')
    
    ax1.set_title('Identical Edges: Exact Null', fontsize=14)
    ax1.set_xlabel('R₁ Parameter', fontsize=12)
    ax1.set_ylabel('R₂ Parameter', fontsize=12)
    
    # Add colorbar
    divider1 = make_axes_locatable(ax1)
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    cbar1 = plt.colorbar(im1, cax=cax1)
    cbar1.set_label('Residual', fontsize=10)
    
    # Plot 2: Heterogeneous edges residual landscape
    im2 = ax2.contourf(R1_grid, R2_grid, residual_heterogeneous, levels=20, 
                      cmap='Reds', alpha=0.8)
    contours2 = ax2.contour(R1_grid, R2_grid, residual_heterogeneous, levels=10, 
                           colors='darkred', alpha=0.6, linewidths=1)
    ax2.clabel(contours2, inline=True, fontsize=8, fmt='%.3f')
    
    # Mark optimal point
    ax2.plot(R_opt, R_opt, 'ko', markersize=10, markerfacecolor='yellow', 
            markeredgewidth=2, label='R* = 5.8')
    
    ax2.set_title('Heterogeneous Edges: Commutator Floor', fontsize=14)
    ax2.set_xlabel('R₁ Parameter', fontsize=12)
    ax2.set_ylabel('R₂ Parameter', fontsize=12)
    ax2.legend()
    
    # Add colorbar
    divider2 = make_axes_locatable(ax2)
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    cbar2 = plt.colorbar(im2, cax=cax2)
    cbar2.set_label('Residual', fontsize=10)
    
    # Plot 3: Cross-section comparison
    R_cross = R1  # Cross-section along R1 = R2 diagonal
    residual_identical_cross = np.diag(residual_identical)
    residual_heterogeneous_cross = np.diag(residual_heterogeneous)
    
    ax3.semilogy(R_cross, residual_identical_cross, 'o-', color=CCC_COLORS['primary'], 
                linewidth=3, markersize=4, label='Identical Edges')
    ax3.semilogy(R_cross, residual_heterogeneous_cross, 's-', color=CCC_COLORS['danger'], 
                linewidth=3, markersize=4, label='Heterogeneous Edges')
    
    # Add theoretical lines
    ax3.axhline(0.001, color=CCC_COLORS['primary'], linestyle='--', alpha=0.7,
               label='Noise Floor')
    ax3.axhline(commutator_floor, color=CCC_COLORS['danger'], linestyle='--', alpha=0.7,
               label='Commutator Floor')
    
    ax3.set_xlabel('R Parameter (diagonal)', fontsize=12)
    ax3.set_ylabel('Residual (log scale)', fontsize=12)
    ax3.set_title('Cross-section Comparison', fontsize=14)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_ylim(1e-4, 1e-1)
    
    # Plot 4: Statistical analysis
    # Distribution of residuals
    residuals_identical_flat = residual_identical.flatten()
    residuals_heterogeneous_flat = residual_heterogeneous.flatten()
    
    # Histogram
    bins = np.logspace(-4, -1, 50)
    ax4.hist(residuals_identical_flat, bins=bins, alpha=0.6, color=CCC_COLORS['primary'], 
            label='Identical Edges', density=True)
    ax4.hist(residuals_heterogeneous_flat, bins=bins, alpha=0.6, color=CCC_COLORS['danger'], 
            label='Heterogeneous Edges', density=True)
    
    ax4.set_xscale('log')
    ax4.set_xlabel('Residual Value', fontsize=12)
    ax4.set_ylabel('Probability Density', fontsize=12)
    ax4.set_title('Residual Distributions', fontsize=14)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add statistical annotations
    mean_identical = np.mean(residuals_identical_flat)
    std_identical = np.std(residuals_identical_flat)
    mean_heterogeneous = np.mean(residuals_heterogeneous_flat)
    std_heterogeneous = np.std(residuals_heterogeneous_flat)
    
    stats_text = (f'Statistical Summary:\n'
                 f'Identical: μ = {mean_identical:.4f}, σ = {std_identical:.4f}\n'
                 f'Heterogeneous: μ = {mean_heterogeneous:.3f}, σ = {std_heterogeneous:.3f}\n'
                 f'Ratio: {mean_heterogeneous/mean_identical:.1f}×')
    
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='white', alpha=0.8))
    
    # Add theoretical difference annotations
    ax1.text(0.02, 0.98, 'Theory: Perfect cancellation\nR ≈ 0 (noise limited)', 
            transform=ax1.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    ax2.text(0.02, 0.98, 'Theory: Non-commuting\n[∂/∂R₁, ∂/∂R₂] ≠ 0', 
            transform=ax2.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.8))
    
    # Add arrows showing key differences
    ax3.annotate('Commutator\nFloor', xy=(R_opt, commutator_floor), 
                xytext=(8, 0.05), arrowprops=dict(arrowstyle='->', 
                color=CCC_COLORS['danger'], lw=2), fontsize=11, ha='center')
    
    ax3.annotate('Noise\nFloor', xy=(5, 0.001), xytext=(3, 0.0005),
                arrowprops=dict(arrowstyle='->', color=CCC_COLORS['primary'], lw=2),
                fontsize=11, ha='center')
    
    plt.suptitle('Exact-Null vs Commutator Floor: Theoretical Differences', 
                fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    return fig

if __name__ == "__main__":
    fig = create_null_comparison()
    save_figure(fig, 'null_comparison', ['png', 'svg'])
    plt.close()
