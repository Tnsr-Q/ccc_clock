"""
Figure 8: Static Explainer Diagram
Shows the modulation and demodulation concept in a clear static format
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle
import sys
sys.path.append('/home/ubuntu/figures')
from style_config import *

def create_static_explainer():
    setup_matplotlib_style()
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Operational Loop (top-left)
    theta = np.linspace(0, 4*np.pi, 200)
    r = 1 + 0.3 * np.sin(3*theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    ax1.plot(x, y, color=CCC_COLORS['primary'], linewidth=4, alpha=0.8)
    
    # Mark key points on the loop
    key_points = [0, 50, 100, 150]
    colors = [CCC_COLORS['success'], CCC_COLORS['warning'], 
              CCC_COLORS['danger'], CCC_COLORS['purple']]
    labels = ['A₁', 'B₁', 'B₂', 'A₂']
    
    for i, (idx, color, label) in enumerate(zip(key_points, colors, labels)):
        ax1.plot(x[idx], y[idx], 'o', markersize=12, color=color, 
                markeredgecolor='black', markeredgewidth=2)
        ax1.text(x[idx]*1.2, y[idx]*1.2, label, fontsize=14, ha='center', 
                va='center', fontweight='bold')
    
    # Add arrows showing direction
    for i in range(0, len(x)-20, 40):
        dx = x[i+10] - x[i]
        dy = y[i+10] - y[i]
        ax1.arrow(x[i], y[i], dx*0.3, dy*0.3, head_width=0.1, 
                 head_length=0.05, fc='black', ec='black', alpha=0.6)
    
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.set_title('Operational Loop: ABBA Sequence', fontsize=16, pad=20)
    ax1.grid(True, alpha=0.3)
    
    # Add holonomy annotation
    ax1.text(0, 0, 'Holonomy\n∮ A·dl ≠ 0', ha='center', va='center', 
            fontsize=12, bbox=dict(boxstyle="round,pad=0.5", 
            facecolor='yellow', alpha=0.8))
    
    # 2. ABBA Sequence Pattern (top-right)
    t = np.linspace(0, 8, 1000)
    abba_pattern = np.zeros_like(t)
    
    # Generate ABBA pattern
    period = 2.0
    for i, time in enumerate(t):
        phase = (time % period) / period
        if phase < 0.25:
            abba_pattern[i] = 1  # A
        elif phase < 0.75:
            abba_pattern[i] = -1  # B
        else:
            abba_pattern[i] = 1  # A
    
    ax2.plot(t, abba_pattern, color=CCC_COLORS['success'], linewidth=4)
    ax2.fill_between(t, 0, abba_pattern, alpha=0.3, color=CCC_COLORS['success'])
    
    # Mark phases
    phase_times = [0.25, 1.25, 1.75, 3.75]
    phase_labels = ['A', 'B', 'B', 'A']
    phase_colors = [CCC_COLORS['success'], CCC_COLORS['warning'], 
                   CCC_COLORS['warning'], CCC_COLORS['success']]
    
    for time, label, color in zip(phase_times, phase_labels, phase_colors):
        ax2.axvline(time, color=color, linestyle='--', alpha=0.7)
        ax2.text(time, 1.2, label, ha='center', fontsize=14, 
                fontweight='bold', color=color)
    
    ax2.set_xlim(0, 4)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_xlabel('Time', fontsize=14)
    ax2.set_ylabel('Phase', fontsize=14)
    ax2.set_title('ABBA Modulation Pattern', fontsize=16, pad=20)
    ax2.grid(True, alpha=0.3)
    
    # Add period annotation
    ax2.annotate('', xy=(0, -1.3), xytext=(2, -1.3),
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax2.text(1, -1.4, 'T_ABBA = 2.0s', ha='center', fontsize=12)
    
    # 3. Signal Modulation (bottom-left)
    # Raw holonomy signal
    holonomy_signal = 0.5 * np.sin(2*np.pi*0.5*t)
    
    # Modulated signal
    modulated_signal = holonomy_signal * abba_pattern
    
    ax3.plot(t, holonomy_signal, '--', color=CCC_COLORS['primary'], 
            linewidth=2, alpha=0.7, label='Raw Holonomy')
    ax3.plot(t, modulated_signal, color=CCC_COLORS['danger'], 
            linewidth=3, label='Modulated Signal')
    
    # Highlight modulation effect
    ax3.fill_between(t, 0, modulated_signal, alpha=0.2, color=CCC_COLORS['danger'])
    
    ax3.set_xlim(0, 4)
    ax3.set_ylim(-1, 1)
    ax3.set_xlabel('Time', fontsize=14)
    ax3.set_ylabel('Signal Amplitude', fontsize=14)
    ax3.set_title('Signal Modulation', fontsize=16, pad=20)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Add modulation annotation
    ax3.text(0.5, 0.7, 'Modulation:\nS_mod = S_hol × ABBA', 
            fontsize=11, bbox=dict(boxstyle="round,pad=0.3", 
            facecolor='lightblue', alpha=0.8))
    
    # 4. Lock-in Detection (bottom-right)
    # Demodulated signal
    demod_signal = modulated_signal * abba_pattern
    
    # Low-pass filtered (running average)
    window = 50
    demod_filtered = np.convolve(demod_signal, np.ones(window)/window, mode='same')
    
    ax4.plot(t, demod_signal, color=CCC_COLORS['gray'], alpha=0.5, 
            linewidth=1, label='Raw Demodulated')
    ax4.plot(t, demod_filtered, color=CCC_COLORS['purple'], 
            linewidth=4, label='Filtered Output')
    
    # Mark final holonomy value
    final_holonomy = demod_filtered[-100:].mean()
    ax4.axhline(final_holonomy, color=CCC_COLORS['success'], 
               linestyle=':', linewidth=2, alpha=0.8)
    ax4.text(3.5, final_holonomy + 0.05, f'Holonomy = {final_holonomy:.3f}', 
            fontsize=12, color=CCC_COLORS['success'], fontweight='bold')
    
    ax4.set_xlim(0, 4)
    ax4.set_ylim(-0.2, 0.8)
    ax4.set_xlabel('Time', fontsize=14)
    ax4.set_ylabel('Demodulated Signal', fontsize=14)
    ax4.set_title('Lock-in Detection & Demodulation', fontsize=16, pad=20)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Add demodulation equation
    ax4.text(0.02, 0.95, 'Demodulation:\nS_out = S_mod × ABBA_ref\nThen: Low-pass filter', 
            transform=ax4.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.8))
    
    # Add overall flow arrows between subplots
    # Arrow from loop to ABBA
    arrow1 = FancyArrowPatch((0.48, 0.75), (0.52, 0.75), 
                            connectionstyle="arc3", 
                            arrowstyle='->', mutation_scale=20, 
                            color='red', linewidth=3,
                            transform=fig.transFigure)
    fig.patches.append(arrow1)
    
    # Arrow from ABBA to modulation
    arrow2 = FancyArrowPatch((0.75, 0.52), (0.25, 0.48), 
                            connectionstyle="arc3,rad=0.3", 
                            arrowstyle='->', mutation_scale=20, 
                            color='red', linewidth=3,
                            transform=fig.transFigure)
    fig.patches.append(arrow2)
    
    # Arrow from modulation to detection
    arrow3 = FancyArrowPatch((0.48, 0.25), (0.52, 0.25), 
                            connectionstyle="arc3", 
                            arrowstyle='->', mutation_scale=20, 
                            color='red', linewidth=3,
                            transform=fig.transFigure)
    fig.patches.append(arrow3)
    
    # Add main title and summary
    fig.suptitle('CCC Clock: Modulation & Demodulation Concept', 
                fontsize=20, y=0.95, fontweight='bold')
    
    # Add summary box
    summary_text = ('Key Concept:\n'
                   '1. Operational loop creates holonomy\n'
                   '2. ABBA sequence modulates signal\n'
                   '3. Lock-in detection extracts holonomy\n'
                   '4. Sign flip under loop reversal')
    
    fig.text(0.02, 0.02, summary_text, fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.9))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90, bottom=0.15)
    
    return fig

if __name__ == "__main__":
    fig = create_static_explainer()
    save_figure(fig, 'ccc_explainer', ['png', 'svg'])
    plt.close()
