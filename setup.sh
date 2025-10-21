#!/bin/bash
# Setup script for PaddleOCR Application

echo "=========================================="
echo "PaddleOCR Application Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if poppler is installed
echo ""
echo "Checking for poppler (required for PDF processing)..."
if command -v pdfinfo &> /dev/null; then
    echo "✓ Poppler is installed"
else
    echo "⚠ Poppler is not installed"
    echo ""
    echo "Please install poppler:"
    echo "  macOS:   brew install poppler"
    echo "  Ubuntu:  sudo apt-get install poppler-utils"
    echo "  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully"

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p output
echo "✓ Output directory created"

# Download PaddleOCR models (optional, will happen on first run anyway)
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To use the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python main.py <your-file.pdf>"
echo ""
echo "  3. See examples:"
echo "     python examples.py"
echo ""
echo "  4. Read documentation:"
echo "     cat README.md"
echo ""
echo "Note: On first run, PaddleOCR will download models (~150MB)"
echo "      This is a one-time download and may take a few minutes."
echo ""
