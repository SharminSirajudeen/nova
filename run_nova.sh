#!/bin/bash
# Simple NOVA runner with proper environment

# Set Ollama to use external storage
export OLLAMA_MODELS="/Volumes/SandiskSSD/NOVA/ollama/models"

# Run NOVA
echo "Starting NOVA with dolphin3..."
python3 -m src.main