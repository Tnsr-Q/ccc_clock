# CCC Clock GUI Application

A GUI clock application built with Rust and egui, featuring a digital clock, stopwatch, and timer functionality.

## Features

- **Digital Clock**: Real-time display of current time, date, and day
- **Stopwatch**: Precision timing with start, stop, and reset functionality  
- **Timer**: Countdown timer with minutes and seconds setting
- **Tabbed Interface**: Easy navigation between different modes

## Dependencies

- `eframe` - GUI framework wrapper for egui
- `egui` - Immediate mode GUI library
- `chrono` - Date and time handling

## Building

```bash
# Build debug version
cargo build

# Build release version
cargo build --release

# Run the application
cargo run
```

## Testing

```bash
# Run unit tests
cargo test
```

## Module Structure

The application follows proper Rust module organization:

- `main.rs` - Entry point with module declarations and main function
- `app.rs` - Main application logic and UI structure
- `clock.rs` - Digital clock functionality
- `stopwatch.rs` - Stopwatch functionality  
- `timer.rs` - Timer functionality
- `utils.rs` - Utility functions with time formatting helpers

## Import Structure

The project uses proper import organization:
- External crate imports (`eframe`, `egui`, `chrono`) in files where needed
- Internal module imports using `crate::` paths
- Public module declarations in `main.rs`
- Proper visibility modifiers for cross-module access

## Usage

1. Run `cargo run` to start the application
2. Use the tabs at the top to switch between Clock, Stopwatch, and Timer
3. Clock tab shows current time in a large, easy-to-read format
4. Stopwatch tab provides start/stop/reset controls with centisecond precision
5. Timer tab allows setting countdown timers with visual and text alerts