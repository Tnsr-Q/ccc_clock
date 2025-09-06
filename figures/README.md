# 🎨 CCC Clock Visualization Gallery

This directory contains all figures, plots, and visualizations for the CCC Clock Demonstration System.

## 📁 Directory Organization

- **[scripts/](scripts/)** - Figure generation scripts and animation tools
- **[static/](static/)** - PNG and SVG static figures (future organization)
- **[interactive/](interactive/)** - HTML interactive visualizations (future organization)

## 📊 Figure Categories

### Static Figures (PNG/SVG)
High-resolution publication-ready figures for papers and presentations.

| Figure | Description | Formats | Key Result |
|--------|-------------|---------|------------|
| **manifold_schematic** | Θ-loop operational manifold | [PNG](manifold_schematic.png) / [SVG](manifold_schematic.svg) | Shows geometric measurement |
| **bridge_landscape** | 3D residual optimization | [PNG](bridge_landscape.png) / [SVG](bridge_landscape.svg) | R* = 5.80 convergence |
| **epsilon_sweep** | ε-parameter scaling analysis | [PNG](epsilon_sweep.png) / [SVG](epsilon_sweep.svg) | Linear scaling confirmed |
| **sensitivity_curves** | Detection time vs loop area | [PNG](sensitivity_curves.png) / [SVG](sensitivity_curves.svg) | 0.8h detection achieved |
| **abba_traces** | ABBA demodulation traces | [PNG](abba_traces.png) / [SVG](abba_traces.svg) | Perfect -1.000 sign flip |
| **null_comparison** | Exact null vs commutator | [PNG](null_comparison.png) / [SVG](null_comparison.svg) | 10× floor difference |
| **weight_optimization** | 14D weight learning | [PNG](weight_optimization.png) / [SVG](weight_optimization.svg) | 100× improvement |
| **ccc_explainer** | Concept diagram | [PNG](ccc_explainer.png) / [SVG](ccc_explainer.svg) | Full signal chain |

### Interactive Visualizations (HTML)
Web-based interactive plots for exploration and presentation.

- **[bridge_landscape.html](bridge_landscape.html)** - Interactive 3D surface plot of bridge residuals
- More interactive versions coming soon!

### Figure Generation Scripts
Python scripts to reproduce all figures. Most scripts are in the root of this directory, with animations moved to `scripts/`.

| Script | Creates | Dependencies |
|--------|---------|--------------|
| `make_manifold_schematic.py` | Operational manifold diagram | matplotlib, numpy |
| `make_bridge_landscape.py` | 3D bridge analysis | plotly, scipy |
| `make_epsilon_sweep.py` | ε-sweep analysis | matplotlib, seaborn |
| `make_sensitivity_curves.py` | Detection sensitivity | matplotlib, numpy |
| `make_abba_traces.py` | ABBA protocol traces | matplotlib, scipy |
| `make_null_comparison.py` | Null comparison panels | matplotlib, seaborn |
| `make_weight_optimization.py` | Weight optimization | matplotlib, numpy |
| `make_static_explainer.py` | CCC concept diagram | matplotlib |
| `make_animation.py` | Animated demonstrations | matplotlib, ffmpeg |
| **[scripts/animate_theta_abba.py](scripts/animate_theta_abba.py)** | Θ-loop ABBA animation | matplotlib, ffmpeg |

### Shared Configuration
- **[style_config.py](style_config.py)** - Consistent styling across all figures

## 🎯 Key Results Visualized

### Performance Achievements
- **Detection Time**: 0.8 hours (Parameter Set A)
- **Bridge Convergence**: R* = 5.80 ± 0.098
- **Sign Flip**: Perfect -1.000 ratio
- **Systematic Rejection**: >40 dB

### Scientific Validation
- Θ-loop geometry confirmed
- ABBA protocol validated
- Bridge analysis converged
- Commutator floor reached

## 📐 Figure Specifications

### Technical Standards
- **Resolution**: 300 DPI for publication
- **Color Scheme**: Colorblind-friendly palette
- **Font**: Times New Roman for papers
- **Grid**: Professional scientific styling

### File Formats
- **PNG**: Raster format for documents
- **SVG**: Vector format for scaling
- **HTML**: Interactive web visualizations
- **PDF**: Export option available

## 🔧 Reproducing Figures

To regenerate all figures:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all figure generation scripts
cd figures
python make_manifold_schematic.py
python make_bridge_landscape.py
python make_epsilon_sweep.py
python make_sensitivity_curves.py
python make_abba_traces.py
python make_null_comparison.py
python make_weight_optimization.py
python make_static_explainer.py
```

## 📚 Documentation

For detailed information about each visualization:
- See [VISUALIZATION_SUITE_SUMMARY.md](VISUALIZATION_SUITE_SUMMARY.md)
- Check individual script docstrings
- Review [style_config.py](style_config.py) for styling details

## 🎬 Animations

To create the animated demonstration:
```bash
python make_animation.py
# Requires ffmpeg for video generation
```

## 📝 Citation

If using these figures in publications, please cite:
```
CCC Clock Demonstration System
GitHub: https://github.com/Tnsr-Q/ccc_clock
```

---

*All figures are publication-ready and validated for scientific accuracy.*
