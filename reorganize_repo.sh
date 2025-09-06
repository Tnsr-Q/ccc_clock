#!/bin/bash
# Repository Reorganization Script
# This script provides guidance for reorganizing the CCC Clock repository

echo "CCC Clock Repository Reorganization Plan"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Phase 1: Documentation Organization${NC}"
echo "--------------------------------------"
echo "Move documentation files to proper locations:"
echo ""

# Documentation moves
cat << 'EOF'
# Executive Documents (from ccc_clock/ to docs/executive/)
- EXECUTIVE_BRIEF.md → docs/executive/
- GO_NO_GO_DECISION.md → docs/executive/
- FINAL_PERFORMANCE_SUMMARY.md → docs/executive/
- PRODUCTION_SUMMARY.md → docs/executive/

# Technical Documents (to docs/technical/)
- ANALYSIS_RESULTS.md → docs/technical/
- bridge_null_enhancements_summary.md → docs/technical/
- REPRODUCIBILITY_CHECKLIST.md → docs/technical/
- DEPLOYMENT_CHECKLIST.md → docs/technical/
- README_experiments.md → docs/technical/

# Collaboration Documents (to docs/collaboration/)
- LAB_OUTREACH_TEMPLATE.md → docs/collaboration/
- presentation_slides.md → docs/collaboration/

# PDF Cleanup
- Remove all .pdf duplicates (keep only essential ones in releases/)
EOF

echo ""
echo -e "${GREEN}Phase 2: Source Code Organization${NC}"
echo "--------------------------------------"

cat << 'EOF'
# Core Modules (from root to src/ccc_clock/)
- bridge_null_utils.py → src/ccc_clock/
- experiments_bridge_null.py → src/analysis/

# Keep existing structure:
- src/ccc_clock/ (already organized)
- tests/ (already organized)

# Scripts to move:
- dashboard.py → web/
- animate_theta_abba.py → figures/scripts/
EOF

echo ""
echo -e "${GREEN}Phase 3: Asset Organization${NC}"
echo "--------------------------------------"

cat << 'EOF'
# Figures (already well organized)
- figures/ (keep current structure)
  - Add subdirectories:
    - static/ (for .png, .svg files)
    - interactive/ (for .html files)
    - scripts/ (for generation scripts)

# Web Assets
- index.html → web/
- Create web/assets/ for CSS/JS files

# Presentations
- CCC_Clock_Presentation.* → presentations/slides/
- presentation_slides.* → presentations/slides/
EOF

echo ""
echo -e "${GREEN}Phase 4: Cleanup${NC}"
echo "--------------------------------------"

cat << 'EOF'
# Remove from repository:
- .DS_Store (all instances)
- __pycache__/ (all instances)
- .pytest_cache/
- .venv/
- *.pyc files
- visualization_data.pkl (regenerate as needed)
- validation_log.txt (regenerate as needed)

# Files to keep in root:
- README.md (main)
- LICENSE
- CITATION.cff
- requirements.txt
- setup.py
- .gitignore
- REPO_STRUCTURE.md
EOF

echo ""
echo -e "${YELLOW}Phase 5: Create Navigation Files${NC}"
echo "--------------------------------------"

cat << 'EOF'
Create README.md files in each major directory:
- docs/README.md (documentation index)
- src/README.md (code structure guide)
- figures/README.md (visualization catalog)
- web/README.md (web interface guide)
- presentations/README.md (presentation materials)
EOF

echo ""
echo -e "${GREEN}Benefits of Reorganization:${NC}"
echo "- Clear separation of concerns"
echo "- Easy navigation for collaborators"
echo "- Professional repository appearance"
echo "- Reduced clutter and duplicates"
echo "- Better development workflow"
echo ""
echo "Note: This is a guide. Execute moves carefully to preserve git history."
