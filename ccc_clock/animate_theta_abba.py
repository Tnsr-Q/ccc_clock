
#!/usr/bin/env python3
"""
CCC Clock Θ-Loop + ABBA Animation Generator

Creates a 20-30 second animation showing:
- Θ-loop geometry in operational space
- ABBA sequence timing and modulation
- Signal demodulation and lock-in detection
- Clear visualization of the measurement principle
"""

import os

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Set up the figure and animation parameters
plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(16, 9))
fig.suptitle('CCC Clock: Θ-Loop Geometry and ABBA Protocol', fontsize=20, fontweight='bold')

# Animation parameters
duration = 10  # seconds (reduced for faster generation)
fps = 15       # reduced fps for faster generation
total_frames = duration * fps

# Create subplots
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
ax_3d = fig.add_subplot(gs[0, 0], projection='3d')
ax_theta = fig.add_subplot(gs[0, 1])
ax_abba = fig.add_subplot(gs[0, 2])
ax_signal = fig.add_subplot(gs[1, :2])
ax_demod = fig.add_subplot(gs[1, 2])

def setup_plots():
    """Initialize all subplot configurations"""
    
    # 3D Θ-loop visualization
    ax_3d.set_title('Θ-Loop Geometry', fontsize=14, fontweight='bold')
    ax_3d.set_xlabel('X (mm)')
    ax_3d.set_ylabel('Y (mm)')
    ax_3d.set_zlabel('Z (mm)')
    ax_3d.set_xlim([-15, 15])
    ax_3d.set_ylim([-15, 15])
    ax_3d.set_zlim([-5, 5])
    
    # Θ-loop cross-section
    ax_theta.set_title('Θ-Loop Cross-Section', fontsize=14, fontweight='bold')
    ax_theta.set_xlabel('Position (mm)')
    ax_theta.set_ylabel('Height (mm)')
    ax_theta.set_xlim([-20, 20])
    ax_theta.set_ylim([-15, 15])
    ax_theta.set_aspect('equal')
    ax_theta.grid(True, alpha=0.3)
    
    # ABBA sequence timing
    ax_abba.set_title('ABBA Protocol Timing', fontsize=14, fontweight='bold')
    ax_abba.set_xlabel('Time (s)')
    ax_abba.set_ylabel('Phase State')
    ax_abba.set_xlim([0, 4])
    ax_abba.set_ylim([-0.5, 3.5])
    ax_abba.set_yticks([0, 1, 2, 3])
    ax_abba.set_yticklabels(['A₁', 'B₁', 'B₂', 'A₂'])
    ax_abba.grid(True, alpha=0.3)
    
    # Signal evolution
    ax_signal.set_title('Signal Evolution and Demodulation', fontsize=14, fontweight='bold')
    ax_signal.set_xlabel('Time (s)')
    ax_signal.set_ylabel('Signal Amplitude')
    ax_signal.grid(True, alpha=0.3)
    
    # Demodulated output
    ax_demod.set_title('Lock-in Detection', fontsize=14, fontweight='bold')
    ax_demod.set_xlabel('Frequency (Hz)')
    ax_demod.set_ylabel('Power (dB)')
    ax_demod.grid(True, alpha=0.3)

def create_theta_loop_3d():
    """Create 3D Θ-loop geometry"""
    # Parameters for Θ-loop
    R_major = 10  # Major radius (mm)
    R_minor = 2   # Minor radius (mm)
    
    # Create Θ-loop parametric equations
    u = np.linspace(0, 2*np.pi, 100)
    v = np.linspace(0, 2*np.pi, 50)
    
    # Torus equations with Θ-loop modification
    x_loop = []
    y_loop = []
    z_loop = []
    
    for i, u_val in enumerate(u):
        # Create the characteristic Θ-shape
        if i < len(u)//2:
            # First loop
            x = (R_major + R_minor * np.cos(v)) * np.cos(u_val)
            y = (R_major + R_minor * np.cos(v)) * np.sin(u_val)
            z = R_minor * np.sin(v)
        else:
            # Second loop (twisted)
            x = (R_major + R_minor * np.cos(v)) * np.cos(u_val + np.pi)
            y = (R_major + R_minor * np.cos(v)) * np.sin(u_val + np.pi)
            z = R_minor * np.sin(v) * np.cos(u_val - np.pi)
        
        x_loop.extend(x)
        y_loop.extend(y)
        z_loop.extend(z)
    
    return np.array(x_loop), np.array(y_loop), np.array(z_loop)

def create_abba_sequence(t):
    """Generate ABBA sequence state at time t"""
    cycle_time = 4.0  # Total cycle time in seconds
    t_mod = t % cycle_time
    
    if t_mod < 1.0:
        return 0, 'A₁'  # First A state
    elif t_mod < 2.0:
        return 1, 'B₁'  # First B state
    elif t_mod < 3.0:
        return 2, 'B₂'  # Second B state
    else:
        return 3, 'A₂'  # Second A state

def generate_ccc_signal(t, abba_state):
    """Generate CCC signal with ABBA modulation"""
    # Base frequencies
    f_carrier = 50  # Carrier frequency (Hz)
    f_mod = 0.25    # ABBA modulation frequency (Hz)
    
    # Phase shifts for ABBA states
    phase_shifts = [0, np.pi/2, np.pi/2, 0]  # A₁, B₁, B₂, A₂
    
    # Generate signal
    carrier = np.sin(2 * np.pi * f_carrier * t)
    modulation = np.sin(2 * np.pi * f_mod * t + phase_shifts[abba_state])
    
    # Add CCC-specific effects
    ccc_effect = 0.1 * np.sin(2 * np.pi * 0.1 * t)  # Slow CCC modulation
    noise = 0.05 * np.random.randn(len(t) if hasattr(t, '__len__') else 1)
    
    signal = carrier * (1 + 0.3 * modulation + ccc_effect) + noise
    return signal

def animate_frame(frame):
    """Animation function for each frame"""
    # Clear all axes
    ax_3d.clear()
    ax_theta.clear()
    ax_abba.clear()
    ax_signal.clear()
    ax_demod.clear()
    
    # Re-setup plots
    setup_plots()
    
    # Current time
    current_time = frame / fps
    
    # 1. 3D Θ-loop visualization
    x_loop, y_loop, z_loop = create_theta_loop_3d()
    
    # Animate the loop construction
    progress = (frame % (fps * 2)) / (fps * 2)  # 2-second cycle
    n_points = int(progress * len(x_loop))
    
    if n_points > 0:
        ax_3d.plot(x_loop[:n_points], y_loop[:n_points], z_loop[:n_points], 
                  'b-', linewidth=3, alpha=0.8)
        
        # Add current position marker
        if n_points < len(x_loop):
            ax_3d.scatter([x_loop[n_points-1]], [y_loop[n_points-1]], [z_loop[n_points-1]], 
                         c='red', s=100, alpha=1.0)
    
    # Add coordinate system
    ax_3d.quiver(0, 0, 0, 10, 0, 0, color='red', alpha=0.6, arrow_length_ratio=0.1)
    ax_3d.quiver(0, 0, 0, 0, 10, 0, color='green', alpha=0.6, arrow_length_ratio=0.1)
    ax_3d.quiver(0, 0, 0, 0, 0, 5, color='blue', alpha=0.6, arrow_length_ratio=0.1)
    
    ax_3d.set_title('Θ-Loop Geometry', fontsize=14, fontweight='bold')
    ax_3d.set_xlabel('X (mm)')
    ax_3d.set_ylabel('Y (mm)')
    ax_3d.set_zlabel('Z (mm)')
    
    # 2. Θ-loop cross-section
    theta = np.linspace(0, 2*np.pi, 100)
    r_outer = 12
    r_inner = 8
    
    # Outer loop
    x_outer = r_outer * np.cos(theta)
    y_outer = r_outer * np.sin(theta)
    ax_theta.plot(x_outer, y_outer, 'b-', linewidth=3, label='Outer loop')
    
    # Inner loop
    x_inner = r_inner * np.cos(theta)
    y_inner = r_inner * np.sin(theta)
    ax_theta.plot(x_inner, y_inner, 'r-', linewidth=3, label='Inner loop')
    
    # Connection (Θ-bridge)
    bridge_angle = current_time * 0.5  # Rotating bridge
    x_bridge = [r_inner * np.cos(bridge_angle), r_outer * np.cos(bridge_angle)]
    y_bridge = [r_inner * np.sin(bridge_angle), r_outer * np.sin(bridge_angle)]
    ax_theta.plot(x_bridge, y_bridge, 'g-', linewidth=4, label='Θ-bridge')
    
    ax_theta.legend()
    ax_theta.set_aspect('equal')
    
    # 3. ABBA sequence timing
    time_window = 8.0
    t_abba = np.linspace(current_time - time_window/2, current_time + time_window/2, 1000)
    
    abba_states = []
    for t in t_abba:
        state, _ = create_abba_sequence(t)
        abba_states.append(state)
    
    ax_abba.plot(t_abba, abba_states, 'b-', linewidth=2)
    ax_abba.axvline(current_time, color='red', linestyle='--', linewidth=2, label='Current time')
    
    # Current state indicator
    current_state, current_label = create_abba_sequence(current_time)
    ax_abba.scatter([current_time], [current_state], c='red', s=100, zorder=5)
    ax_abba.text(current_time + 0.2, current_state, current_label, 
                fontsize=12, fontweight='bold', color='red')
    
    ax_abba.set_xlim([current_time - time_window/2, current_time + time_window/2])
    ax_abba.legend()
    
    # 4. Signal evolution
    t_signal = np.linspace(current_time - 2, current_time + 0.1, 1000)
    
    signals = []
    for t in t_signal:
        state, _ = create_abba_sequence(t)
        signal = generate_ccc_signal(np.array([t]), state)
        signals.append(signal[0])
    
    ax_signal.plot(t_signal, signals, 'b-', linewidth=1.5, alpha=0.8, label='Raw signal')
    
    # Add envelope
    envelope = np.abs(np.array(signals))
    ax_signal.plot(t_signal, envelope, 'r-', linewidth=2, alpha=0.7, label='Envelope')
    ax_signal.plot(t_signal, -envelope, 'r-', linewidth=2, alpha=0.7)
    
    ax_signal.axvline(current_time, color='red', linestyle='--', alpha=0.7)
    ax_signal.set_xlim([current_time - 2, current_time + 0.1])
    ax_signal.legend()
    
    # 5. Lock-in detection (frequency domain)
    # Simulate lock-in amplifier output
    frequencies = np.linspace(0, 100, 500)
    
    # Create realistic lock-in spectrum
    signal_freq = 50  # Signal frequency
    noise_floor = -60
    signal_peak = -10
    
    spectrum = noise_floor + 10 * np.random.randn(len(frequencies))
    
    # Add signal peak
    signal_idx = np.argmin(np.abs(frequencies - signal_freq))
    spectrum[signal_idx-5:signal_idx+5] += signal_peak - noise_floor
    
    # Add harmonics
    for harmonic in [2, 3]:
        harm_freq = signal_freq * harmonic
        if harm_freq < frequencies[-1]:
            harm_idx = np.argmin(np.abs(frequencies - harm_freq))
            spectrum[harm_idx-2:harm_idx+2] += (signal_peak - noise_floor) / harmonic
    
    ax_demod.plot(frequencies, spectrum, 'b-', linewidth=1.5)
    ax_demod.axvline(signal_freq, color='red', linestyle='--', linewidth=2, 
                    label=f'Signal @ {signal_freq} Hz')
    ax_demod.set_ylim([noise_floor - 10, signal_peak + 10])
    ax_demod.legend()
    
    # Add frame counter
    fig.text(0.02, 0.02, f'Frame: {frame}/{total_frames} | Time: {current_time:.1f}s', 
             fontsize=10, alpha=0.7)

# Create animation
print("Creating CCC Clock Θ-Loop + ABBA Animation...")
print(f"Duration: {duration}s at {fps} FPS = {total_frames} frames")

# Setup initial plots
setup_plots()

# Create animation
anim = animation.FuncAnimation(fig, animate_frame, frames=total_frames, 
                             interval=1000/fps, blit=False, repeat=True)

# Save animation
output_path = os.path.join(os.path.dirname(__file__), 'figures', 'theta_abba_animation.mp4')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(f"Saving animation to: {output_path}")
print("This may take several minutes...")

# Use ffmpeg writer for high quality
Writer = animation.writers['ffmpeg']
writer = Writer(fps=fps, metadata=dict(artist='CCC Clock Demo'), bitrate=1800)

try:
    anim.save(output_path, writer=writer, dpi=100)
    print(f"Animation saved successfully: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
except Exception as e:
    print(f"Error saving animation: {e}")
    print("Trying alternative writer...")
    
    # Fallback to pillow writer
    try:
        anim.save(output_path.replace('.mp4', '.gif'), writer='pillow', fps=fps//2)
        print(f"Animation saved as GIF: {output_path.replace('.mp4', '.gif')}")
    except Exception as e2:
        print(f"Error with fallback writer: {e2}")

plt.close()
print("Animation generation complete!")
