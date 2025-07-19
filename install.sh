#!/bin/bash
#
# NOVA One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/SharminSirajudeen/nova/main/install.sh | bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
    ╔═══════════════════════════════════════╗
    ║              NOVA                     ║
    ║     Neural Optimization &             ║
    ║     Versatile Automation              ║
    ╚═══════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Main installation
main() {
    clear
    show_banner
    
    echo -e "${CYAN}NOVA One-Line Installer${NC}"
    echo "========================"
    echo
    
    # Step 1: Check Prerequisites
    echo "Step 1: Checking prerequisites..."
    
    # Check OS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "NOVA requires macOS"
        exit 1
    fi
    log_info "macOS detected"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required"
        echo "Please install Python 3.9+ from https://python.org and run this installer again"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 9 ]]; then
        log_error "Python 3.9+ is required (found $PYTHON_VERSION)"
        echo "Please install Python 3.9+ from https://python.org and run this installer again"
        exit 1
    fi
    log_info "Python $PYTHON_VERSION detected"
    
    # Step 2: Download NOVA
    echo
    echo "Step 2: Downloading NOVA..."
    
    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Download NOVA
    if command -v git &> /dev/null; then
        log_info "Downloading NOVA with git..."
        git clone https://github.com/SharminSirajudeen/nova.git
        cd nova
    else
        log_info "Downloading NOVA with curl..."
        curl -L https://github.com/SharminSirajudeen/nova/archive/main.tar.gz | tar xz
        cd nova-main
    fi
    
    # Step 3: Install Dependencies
    echo
    echo "Step 3: Installing Python dependencies..."
    
    log_info "Installing required packages..."
    pip3 install --user psutil click rich prompt-toolkit aiohttp aiofiles pydantic python-dotenv pyobjc-framework-Cocoa pyobjc-framework-ScriptingBridge cryptography ollama openai tiktoken numpy
    
    # Step 4: Install NOVA Globally
    echo
    echo "Step 4: Installing NOVA globally..."
    
    # Create nova directory
    log_info "Creating ~/.nova directory..."
    mkdir -p ~/.nova
    
    # Copy files
    log_info "Copying NOVA files..."
    cp -r . ~/.nova/
    
    # Create global command
    log_info "Creating nova command..."
    mkdir -p ~/bin
    cat > ~/bin/nova << 'EOF'
#!/bin/bash
cd ~/.nova
python3 nova_core.py "$@"
EOF
    
    # Make executable
    chmod +x ~/bin/nova
    ln -sf ~/bin/nova ~/bin/nv
    
    # Step 5: Add to PATH
    echo
    echo "Step 5: Setting up PATH..."
    
    # Detect shell and add to appropriate config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # Add to PATH if not already there
    if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$SHELL_CONFIG" 2>/dev/null; then
        echo 'export PATH="$HOME/bin:$PATH"' >> "$SHELL_CONFIG"
        log_info "Added ~/bin to PATH in $SHELL_CONFIG"
    else
        log_info "PATH already configured"
    fi
    
    # Cleanup
    cd -
    rm -rf "$TEMP_DIR"
    
    # Success message
    echo
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ NOVA installed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo
    echo "To get started:"
    echo -e "1. ${CYAN}Open a new terminal${NC} (or run: source $SHELL_CONFIG)"
    echo -e "2. ${CYAN}Run: nova${NC}"
    echo
    echo "NOVA will guide you through the rest of the setup!"
    echo
    echo "Available commands:"
    echo -e "  ${CYAN}nova${NC}     - Start interactive session"
    echo -e "  ${CYAN}nv${NC}       - Quick shorthand"
    echo -e "  ${CYAN}nova -h${NC}  - Show help"
    echo
}

# Run main installation
main "$@"