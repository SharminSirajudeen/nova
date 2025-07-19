#!/bin/bash

echo "================================================"
echo "NOVA Legendary Mode Setup"
echo "================================================"
echo ""
echo "This script sets up the AI Software Development"
echo "Company features for NOVA."
echo ""

# Check if we're in the nova directory
if [ ! -f "nova.py" ]; then
    echo "Error: Please run this script from the nova directory"
    exit 1
fi

# Create necessary directories
echo "1. Creating directories..."
mkdir -p ~/.nova/company/{projects,clients,deliverables,documentation,metrics,templates,research}
echo "   ✓ Company directories created"

# Check Python version
echo ""
echo "2. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Install additional requirements if needed
echo ""
echo "3. Checking dependencies..."
pip3 install -q aiohttp 2>/dev/null || true
echo "   ✓ Dependencies checked"

# Test the integration
echo ""
echo "4. Testing integration..."
python3 test_integration.py
test_result=$?

if [ $test_result -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ Setup Complete!"
    echo "================================================"
    echo ""
    echo "You can now use NOVA in two modes:"
    echo ""
    echo "1. Personal Mode (default):"
    echo "   python3 nova.py"
    echo ""
    echo "2. Company Mode:"
    echo "   python3 nova.py"
    echo "   Then type: /mode company"
    echo ""
    echo "Company mode commands:"
    echo "   /company - Show dashboard"
    echo "   /project create <brief> - Create project"
    echo "   /team - Show AI team"
    echo ""
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi