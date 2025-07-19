#!/bin/bash

# NOVA Optimized Model Setup
# Downloads only 3 powerful models for all agent roles

echo "🚀 NOVA Optimized Model Setup"
echo "=============================="
echo "This will download 3 powerful uncensored models (~49GB total)"
echo "These 3 models will power all 20+ AI agents efficiently"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install from https://ollama.ai"
    exit 1
fi

echo "✅ Ollama detected"
echo ""

# Core models
MODELS=(
    "dolphin-mixtral:8x7b"    # Universal powerhouse (CEO, CTO, Architects)
    "deepseek-coder:33b"      # Technical specialist (All developers, DevOps)
    "dolphin-mistral:7b"      # Fast creative (Designers, Support, Quick tasks)
)

# Model descriptions
declare -A MODEL_DESC
MODEL_DESC["dolphin-mixtral:8x7b"]="Universal AI (Executives, Senior roles) - 26GB"
MODEL_DESC["deepseek-coder:33b"]="Code Specialist (Developers, Engineers) - 19GB"
MODEL_DESC["dolphin-mistral:7b"]="Fast Creative (Designers, Support) - 4.1GB"

# Check which models are already installed
echo "Checking installed models..."
INSTALLED=$(ollama list | tail -n +2 | awk '{print $1}')

echo ""
echo "📊 Model Status:"
echo "----------------"

for model in "${MODELS[@]}"; do
    if echo "$INSTALLED" | grep -q "^$model"; then
        echo "✅ $model - ${MODEL_DESC[$model]} [INSTALLED]"
    else
        echo "❌ $model - ${MODEL_DESC[$model]} [NOT INSTALLED]"
    fi
done

echo ""
echo "🎯 Model Strategy Benefits:"
echo "- Only 3 models instead of 15+"
echo "- ~49GB total vs 300GB+ for individual models"
echo "- Full coverage of all AI agent roles"
echo "- Smart routing based on task type"
echo "- Personality through prompting, not separate models"
echo ""

# Ask for confirmation
read -p "Download missing models? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    for model in "${MODELS[@]}"; do
        if ! echo "$INSTALLED" | grep -q "^$model"; then
            echo "📥 Downloading $model..."
            echo "   ${MODEL_DESC[$model]}"
            ollama pull "$model"
            echo "✅ $model installed"
            echo ""
        fi
    done
    
    echo ""
    echo "🎉 Setup complete! Your NOVA now has:"
    echo ""
    echo "1. Universal AI Model - Powers:"
    echo "   • CEO (Warren Buffett mode)"
    echo "   • CTO (Steve Jobs mode)"
    echo "   • Chief Product Officer"
    echo "   • Senior Architects"
    echo "   • Product Managers"
    echo ""
    echo "2. Technical AI Model - Powers:"
    echo "   • Full-stack Developers"
    echo "   • Backend/Frontend Engineers"
    echo "   • DevOps Engineers"
    echo "   • QA Engineers"
    echo ""
    echo "3. Creative AI Model - Powers:"
    echo "   • UI/UX Designers (Jony Ive mode)"
    echo "   • Product Designers"
    echo "   • Technical Writers"
    echo "   • Support Engineers"
    echo ""
    echo "✨ All 20+ agents are now ready with just 3 models!"
else
    echo "Setup cancelled."
fi