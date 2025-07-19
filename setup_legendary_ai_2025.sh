#!/bin/bash

# NOVA Legendary AI Setup 2025 Edition
# Downloads the most powerful uncensored models and sets up all legendary personalities

echo "🚀 NOVA Legendary AI Setup - 2025 Edition"
echo "=========================================="
echo ""
echo "This will set up the most powerful AI development company with:"
echo "• 🧠 Latest reasoning models (DeepSeek R1 - Jan 2025)"
echo "• 💻 Most powerful uncensored models (Dolphin Mixtral 8x22B)"
echo "• 👥 20+ legendary tech personalities (Jobs, Buffett, Linus, Ive, Musk, etc.)"
echo "• 🏢 Complete AI development company (CEO, CTO, architects, developers, designers)"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install from https://ollama.ai"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama detected"
echo ""

# Ultra-Powerful Models (2025 Edition)
declare -a MODELS=(
    "deepseek-r1:14b"           # Latest reasoning titan (Jan 2025)
    "dolphin-mixtral:8x22b"     # Most powerful uncensored (141B params)
    "deepseek-coder-v2:16b"     # Advanced coding specialist
    "dolphin3:8b"               # Latest creative master (Llama 3.1)
)

# Model descriptions and roles
declare -A MODEL_DESC
MODEL_DESC["deepseek-r1:14b"]="🧠 REASONING TITAN - Latest DeepSeek R1 for complex analysis, strategy, AI research - 8.5GB"
MODEL_DESC["dolphin-mixtral:8x22b"]="🌟 UNIVERSAL GENIUS - Most powerful Dolphin uncensored for leadership, product design - 87GB"  
MODEL_DESC["deepseek-coder-v2:16b"]="💻 CODE VIRTUOSO - Advanced coding specialist for all development tasks - 9.1GB"
MODEL_DESC["dolphin3:8b"]="🎨 CREATIVE MASTER - Latest Dolphin 3.0 for design, writing, quick tasks - 4.7GB"

# Legendary personalities powered by these models
declare -A PERSONALITIES
PERSONALITIES["Alexandra Sterling"]="CTO (Buffett × Linus × Jobs × Ive) - Strategic technical leadership"
PERSONALITIES["Marcus Venture"]="CEO (Jobs × Bezos × Musk) - Visionary product leadership"
PERSONALITIES["Luna Chen"]="Design Genius (Ive × Dieter Rams × Paul Rand) - Aesthetic perfection"
PERSONALITIES["David Park"]="Product Visionary (Jobs × Julie Zhuo × Satya Nadella) - User-centered innovation"
PERSONALITIES["Kai Nakamura"]="Senior Architect (Linus × John Carmack × Jeff Dean) - System excellence"
PERSONALITIES["Sofia Rodriguez"]="Full-Stack Virtuoso (Dan Abramov × Kent Beck) - Developer experience"
PERSONALITIES["Dr. Aisha Patel"]="AI Researcher (Geoffrey Hinton × Andrej Karpathy) - ML innovation"
PERSONALITIES["Ryan Kim"]="DevOps Wizard (Kelsey Hightower × Adrian Cockcroft) - Infrastructure mastery"
PERSONALITIES["Emma Thompson"]="QA Perfectionist (James Bach × Lisa Crispin) - Quality excellence"

echo "🎯 Model Strategy:"
echo "=================="
echo "Total Storage: ~109GB (vs 300GB+ for individual models)"
echo "Total Agents: 20+ legendary personalities"
echo "Coverage: 100% of software development lifecycle"
echo ""

# Check which models are already installed
echo "📊 Checking installed models..."
INSTALLED=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')

echo ""
echo "Model Status:"
echo "============"

for model in "${MODELS[@]}"; do
    if echo "$INSTALLED" | grep -q "$model"; then
        echo "✅ $model - ${MODEL_DESC[$model]} [INSTALLED]"
    else
        echo "❌ $model - ${MODEL_DESC[$model]} [NOT INSTALLED]"
    fi
done

echo ""
echo "🎭 Legendary AI Personalities:"
echo "============================="
for personality in "${!PERSONALITIES[@]}"; do
    echo "• $personality - ${PERSONALITIES[$personality]}"
done

echo ""
echo "🔄 Model Assignment Strategy:"
echo "============================"
echo "🧠 REASONING TITAN (deepseek-r1:14b):"
echo "   • Alexandra Sterling (CTO), Marcus Venture (CEO)"
echo "   • Dr. Aisha Patel (AI Research), Security Experts"
echo ""
echo "🌟 UNIVERSAL GENIUS (dolphin-mixtral:8x22b):"
echo "   • David Park (Product), Emma Thompson (QA)"
echo "   • UX Designers, Business Analysts"
echo ""
echo "💻 CODE VIRTUOSO (deepseek-coder-v2:16b):"
echo "   • Kai Nakamura (Architect), Sofia Rodriguez (Full-Stack)"
echo "   • All Developers, Ryan Kim (DevOps), Engineers"
echo ""
echo "🎨 CREATIVE MASTER (dolphin3:8b):"
echo "   • Luna Chen (Design), Technical Writers"
echo "   • UI Designers, Customer Success, Quick Tasks"
echo ""

# Calculate total size of missing models
total_size=0
missing_models=()
for model in "${MODELS[@]}"; do
    if ! echo "$INSTALLED" | grep -q "$model"; then
        missing_models+=("$model")
        case $model in
            "deepseek-r1:14b") total_size=$((total_size + 9)) ;;
            "dolphin-mixtral:8x22b") total_size=$((total_size + 87)) ;;
            "deepseek-coder-v2:16b") total_size=$((total_size + 9)) ;;
            "dolphin3:8b") total_size=$((total_size + 5)) ;;
        esac
    fi
done

if [ ${#missing_models[@]} -eq 0 ]; then
    echo "🎉 All models are already installed! Your Legendary AI company is ready!"
    echo ""
    echo "Quick start:"
    echo "  python nova.py"
    echo "  /mode company"
    echo "  /project create 'Build an AI-powered social media platform'"
    exit 0
fi

echo "📦 Download Required:"
echo "===================="
echo "Missing models: ${#missing_models[@]} models (~${total_size}GB)"
echo "Models to download: ${missing_models[*]}"
echo ""

# Ask for confirmation
read -p "🚀 Download missing models and complete setup? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Starting download process..."
    echo "This may take a while depending on your internet connection."
    echo ""
    
    success_count=0
    for model in "${missing_models[@]}"; do
        echo "📥 Downloading $model..."
        echo "   ${MODEL_DESC[$model]}"
        echo ""
        
        # Download with progress
        if ollama pull "$model"; then
            echo "✅ $model installed successfully"
            ((success_count++))
        else
            echo "❌ Failed to install $model"
        fi
        echo ""
    done
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo "✅ Successfully installed $success_count/${#missing_models[@]} models"
    echo ""
    echo "🏢 Your Legendary AI Development Company is now ready with:"
    echo ""
    echo "EXECUTIVE TEAM:"
    echo "• Alexandra Sterling (CTO) - Buffett × Linus × Jobs × Ive"
    echo "• Marcus Venture (CEO) - Jobs × Bezos × Musk" 
    echo ""
    echo "ENGINEERING TEAM:"
    echo "• Kai Nakamura (Senior Architect) - Linus × Carmack × Jeff Dean"
    echo "• Sofia Rodriguez (Full-Stack) - Dan Abramov × Kent Beck"
    echo "• Dr. Aisha Patel (AI Research) - Hinton × Karpathy"
    echo ""
    echo "DESIGN TEAM:"
    echo "• Luna Chen (Design Genius) - Ive × Dieter Rams × Paul Rand"
    echo "• David Park (Product Vision) - Jobs × Julie Zhuo × Nadella"
    echo ""
    echo "OPERATIONS TEAM:"
    echo "• Ryan Kim (DevOps Wizard) - Kelsey Hightower × Adrian Cockcroft"
    echo "• Emma Thompson (QA Perfect) - James Bach × Lisa Crispin"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "======================="
    echo "# Start your AI company"
    echo "python nova.py"
    echo ""
    echo "# Switch to company mode"
    echo "/mode company"
    echo ""
    echo "# Create your first project" 
    echo "/project create 'Build a real-time collaboration platform with AI'"
    echo ""
    echo "# See your legendary team"
    echo "/team"
    echo ""
    echo "# View company dashboard"
    echo "/company"
    echo ""
    echo "# Switch personalities for different approaches"
    echo "/personality jobs     # Steve Jobs mode"
    echo "/personality buffett  # Warren Buffett mode"
    echo "/personality linus    # Linus Torvalds mode"
    echo "/personality ive      # Jony Ive mode"
    echo ""
    echo "✨ Your AI company can now handle any software project with the combined"
    echo "   wisdom of tech's greatest legends!"
    
else
    echo ""
    echo "❌ Setup cancelled. Run this script again when ready to download."
    echo ""
    echo "Note: You can also download models individually:"
    for model in "${missing_models[@]}"; do
        echo "  ollama pull $model"
    done
fi

echo ""
echo "📚 For more information:"
echo "• Read OPTIMIZED_MODELS.md for detailed strategy"
echo "• Check src/legendary/ for personality implementations"
echo "• Visit https://ollama.com for model documentation"