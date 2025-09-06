# CCC Clock Demonstration System
**ALWAYS follow these instructions first and fallback to additional search and context gathering only when information is incomplete or found to be in error.**

The CCC Clock Demonstration System is a Python-based scientific computing platform for testing Computational Complexity Cosmology (CCC) theory using co-located optical atomic clocks.

## Working Effectively

### Bootstrap, Build, and Test the Repository

**Initial Setup (takes ~70 seconds total):**
```bash
# Install package in development mode
pip install -e .
# Install dependencies from requirements file  
pip install -r ccc_clock/requirements.txt
# Install dashboard dependency (not in requirements.txt)
pip install dash myst-parser
```

**Run Tests (takes 1.2 seconds):**
```bash
cd ccc_clock
python -m pytest tests/ -v
# Expected: 6 tests pass with 6 warnings in ~1.2 seconds
```

**Code Quality Checks (each takes <1 second):**
```bash
cd ccc_clock
# Check critical errors
flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
# Format code 
black src tests
# Check formatting
black --check src tests
```

**Build Documentation (takes 1.8 seconds):**
```bash
cd ccc_clock/docs
make html
# Builds to _build/html/ (excluded by .gitignore)
```

## Running Applications

**Dashboard (Live Monitoring System):**
```bash
cd ccc_clock
python dashboard.py
# Starts on http://localhost:8050
# Dashboard displays real-time CCC clock parameters and visualizations
```

**Generate Scientific Figures (takes 3-4 seconds each):**
```bash
# From repository root
python figures/make_abba_traces.py
python figures/make_sensitivity_curves.py 
python figures/make_manifold_schematic.py
# Outputs saved to figures/output/ (excluded by .gitignore)
```

**Run Core Analysis Modules:**
```bash
cd ccc_clock
# Test metrology module (runs self-tests)
python src/metrology.py
# Expected output: Parameter set analysis and ABBA simulator tests
```

## Validation

**ALWAYS test code changes with this full validation sequence:**

1. **Run the test suite (1.2 seconds - NEVER CANCEL):**
   ```bash
   cd ccc_clock && python -m pytest tests/ -v
   ```

2. **Check code formatting (<1 second):**
   ```bash
   cd ccc_clock && black --check src tests
   ```

3. **Verify dashboard starts (10 seconds test):**
   ```bash
   cd ccc_clock && timeout 10 python dashboard.py
   ```

4. **Test figure generation (3-4 seconds):**
   ```bash
   python figures/make_abba_traces.py
   ```

5. **Manual scenario validation:**
   - Import core modules: `from ccc_clock.src.metrology import PARAMETER_SETS`
   - Verify 3 parameter sets available: A, B, C
   - Test dashboard loads visualization interface
   - Generate at least one scientific figure to verify plotting pipeline

**Timing Expectations (NEVER CANCEL these operations):**
- Initial package install: ~60 seconds
- Test suite: 1.2 seconds  
- Code formatting: <1 second each
- Documentation build: 1.8 seconds
- Figure generation: 3-4 seconds each
- Dashboard startup: <5 seconds

## Repository Structure

**Core Python Package (`ccc_clock/`):**
```
ccc_clock/
├── src/
│   ├── metrology.py         # Core CCC theory implementation  
│   ├── bridge_ccc.py        # Bridge analysis (R* = 5.80)
│   └── protocol.py          # ABBA demodulation protocol
├── tests/
│   └── test_acceptance.py   # 6 acceptance criteria tests
├── dashboard.py             # Live monitoring dashboard (port 8050)
├── docs/                    # Sphinx documentation
└── requirements.txt         # Python dependencies
```

**Scientific Assets:**
```
figures/                     # Figure generation scripts
├── make_abba_traces.py     # ABBA protocol visualization
├── make_sensitivity_curves.py  # Detection sensitivity plots  
├── make_manifold_schematic.py  # Θ-loop geometry
└── output/                 # Generated figures (gitignored)
```

## Common Development Tasks

**Add new scientific analysis:**
1. Create module in `ccc_clock/src/`
2. Add tests in `ccc_clock/tests/`
3. Run validation sequence
4. Generate figures if applicable

**Modify dashboard:**
1. Edit `ccc_clock/dashboard.py`
2. Test startup with `timeout 10 python dashboard.py`
3. Verify visualization loads correctly

**Update documentation:**
1. Edit files in `ccc_clock/docs/`
2. Build with `cd ccc_clock/docs && make html`
3. Check for warnings in build output

## Dependencies and System Requirements

**Python Requirements:**
- Python 3.9+ (tested with 3.12.3)
- Core: numpy, scipy, matplotlib, pandas
- Interactive: plotly, dash, jupyter
- Testing: pytest, pytest-cov
- Documentation: sphinx, sphinx-rtd-theme, myst-parser

**Optional but Recommended:**
- FFmpeg (for animation generation): `sudo apt-get install ffmpeg`
- Not required for core functionality

**Import Pattern for Development:**
```python
import sys
sys.path.append('ccc_clock/src')
from metrology import PARAMETER_SETS, CCCMetrology
from bridge_ccc import CCCBridgeAnalyzer  
from protocol import ABBASequence, CCCProtocol
```

## Troubleshooting

**Test Failures:**
```bash
# Run with verbose output
cd ccc_clock && python -m pytest tests/ -v -s --tb=long
```

**Import Errors:**
```bash
# Ensure PYTHONPATH includes src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/ccc_clock/src"
```

**Dashboard Not Loading:**
```bash
# Verify dash dependency
pip install dash
# Check port availability (dashboard uses 8050)
```

**Animation Generation Issues:**
```bash
# Install FFmpeg if needed
sudo apt-get install ffmpeg
# Set matplotlib backend for headless systems
export MPLBACKEND=Agg
```

## CI/CD Integration

**GitHub Actions Pipeline (.github/workflows/ci.yml):**
- Multi-platform testing (Python 3.9, 3.10, 3.11)
- Code quality: flake8, black, isort, mypy
- Documentation builds and deployment
- Animation generation with artifact storage

**Before committing changes:**
```bash
cd ccc_clock
flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
black src tests
python -m pytest tests/ -v
```

## Key Scientific Concepts

**Parameter Sets (available in PARAMETER_SETS dict):**
- Set A: Fast detection (0.8 hours) - max signal
- Set B: Balanced approach (13.1 hours) 
- Set C: Conservative (>1000 hours) - requires optimization

**Core Equation:** `(Δf/f)_demod = Γ_Θ × R_op × A_Σ + systematics`

**Acceptance Criteria (A1-A5):**
- A1: Detection time ≤ 72h for at least one parameter set
- A2: Bridge analysis convergence 
- A3: ABBA sign flip validation
- A4: Publication-ready documentation
- A5: Reproducible execution

Always validate that your changes maintain all acceptance criteria by running the test suite.