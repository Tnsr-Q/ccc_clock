"""
Figure 8: Animated Explainer
20-30 second animation showing modulation + demodulation concept
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyArrowPatch
import sys
sys.path.append('/home/ubuntu/figures')
from style_config import *

def create_animated_explainer():
    setup_matplotlib_style()
    
    # Animation parameters
    duration = 25  # seconds
    fps = 10
    n_frames = duration * fps
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Layout: 2x2 grid
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=1)  # Operational loop
    ax2 = plt.subplot2grid((2, 3), (0, 1), colspan=1)  # ABBA sequence
    ax3 = plt.subplot2grid((2, 3), (0, 2), colspan=1)  # Signal modulation
    ax4 = plt.subplot2grid((2, 3), (1, 0), colspan=3)  # Lock-in detection
    
    # Initialize plots
    def init_plots():
        # Operational loop (ax1)
        ax1.set_xlim(-2, 2)
        ax1.set_ylim(-2, 2)
        ax1.set_aspect('equal')
        ax1.set_title('Operational Loop', fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # ABBA sequence (ax2)
        ax2.set_xlim(0, 8)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_title('ABBA Sequence', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Phase')
        
        # Signal modulation (ax3)
        ax3.set_xlim(0, 8)
        ax3.set_ylim(-2, 2)
        ax3.set_title('Signal Modulation', fontsize=14)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Amplitude')
        
        # Lock-in detection (ax4)
        ax4.set_xlim(0, 8)
        ax4.set_ylim(-1, 1)
        ax4.set_title('Lock-in Detection & Demodulation', fontsize=14)
        ax4.grid(True, alpha=0.3)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Demodulated Signal')
    
    init_plots()
    
    # Animation data
    t_anim = np.linspace(0, 8, n_frames)
    
    # Operational loop path
    theta_loop = np.linspace(0, 4*np.pi, 100)
    r_loop = 1 + 0.3 * np.sin(3*theta_loop)
    x_loop = r_loop * np.cos(theta_loop)
    y_loop = r_loop * np.sin(theta_loop)
    
    # ABBA pattern
    def abba_pattern(t):
        """Generate ABBA sequence pattern"""
        period = 2.0
        phase = (t % period) / period
        if phase < 0.25:
            return 1  # A
        elif phase < 0.75:
            return -1  # B
        else:
            return 1  # A
    
    # Initialize line objects
    loop_line, = ax1.plot([], [], 'b-', linewidth=3, alpha=0.7)
    loop_point, = ax1.plot([], [], 'ro', markersize=10)
    loop_trail, = ax1.plot([], [], 'r-', linewidth=2, alpha=0.5)
    
    abba_line, = ax2.plot([], [], 'g-', linewidth=3)
    abba_points, = ax2.plot([], [], 'go', markersize=6)
    
    signal_line, = ax3.plot([], [], 'b-', linewidth=2, label='Raw Signal')
    modulated_line, = ax3.plot([], [], 'r-', linewidth=2, label='Modulated')
    
    demod_line, = ax4.plot([], [], 'purple', linewidth=3, label='Demodulated')
    demod_avg, = ax4.plot([], [], 'orange', linewidth=4, label='Running Average')
    
    # Text annotations
    phase_text = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=12,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    holonomy_text = ax4.text(0.02, 0.95, '', transform=ax4.transAxes, fontsize=12,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))
    
    def animate(frame):
        current_time = t_anim[frame]
        
        # 1. Operational loop animation
        # Show full loop path
        loop_line.set_data(x_loop, y_loop)
        
        # Current position on loop
        loop_progress = (current_time / 8) * len(x_loop)
        current_idx = int(loop_progress) % len(x_loop)
        
        loop_point.set_data([x_loop[current_idx]], [y_loop[current_idx]])
        
        # Trail showing recent path
        trail_length = 20
        trail_start = max(0, current_idx - trail_length)
        trail_end = current_idx + 1
        if trail_end > len(x_loop):
            # Handle wrap-around
            trail_x = np.concatenate([x_loop[trail_start:], x_loop[:trail_end-len(x_loop)]])
            trail_y = np.concatenate([y_loop[trail_start:], y_loop[:trail_end-len(y_loop)]])
        else:
            trail_x = x_loop[trail_start:trail_end]
            trail_y = y_loop[trail_start:trail_end]
        
        loop_trail.set_data(trail_x, trail_y)
        
        # 2. ABBA sequence animation
        t_seq = np.linspace(0, current_time, max(1, int(current_time * 10)))
        abba_seq = [abba_pattern(t) for t in t_seq]
        
        abba_line.set_data(t_seq, abba_seq)
        
        # Current ABBA points
        if len(t_seq) > 0:
            current_abba = abba_pattern(current_time)
            abba_points.set_data([current_time], [current_abba])
            
            # Update phase text
            phase_name = 'A' if current_abba > 0 else 'B'
            phase_text.set_text(f'Current Phase: {phase_name}')
        
        # 3. Signal modulation
        t_signal = np.linspace(0, current_time, max(1, int(current_time * 20)))
        
        # Raw signal (holonomy effect)
        holonomy_signal = 0.5 * np.sin(2 * np.pi * 0.5 * t_signal)
        
        # Modulated signal (ABBA pattern applied)
        modulated_signal = []
        for t in t_signal:
            mod_factor = abba_pattern(t)
            modulated_signal.append(holonomy_signal[len(modulated_signal)] * mod_factor)
        
        signal_line.set_data(t_signal, holonomy_signal)
        modulated_line.set_data(t_signal, modulated_signal)
        
        # 4. Lock-in detection
        if len(t_signal) > 1:
            # Demodulated signal (multiply by reference)
            demod_signal = []
            for i, t in enumerate(t_signal):
                ref_signal = abba_pattern(t)
                demod_val = modulated_signal[i] * ref_signal
                demod_signal.append(demod_val)
            
            demod_line.set_data(t_signal, demod_signal)
            
            # Running average (low-pass filter)
            if len(demod_signal) > 10:
                window = min(20, len(demod_signal)//2)
                demod_avg_vals = []
                for i in range(len(demod_signal)):
                    start_idx = max(0, i - window)
                    avg_val = np.mean(demod_signal[start_idx:i+1])
                    demod_avg_vals.append(avg_val)
                
                demod_avg.set_data(t_signal, demod_avg_vals)
                
                # Update holonomy text
                if len(demod_avg_vals) > 0:
                    final_holonomy = demod_avg_vals[-1]
                    holonomy_text.set_text(f'Holonomy Signal: {final_holonomy:.3f}')
        
        return (loop_line, loop_point, loop_trail, abba_line, abba_points,
                signal_line, modulated_line, demod_line, demod_avg, 
                phase_text, holonomy_text)
    
    # Add legends
    ax3.legend(loc='upper right')
    ax4.legend(loc='upper right')
    
    # Add overall title with animation progress
    def update_title(frame):
        progress = (frame / n_frames) * 100
        fig.suptitle(f'CCC Clock: Modulation & Demodulation Concept (Progress: {progress:.0f}%)', 
                    fontsize=16)
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, frames=n_frames, interval=1000/fps, 
                                  blit=False, repeat=True)
    
    # Add progress indicator
    def animate_with_title(frame):
        update_title(frame)
        return animate(frame)
    
    anim = animation.FuncAnimation(fig, animate_with_title, frames=n_frames, 
                                  interval=1000/fps, blit=False, repeat=True)
    
    plt.tight_layout()
    
    return anim, fig

def save_animation():
    """Save animation in multiple formats"""
    anim, fig = create_animated_explainer()
    
    # Check available writers
    print("Available writers:", list(animation.writers.list()))
    
    try:
        # Save as GIF (most reliable)
        print("Saving animation as GIF...")
        anim.save('/home/ubuntu/figures/ccc_explainer.gif', writer='pillow', fps=8)
        print("GIF saved successfully!")
    except Exception as e:
        print(f"GIF save failed: {e}")
    
    try:
        # Try to save as MP4 if ffmpeg is available
        if 'ffmpeg' in animation.writers.list():
            print("Saving animation as MP4...")
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=10, metadata=dict(artist='CCC Clock System'), bitrate=1800)
            anim.save('/home/ubuntu/figures/ccc_explainer.mp4', writer=writer)
            print("MP4 saved successfully!")
        else:
            print("ffmpeg not available, skipping MP4")
    except Exception as e:
        print(f"MP4 save failed: {e}")
    
    # Save static frames as backup
    try:
        print("Saving key frames as static images...")
        key_frames = [0, 50, 100, 150, 200]  # Sample frames
        for i, frame in enumerate(key_frames):
            if frame < anim._func(0).__len__():  # Check if frame exists
                fig.savefig(f'/home/ubuntu/figures/animation_frame_{i:02d}.png', 
                           dpi=150, bbox_inches='tight')
        print("Static frames saved!")
    except Exception as e:
        print(f"Static frame save failed: {e}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_animation()
