# 🔬 CCC Clock Source Code

This directory contains the source code for the CCC Clock Demonstration System, organized by language and purpose.

## Directory Structure

### 📊 Python Analysis Scripts (`analysis/`)
Python modules for specialized analysis and experimentation.

- **[experiments_bridge_null.py](analysis/experiments_bridge_null.py)** - Bridge null hypothesis experiments and validation

### 🦀 Rust Components (`.rs` files)
Core system components written in Rust for performance-critical operations.

| Component | Description | Purpose |
|-----------|-------------|---------|
| **[main.rs](main.rs)** | Main entry point | Application initialization |
| **[app.rs](app.rs)** | Application logic | Core application framework |
| **[clock.rs](clock.rs)** | Clock operations | Timing and synchronization |
| **[timer.rs](timer.rs)** | Timer functionality | Precision timing operations |
| **[stopwatch.rs](stopwatch.rs)** | Stopwatch utilities | Measurement timing |
| **[utils.rs](utils.rs)** | Utility functions | Common helper functions |

### 🐍 Core Python Package
The main Python package is located in `ccc_clock/src/` with the following modules:

- **metrology.py** - Core CCC theory implementation and parameter sets
- **bridge_ccc.py** - Bridge analysis (R* = 5.80 optimization)
- **protocol.py** - ABBA demodulation protocol
- **bridge_null_utils.py** - Bridge null hypothesis utilities

## Development Guidelines

### Adding New Analysis Scripts
1. Place Python analysis scripts in `src/analysis/`
2. Follow the existing naming convention: `experiments_*.py` or `analysis_*.py`
3. Add appropriate docstrings and type hints
4. Include unit tests in the corresponding test directory

### Rust Development
1. Follow Rust conventions and use `cargo` for building
2. Add new modules to the appropriate section in `Cargo.toml`
3. Ensure cross-platform compatibility

### Integration
- Python scripts can import from the main `ccc_clock` package
- Rust components are compiled separately and can interface with Python via FFI if needed

## Usage Examples

### Python Analysis Scripts
```bash
# Run experiments from repository root
cd /path/to/ccc_clock
python src/analysis/experiments_bridge_null.py
```

### Rust Components
```bash
# Build and run Rust components
cargo build --release
cargo run
```

## Dependencies

### Python
- Requires packages listed in `ccc_clock/requirements.txt`
- Core dependencies: numpy, scipy, matplotlib

### Rust
- Requires Rust toolchain (rustc, cargo)
- Dependencies listed in `Cargo.toml`

---

*For the main CCC Clock Python package, see `ccc_clock/src/`*