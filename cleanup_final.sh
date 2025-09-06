#!/bin/bash
# CCC Clock Repository Final Cleanup Script
# Run this script locally to complete the repository organization

echo "========================================="
echo "CCC Clock Repository Final Cleanup"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to confirm actions
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

echo -e "${BLUE}Step 1: Remove duplicate ccc_clock subdirectory${NC}"
echo "This directory contains duplicates of files already organized elsewhere."
if confirm "Remove ccc_clock/ subdirectory?"; then
    git rm -rf ccc_clock/
    echo -e "${GREEN}✓ Removed ccc_clock/ subdirectory${NC}"
else
    echo -e "${YELLOW}⊗ Skipped removing ccc_clock/${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Move important files before deletion${NC}"

# Check if CITATION.cff needs to be preserved
if [ -f "ccc_clock/CITATION.cff" ] && [ ! -f "CITATION.cff" ]; then
    echo "Moving CITATION.cff to root..."
    git mv ccc_clock/CITATION.cff .
    echo -e "${GREEN}✓ Moved CITATION.cff to root${NC}"
fi

# Check if .zenodo.json needs to be preserved
if [ -f "ccc_clock/.zenodo.json" ] && [ ! -f ".zenodo.json" ]; then
    echo "Moving .zenodo.json to root..."
    git mv ccc_clock/.zenodo.json .
    echo -e "${GREEN}✓ Moved .zenodo.json to root${NC}"
fi

# Move lab_outreach_package if needed
if [ -f "ccc_clock/lab_outreach_package.tar.gz" ]; then
    mkdir -p releases
    git mv ccc_clock/lab_outreach_package.tar.gz releases/
    echo -e "${GREEN}✓ Moved lab_outreach_package.tar.gz to releases/${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Remove PDF from root${NC}"
if [ -f "bridge_null_enhancements_summary.pdf" ]; then
    if confirm "Remove bridge_null_enhancements_summary.pdf from root?"; then
        git rm bridge_null_enhancements_summary.pdf
        echo -e "${GREEN}✓ Removed PDF from root${NC}"
    fi
else
    echo -e "${YELLOW}⊗ PDF not found in root${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Move index.html to root for GitHub Pages${NC}"
if [ -f "web/index.html" ] && [ ! -f "index.html" ]; then
    if confirm "Copy web/index.html to root for GitHub Pages?"; then
        cp web/index.html .
        git add index.html
        echo -e "${GREEN}✓ Copied index.html to root${NC}"
    fi
else
    echo -e "${YELLOW}⊗ index.html already exists or not found${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Create directories for better organization${NC}"

# Create examples directory if it doesn't exist
if [ ! -d "examples" ]; then
    mkdir -p examples
    cat > examples/README.md << 'EOF'
# 📚 CCC Clock Examples

This directory contains example scripts and demonstrations for the CCC Clock system.

## Quick Start Examples
- Parameter optimization demos
- Sensitivity analysis examples
- ABBA protocol demonstrations

Coming soon!
EOF
    git add examples/README.md
    echo -e "${GREEN}✓ Created examples/ directory${NC}"
fi

# Create releases directory if it doesn't exist
if [ ! -d "releases" ]; then
    mkdir -p releases
    cat > releases/README.md << 'EOF'
# 📦 CCC Clock Releases

This directory contains release packages and distributions.

## Available Packages
- `lab_outreach_package.tar.gz` - Complete package for lab partners
EOF
    git add releases/README.md
    echo -e "${GREEN}✓ Created releases/ directory${NC}"
fi

echo ""
echo -e "${BLUE}Step 6: Clean up any remaining artifacts${NC}"

# Remove .DS_Store files
find . -name ".DS_Store" -type f -delete 2>/dev/null
echo -e "${GREEN}✓ Removed .DS_Store files${NC}"

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✓ Removed __pycache__ directories${NC}"

# Remove .pytest_cache directories
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✓ Removed .pytest_cache directories${NC}"

echo ""
echo -e "${BLUE}Step 7: Update repository structure documentation${NC}"
cat > REPO_STRUCTURE.md << 'EOF'
# 📁 CCC Clock Repository Structure

## Current Organization (Updated)

```
ccc_clock/
├── 📚 docs/                    # All documentation
│   ├── executive/              # Leadership documents
│   ├── technical/              # Technical specs
│   └── collaboration/          # Partnership materials
├── 🔬 src/                     # Source code
│   ├── analysis/               # Analysis scripts
│   └── [rust files]            # Rust implementation
├── 🎨 figures/                 # Visualizations
│   └── [8 publication figures]
├── 🌐 web/                     # Web interface
│   ├── dashboard.py
│   └── index.html
├── 🎯 examples/                # Example scripts
├── 🎪 presentations/           # Presentation materials
├── 📦 releases/                # Release packages
└── 📋 Root Files
    ├── README.md
    ├── index.html              # GitHub Pages
    ├── LICENSE
    ├── CITATION.cff
    ├── requirements.txt
    └── setup.py
```

## Navigation

- **Documentation**: [docs/](docs/)
- **Source Code**: [src/](src/)
- **Visualizations**: [figures/](figures/)
- **Web Interface**: [web/](web/)
- **Live Demo**: https://tnsr-q.github.io/ccc_clock/

## Status: ✅ Fully Organized
EOF
git add REPO_STRUCTURE.md
echo -e "${GREEN}✓ Updated REPO_STRUCTURE.md${NC}"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Summary of changes:"
git status --short

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the changes with: git status"
echo "2. Commit the changes with: git commit -m 'Complete repository cleanup and organization'"
echo "3. Push to GitHub with: git push"
echo ""
echo -e "${BLUE}Your repository is now professionally organized!${NC}"
