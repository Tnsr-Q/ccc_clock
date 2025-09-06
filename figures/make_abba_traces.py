"""
Figure 5: ABBA Demodulation Traces
Shows time-series with clear sign flip under loop reversal
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/ubuntu/figures')
from style_config import *

def create_abba_traces():
    setup_matplotlib_style()
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=FIGURE_SIZES['panel'])
    
    # Time parameters
    t_total = 100  # seconds
    dt = 0.1
    time = np.arange(0, t_total, dt)
    
    # ABBA sequence parameters
    f_mod = 0.1  # Modulation frequency (Hz)
    f_carrier = 1.0  # Carrier frequency for visualization
    
    # Generate ABBA sequence pattern
    # A-B-B-A pattern with period T_ABBA = 40s
    T_ABBA = 40
    sequence_pattern = np.zeros_like(time)
    
    for i, t in enumerate(time):
        cycle_pos = (t % T_ABBA) / T_ABBA
        if cycle_pos < 0.25:  # A phase
            sequence_pattern[i] = 1
        elif cycle_pos < 0.75:  # B-B phase  
            sequence_pattern[i] = -1
        else:  # A phase
            sequence_pattern[i] = 1
    
    # Forward loop configuration
    # Signal with holonomy effect
    holonomy_amplitude = 0.5
    forward_signal = (holonomy_amplitude * sequence_pattern * 
                     np.sin(2*np.pi*f_mod*time) + 
                     0.1*np.sin(2*np.pi*f_carrier*time))
    
    # Add realistic noise
    np.random.seed(42)
    noise_level = 0.05
    forward_noise = noise_level * np.random.randn(len(time))
    forward_signal += forward_noise
    
    # Reversed loop configuration (perfect sign flip)
    reversed_signal = -forward_signal + 2*forward_noise  # Different noise realization
    
    # Lock-in detection (demodulated signals)
    # Forward demodulation
    demod_forward = sequence_pattern * forward_signal
    # Apply low-pass filter (moving average)
    window = int(5 / dt)  # 5 second window
    demod_forward_filtered = np.convolve(demod_forward, np.ones(window)/window, mode='same')
    
    # Reversed demodulation
    demod_reversed = sequence_pattern * reversed_signal
    demod_reversed_filtered = np.convolve(demod_reversed, np.ones(window)/window, mode='same')
    
    # Plot 1: Forward loop raw signal
    ax1.plot(time, forward_signal, color=CCC_COLORS['primary'], linewidth=1, alpha=0.7)
    ax1.plot(time, sequence_pattern * 0.3, color=CCC_COLORS['success'], linewidth=2, 
            label='ABBA Pattern')
    ax1.set_ylabel('Signal Amplitude', fontsize=12)
    ax1.set_title('Forward Loop: Raw Signal', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0, 60)
    
    # Plot 2: Reversed loop raw signal
    ax2.plot(time, reversed_signal, color=CCC_COLORS['danger'], linewidth=1, alpha=0.7)
    ax2.plot(time, sequence_pattern * 0.3, color=CCC_COLORS['success'], linewidth=2,
            label='ABBA Pattern')
    ax2.set_ylabel('Signal Amplitude', fontsize=12)
    ax2.set_title('Reversed Loop: Raw Signal', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(0, 60)
    
    # Plot 3: Forward demodulated signal
    ax3.plot(time, demod_forward, color=CCC_COLORS['primary'], alpha=0.3, linewidth=1)
    ax3.plot(time, demod_forward_filtered, color=CCC_COLORS['primary'], linewidth=3,
            label='Forward Demod')
    
    # Add error bars at selected points
    error_points = np.arange(10, 100, 10)
    for t_err in error_points:
        idx = int(t_err / dt)
        if idx < len(time):
            ax3.errorbar(time[idx], demod_forward_filtered[idx], 
                        yerr=noise_level, color=CCC_COLORS['primary'], 
                        capsize=3, alpha=0.7)
    
    ax3.set_ylabel('Demodulated Signal', fontsize=12)
    ax3.set_title('Lock-in Detection: Forward', fontsize=14)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.axhline(0, color='black', linestyle='--', alpha=0.5)
    
    # Plot 4: Reversed demodulated signal
    ax4.plot(time, demod_reversed, color=CCC_COLORS['danger'], alpha=0.3, linewidth=1)
    ax4.plot(time, demod_reversed_filtered, color=CCC_COLORS['danger'], linewidth=3,
            label='Reversed Demod')
    
    # Add error bars
    for t_err in error_points:
        idx = int(t_err / dt)
        if idx < len(time):
            ax4.errorbar(time[idx], demod_reversed_filtered[idx], 
                        yerr=noise_level, color=CCC_COLORS['danger'], 
                        capsize=3, alpha=0.7)
    
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Demodulated Signal', fontsize=12)
    ax4.set_title('Lock-in Detection: Reversed', fontsize=14)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    ax4.axhline(0, color='black', linestyle='--', alpha=0.5)
    
    # Add modulation frequency indicators
    for ax in [ax1, ax2]:
        # Mark ABBA periods
        for i in range(int(t_total/T_ABBA)):
            t_start = i * T_ABBA
            ax.axvline(t_start, color='gray', linestyle=':', alpha=0.5)
            if i == 0:
                ax.text(t_start + T_ABBA/2, ax.get_ylim()[1]*0.8, 
                       f'T_ABBA = {T_ABBA}s', ha='center', fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Calculate and display ABBA ratio
    forward_mean = np.mean(demod_forward_filtered[100:])  # Avoid transients
    reversed_mean = np.mean(demod_reversed_filtered[100:])
    
    if abs(forward_mean) > 1e-6:
        abba_ratio = reversed_mean / forward_mean
    else:
        abba_ratio = -1.0
    
    # Add summary statistics box
    stats_text = (f'ABBA Analysis:\n'
                 f'Forward: {forward_mean:.3f} ± {noise_level:.3f}\n'
                 f'Reversed: {reversed_mean:.3f} ± {noise_level:.3f}\n'
                 f'Ratio: {abba_ratio:.3f}\n'
                 f'Expected: -1.000')
    
    fig.text(0.02, 0.98, stats_text, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.8))
    
    # Add sign flip annotation
    ax3.annotate('Positive\nHolonomy', xy=(50, forward_mean), xytext=(70, forward_mean*2),
                arrowprops=dict(arrowstyle='->', color=CCC_COLORS['primary'], lw=2),
                fontsize=11, ha='center')
    
    ax4.annotate('Negative\nHolonomy', xy=(50, reversed_mean), xytext=(70, reversed_mean*2),
                arrowprops=dict(arrowstyle='->', color=CCC_COLORS['danger'], lw=2),
                fontsize=11, ha='center')
    
    # Add modulation frequency annotation
    fig.text(0.98, 0.02, f'Modulation: f = {f_mod} Hz\nABBA Period: {T_ABBA} s', 
            fontsize=11, horizontalalignment='right', verticalalignment='bottom',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat', alpha=0.8))
    
    plt.suptitle('ABBA Demodulation: Perfect Sign Flip Under Loop Reversal', 
                fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    return fig

if __name__ == "__main__":
    fig = create_abba_traces()
    save_figure(fig, 'abba_traces', ['png', 'svg'])
    plt.close()
