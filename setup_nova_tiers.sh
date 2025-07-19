#!/bin/bash

# NOVA Tiered Model Setup 2025
# Choose the right tier for your development needs

echo "🚀 NOVA Tiered Model Setup - 2025 Edition"
echo "=========================================="
echo ""
echo "Choose your NOVA deployment tier based on your current needs:"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install from https://ollama.ai"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama detected"
echo ""

# Define all tiers
echo "📊 Available Tiers:"
echo "==================="
echo ""

echo "🎯 TIER 3: LOCAL EFFICIENT (Recommended for Local Development)"
echo "   Perfect for: Getting started, testing, development on any machine"
echo "   Storage: ~16GB total"
echo "   Models:"
echo "   • dolphin-mistral:7b (4.1GB) - All-purpose reasoning & leadership"
echo "   • llama2-uncensored:7b (3.8GB) - Universal problem solving"
echo "   • deepseek-coder:7b (3.8GB) - Coding specialist"
echo "   • dolphin3:8b (4.7GB) - Latest creative tasks"
echo ""

echo "💪 TIER 2: LOCAL POWERHOUSE (For High-End Local Development)"
echo "   Perfect for: Serious local development, powerful hardware"
echo "   Storage: ~57GB total"
echo "   Models:"
echo "   • dolphin-mixtral:8x7b (26GB) - Powerful reasoning & leadership"
echo "   • wizard-vicuna-uncensored:13b (7.4GB) - Versatile problem solving"
echo "   • deepseek-coder:33b (19GB) - Advanced coding specialist"
echo "   • dolphin-mistral:7b (4.1GB) - Fast creative tasks"
echo ""

echo "🌟 TIER 1: ULTRA CLOUD (For Cloud Production Deployment)"
echo "   Perfect for: Cloud deployment, maximum capability, production"
echo "   Storage: ~109GB total"
echo "   Models:"
echo "   • deepseek-r1:14b (8.5GB) - Latest reasoning titan (Jan 2025)"
echo "   • dolphin-mixtral:8x22b (87GB) - Most powerful uncensored model"
echo "   • deepseek-coder-v2:16b (9.1GB) - Advanced coding specialist"
echo "   • dolphin3:8b (4.7GB) - Latest creative master"
echo ""

echo "🎭 All tiers include the same legendary AI personalities:"
echo "• Alexandra Sterling (CTO) - Buffett × Linus × Jobs × Ive"
echo "• Marcus Venture (CEO) - Jobs × Bezos × Musk"
echo "• Luna Chen (Design) - Ive × Dieter Rams × Paul Rand"
echo "• Kai Nakamura (Architect) - Linus × Carmack × Jeff Dean"
echo "• Sofia Rodriguez (Full-Stack) - Dan Abramov × Kent Beck"
echo "• Dr. Aisha Patel (AI Research) - Hinton × Karpathy"
echo "• Ryan Kim (DevOps) - Kelsey Hightower × Adrian Cockcroft"
echo "• Emma Thompson (QA) - James Bach × Lisa Crispin"
echo "• And 12+ more legendary personalities..."
echo ""

# Auto-detect recommended tier based on available space (simplified)
available_space=$(df . | tail -1 | awk '{print $4}')
available_gb=$((available_space / 1024 / 1024))

echo "💾 System Check:"
echo "==============="
echo "Available space: ~${available_gb}GB"

if [ $available_gb -gt 120 ]; then
    recommended="1"
    echo "✅ Recommended: TIER 1 (Ultra Cloud) - You have space for the most powerful models"
elif [ $available_gb -gt 70 ]; then
    recommended="2"
    echo "✅ Recommended: TIER 2 (Local Powerhouse) - Good balance of power and space"
else
    recommended="3"
    echo "✅ Recommended: TIER 3 (Local Efficient) - Perfect for your available space"
fi

echo ""
echo "🚀 Select your tier:"
echo "1) TIER 3: Local Efficient (~16GB) - Best for getting started"
echo "2) TIER 2: Local Powerhouse (~57GB) - For serious development"
echo "3) TIER 1: Ultra Cloud (~109GB) - Maximum power"
echo "4) Custom - Select specific models"
echo ""

read -p "Enter your choice (1-4) [${recommended}]: " tier_choice

# Use recommended if no input
if [ -z "$tier_choice" ]; then
    tier_choice=$recommended
fi

# Define tier models
declare -A TIER3_MODELS=(
    ["reasoning"]="dolphin-mistral:7b"
    ["universal"]="llama2-uncensored:7b"
    ["coding"]="deepseek-coder:7b"
    ["creative"]="dolphin3:8b"
)

declare -A TIER2_MODELS=(
    ["reasoning"]="dolphin-mixtral:8x7b"
    ["universal"]="wizard-vicuna-uncensored:13b"
    ["coding"]="deepseek-coder:33b"
    ["creative"]="dolphin-mistral:7b"
)

declare -A TIER1_MODELS=(
    ["reasoning"]="deepseek-r1:14b"
    ["universal"]="dolphin-mixtral:8x22b"
    ["coding"]="deepseek-coder-v2:16b"
    ["creative"]="dolphin3:8b"
)

# Set selected models based on choice
case $tier_choice in
    1|3)
        echo ""
        echo "🎯 Selected: TIER 3 - Local Efficient"
        tier_name="TIER 3 - Local Efficient"
        declare -A SELECTED_MODELS=(
            ["reasoning"]="${TIER3_MODELS[reasoning]}"
            ["universal"]="${TIER3_MODELS[universal]}"
            ["coding"]="${TIER3_MODELS[coding]}"
            ["creative"]="${TIER3_MODELS[creative]}"
        )
        ;;
    2)
        echo ""
        echo "💪 Selected: TIER 2 - Local Powerhouse"
        tier_name="TIER 2 - Local Powerhouse"
        declare -A SELECTED_MODELS=(
            ["reasoning"]="${TIER2_MODELS[reasoning]}"
            ["universal"]="${TIER2_MODELS[universal]}"
            ["coding"]="${TIER2_MODELS[coding]}"
            ["creative"]="${TIER2_MODELS[creative]}"
        )
        ;;
    3|1)
        echo ""
        echo "🌟 Selected: TIER 1 - Ultra Cloud"
        tier_name="TIER 1 - Ultra Cloud"
        declare -A SELECTED_MODELS=(
            ["reasoning"]="${TIER1_MODELS[reasoning]}"
            ["universal"]="${TIER1_MODELS[universal]}"
            ["coding"]="${TIER1_MODELS[coding]}"
            ["creative"]="${TIER1_MODELS[creative]}"
        )
        ;;
    4)
        echo ""
        echo "🔧 Custom Selection - Not implemented in this script"
        echo "Please edit the model configurations manually or use one of the preset tiers."
        exit 1
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "📦 Models to install for ${tier_name}:"
echo "====================================="

# Check which models are already installed
INSTALLED=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')

missing_models=()
for role in "${!SELECTED_MODELS[@]}"; do
    model="${SELECTED_MODELS[$role]}"
    if echo "$INSTALLED" | grep -q "$model"; then
        echo "✅ $model ($role) [INSTALLED]"
    else
        echo "❌ $model ($role) [NOT INSTALLED]"
        missing_models+=("$model")
    fi
done

if [ ${#missing_models[@]} -eq 0 ]; then
    echo ""
    echo "🎉 All models for ${tier_name} are already installed!"
    echo ""
    echo "🚀 Quick Start:"
    echo "python nova.py"
    echo "/mode company"
    echo "/project create 'Build an AI-powered productivity app'"
    exit 0
fi

echo ""
echo "📥 Need to download ${#missing_models[@]} models: ${missing_models[*]}"
echo ""

read -p "🚀 Download missing models? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Downloading models for ${tier_name}..."
    echo ""
    
    success_count=0
    for model in "${missing_models[@]}"; do
        echo "📥 Downloading $model..."
        
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
    echo "🏢 Tier: ${tier_name}"
    echo ""
    echo "🎭 Your Legendary AI Development Company is ready with:"
    echo ""
    echo "LEGENDARY PERSONALITIES ACTIVE:"
    echo "• Alexandra Sterling (CTO) - Strategic + Technical + Product + Design"
    echo "• Marcus Venture (CEO) - Vision + Customer + Innovation"
    echo "• Luna Chen (Design) - Aesthetics + Minimalism + Visual Impact"
    echo "• David Park (Product) - User Research + Empathy + Growth"
    echo "• Kai Nakamura (Architect) - Performance + Scale + System Design"
    echo "• Sofia Rodriguez (Full-Stack) - Developer Experience + Quality"
    echo "• Dr. Aisha Patel (AI Research) - Deep Learning + Practical AI"
    echo "• Ryan Kim (DevOps) - Infrastructure + Automation + Reliability"
    echo "• Emma Thompson (QA) - Quality + Testing + Process Excellence"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "======================="
    echo "# Start NOVA"
    echo "python nova.py"
    echo ""
    echo "# Switch to company mode"
    echo "/mode company"
    echo ""
    echo "# Create a project with legendary team"
    echo "/project create 'Build a real-time collaboration platform'"
    echo ""
    echo "# See your legendary team"
    echo "/team"
    echo ""
    echo "# Switch between legendary personalities"
    echo "/personality jobs     # Steve Jobs mode"
    echo "/personality buffett  # Warren Buffett mode"
    echo "/personality linus    # Linus Torvalds mode"
    echo "/personality ive      # Jony Ive mode"
    echo ""
    echo "⬆️  UPGRADE PATH:"
    echo "================="
    echo "When ready for cloud deployment:"
    echo "./setup_nova_tiers.sh  # Choose TIER 1 for ultra-powerful models"
    echo ""
    echo "Your ${tier_name} setup includes automatic tier upgrade support!"
    
else
    echo ""
    echo "❌ Setup cancelled."
    echo ""
    echo "📝 To install models manually:"
    for model in "${missing_models[@]}"; do
        echo "  ollama pull $model"
    done
fi

echo ""
echo "📚 Next Steps:"
echo "============="
echo "• Start with: python nova.py"
echo "• Read src/legendary/ for personality details"
echo "• Check OPTIMIZED_MODELS.md for strategy documentation"
echo "• When ready for cloud: upgrade to TIER 1 models"