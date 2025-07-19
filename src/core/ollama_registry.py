"""
Ollama Model Registry - Complete list of all Ollama models
Updated to include ALL models from ollama.com/search
"""

# Comprehensive list of ALL Ollama models with metadata
# This includes models missing from the previous list
OLLAMA_COMPLETE_REGISTRY = [
    # Llama 3.1 family (Latest)
    {"name": "llama3.1", "size_gb": 4.7, "ram_required": 8, "description": "Latest Llama 3.1 base model", "tags": ["general", "chat"]},
    {"name": "llama3.1:8b", "size_gb": 4.7, "ram_required": 8, "description": "Llama 3.1 8B - excellent general purpose", "tags": ["general", "code", "chat"]},
    {"name": "llama3.1:70b", "size_gb": 40, "ram_required": 48, "description": "Llama 3.1 70B - exceptional reasoning", "tags": ["reasoning", "complex"]},
    {"name": "llama3.1:405b", "size_gb": 231, "ram_required": 256, "description": "Llama 3.1 405B - research grade", "tags": ["research"]},
    
    # Llama 3 family
    {"name": "llama3", "size_gb": 4.7, "ram_required": 8, "description": "Llama 3 base model", "tags": ["general"]},
    {"name": "llama3:8b", "size_gb": 4.7, "ram_required": 8, "description": "Llama 3 8B - solid performance", "tags": ["general"]},
    {"name": "llama3:70b", "size_gb": 40, "ram_required": 48, "description": "Llama 3 70B", "tags": ["reasoning"]},
    
    # Dolphin family (Uncensored) - IMPORTANT ADDITIONS
    {"name": "tinydolphin", "size_gb": 0.636, "ram_required": 2, "description": "🐬 TinyDolphin - Ultra-small uncensored model", "tags": ["uncensored", "tiny", "fast", "general"]},
    {"name": "dolphin3", "size_gb": 4.7, "ram_required": 8, "description": "🐬 Dolphin 3.0 - Latest uncensored, based on Llama 3.1", "tags": ["uncensored", "code", "general"]},
    {"name": "dolphin-llama3", "size_gb": 4.7, "ram_required": 8, "description": "🐬 Dolphin 2.9 Llama 3 - Uncensored assistant", "tags": ["uncensored", "general"]},
    {"name": "dolphin-llama3:70b", "size_gb": 40, "ram_required": 48, "description": "🐬 Dolphin Llama 3 70B - Large uncensored", "tags": ["uncensored", "complex"]},
    {"name": "dolphin-mistral", "size_gb": 4.1, "ram_required": 8, "description": "🐬 Dolphin Mistral - Fast uncensored", "tags": ["uncensored", "fast"]},
    {"name": "dolphin-mixtral", "size_gb": 26, "ram_required": 32, "description": "🐬 Dolphin Mixtral 8x7B - Powerful uncensored MoE", "tags": ["uncensored", "complex"]},
    {"name": "dolphin-mixtral:8x22b", "size_gb": 141, "ram_required": 150, "description": "🐬 Dolphin Mixtral 8x22B - Massive uncensored", "tags": ["uncensored", "research"]},
    {"name": "dolphin-phi", "size_gb": 2.3, "ram_required": 4, "description": "🐬 Dolphin Phi - Tiny uncensored", "tags": ["uncensored", "tiny"]},
    {"name": "dolphin-qwen2", "size_gb": 4.4, "ram_required": 8, "description": "🐬 Dolphin Qwen 2 - Multilingual uncensored", "tags": ["uncensored", "multilingual"]},
    
    # DeepSeek R1 family (Reasoning) - NEW ADDITIONS
    {"name": "deepseek-r1", "size_gb": 4.5, "ram_required": 8, "description": "🧠 DeepSeek R1 - Advanced reasoning with CoT", "tags": ["reasoning", "code"]},
    {"name": "deepseek-r1:8b", "size_gb": 4.5, "ram_required": 8, "description": "🧠 DeepSeek R1 8B - Chain-of-thought reasoning", "tags": ["reasoning", "code"]},
    {"name": "deepseek-r1:14b", "size_gb": 8, "ram_required": 16, "description": "🧠 DeepSeek R1 14B - Advanced problem solving", "tags": ["reasoning", "complex"]},
    {"name": "deepseek-r1:32b", "size_gb": 16, "ram_required": 32, "description": "🧠 DeepSeek R1 32B - Research-level reasoning", "tags": ["reasoning", "complex"]},
    {"name": "deepseek-r1:70b", "size_gb": 40, "ram_required": 48, "description": "🧠 DeepSeek R1 70B - Top-tier reasoning", "tags": ["reasoning", "research"]},
    
    # DeepSeek V3
    {"name": "deepseek-v3", "size_gb": 236, "ram_required": 256, "description": "DeepSeek V3 - 671B MoE model", "tags": ["complex", "research"]},
    
    # DeepSeek Coder V2
    {"name": "deepseek-coder-v2", "size_gb": 16, "ram_required": 24, "description": "DeepSeek Coder V2 - Latest code model", "tags": ["code"]},
    {"name": "deepseek-coder-v2:16b", "size_gb": 9, "ram_required": 16, "description": "DeepSeek Coder V2 16B", "tags": ["code"]},
    {"name": "deepseek-coder-v2:236b", "size_gb": 128, "ram_required": 140, "description": "DeepSeek Coder V2 236B - Ultimate coding", "tags": ["code", "complex"]},
    
    # Qwen 2.5 family - NEW ADDITIONS
    {"name": "qwen2.5", "size_gb": 4.4, "ram_required": 8, "description": "Qwen 2.5 - Latest generation", "tags": ["general", "multilingual"]},
    {"name": "qwen2.5:0.5b", "size_gb": 0.4, "ram_required": 2, "description": "Qwen 2.5 0.5B - Tiny", "tags": ["tiny", "fast"]},
    {"name": "qwen2.5:1.5b", "size_gb": 0.9, "ram_required": 3, "description": "Qwen 2.5 1.5B - Small", "tags": ["fast"]},
    {"name": "qwen2.5:3b", "size_gb": 2, "ram_required": 4, "description": "Qwen 2.5 3B - Efficient", "tags": ["fast", "general"]},
    {"name": "qwen2.5:7b", "size_gb": 4.4, "ram_required": 8, "description": "Qwen 2.5 7B - Balanced", "tags": ["general", "multilingual"]},
    {"name": "qwen2.5:14b", "size_gb": 8.9, "ram_required": 16, "description": "Qwen 2.5 14B - Advanced", "tags": ["general", "reasoning"]},
    {"name": "qwen2.5:32b", "size_gb": 20, "ram_required": 32, "description": "Qwen 2.5 32B - Professional", "tags": ["reasoning", "complex"]},
    {"name": "qwen2.5:72b", "size_gb": 43, "ram_required": 48, "description": "Qwen 2.5 72B - Flagship, rivals GPT-4", "tags": ["complex", "reasoning"]},
    
    # Qwen 2.5 Coder
    {"name": "qwen2.5-coder", "size_gb": 4.4, "ram_required": 8, "description": "Qwen 2.5 Coder - Latest code model", "tags": ["code"]},
    {"name": "qwen2.5-coder:1.5b", "size_gb": 1.3, "ram_required": 3, "description": "Qwen 2.5 Coder 1.5B", "tags": ["code", "fast"]},
    {"name": "qwen2.5-coder:7b", "size_gb": 4.4, "ram_required": 8, "description": "Qwen 2.5 Coder 7B - Strong at Python/JS", "tags": ["code"]},
    {"name": "qwen2.5-coder:14b", "size_gb": 8.9, "ram_required": 16, "description": "Qwen 2.5 Coder 14B", "tags": ["code", "complex"]},
    {"name": "qwen2.5-coder:32b", "size_gb": 19, "ram_required": 32, "description": "Qwen 2.5 Coder 32B - Pro coding", "tags": ["code", "complex"]},
    
    # Gemma family
    {"name": "gemma", "size_gb": 4.8, "ram_required": 8, "description": "Google's Gemma base", "tags": ["general"]},
    {"name": "gemma:2b", "size_gb": 1.4, "ram_required": 4, "description": "Gemma 2B - Google's smallest", "tags": ["fast", "general"]},
    {"name": "gemma:7b", "size_gb": 4.8, "ram_required": 8, "description": "Gemma 7B - Good reasoning", "tags": ["general", "reasoning"]},
    {"name": "gemma2", "size_gb": 5.5, "ram_required": 10, "description": "Gemma 2 base model", "tags": ["general"]},
    {"name": "gemma2:2b", "size_gb": 1.6, "ram_required": 4, "description": "Gemma 2 2B - Tiny but capable", "tags": ["fast"]},
    {"name": "gemma2:9b", "size_gb": 5.5, "ram_required": 10, "description": "Gemma 2 9B - Improved performance", "tags": ["general", "reasoning"]},
    {"name": "gemma2:27b", "size_gb": 16, "ram_required": 24, "description": "Gemma 2 27B - Large", "tags": ["reasoning", "complex"]},
    
    # Mistral family
    {"name": "mistral", "size_gb": 4.1, "ram_required": 8, "description": "Mistral base model", "tags": ["fast", "general"]},
    {"name": "mistral:7b", "size_gb": 4.1, "ram_required": 8, "description": "Mistral 7B - Fast and efficient", "tags": ["fast", "general"]},
    {"name": "mistral-nemo", "size_gb": 7.1, "ram_required": 12, "description": "Mistral Nemo - 128k context", "tags": ["long-context"]},
    {"name": "mistral-large", "size_gb": 123, "ram_required": 128, "description": "Mistral Large - Flagship model", "tags": ["complex", "reasoning"]},
    {"name": "mixtral", "size_gb": 26, "ram_required": 32, "description": "Mixtral MoE base", "tags": ["complex"]},
    {"name": "mixtral:8x7b", "size_gb": 26, "ram_required": 32, "description": "Mixtral 8x7B - Very capable MoE", "tags": ["reasoning", "complex"]},
    {"name": "mixtral:8x22b", "size_gb": 141, "ram_required": 150, "description": "Mixtral 8x22B - Large MoE", "tags": ["complex"]},
    
    # Command-R family
    {"name": "command-r", "size_gb": 20, "ram_required": 24, "description": "Cohere Command-R - RAG optimized", "tags": ["general", "rag"]},
    {"name": "command-r:35b", "size_gb": 20, "ram_required": 24, "description": "Command-R 35B - Conversational", "tags": ["chat", "rag"]},
    {"name": "command-r-plus", "size_gb": 59, "ram_required": 64, "description": "Command-R Plus - Large model", "tags": ["complex", "rag"]},
    
    # Code models
    {"name": "codellama", "size_gb": 3.8, "ram_required": 8, "description": "CodeLlama base", "tags": ["code"]},
    {"name": "codellama:7b", "size_gb": 3.8, "ram_required": 8, "description": "CodeLlama 7B - Code generation", "tags": ["code"]},
    {"name": "codellama:13b", "size_gb": 7.4, "ram_required": 16, "description": "CodeLlama 13B - Better code", "tags": ["code"]},
    {"name": "codellama:34b", "size_gb": 19, "ram_required": 32, "description": "CodeLlama 34B - Expert code", "tags": ["code", "complex"]},
    {"name": "codellama:70b", "size_gb": 39, "ram_required": 48, "description": "CodeLlama 70B - Ultimate code model", "tags": ["code", "complex"]},
    {"name": "deepseek-coder", "size_gb": 3.8, "ram_required": 8, "description": "DeepSeek Coder base", "tags": ["code"]},
    {"name": "deepseek-coder:6.7b", "size_gb": 3.8, "ram_required": 8, "description": "DeepSeek Coder 6.7B", "tags": ["code"]},
    {"name": "deepseek-coder:33b", "size_gb": 19, "ram_required": 32, "description": "DeepSeek Coder 33B", "tags": ["code", "complex"]},
    {"name": "codegemma", "size_gb": 4.8, "ram_required": 8, "description": "Google's code model", "tags": ["code"]},
    {"name": "codegemma:7b", "size_gb": 4.8, "ram_required": 8, "description": "CodeGemma 7B", "tags": ["code"]},
    {"name": "starcoder2", "size_gb": 4.0, "ram_required": 8, "description": "StarCoder 2 base", "tags": ["code"]},
    {"name": "starcoder2:3b", "size_gb": 1.7, "ram_required": 4, "description": "StarCoder 2 3B - Fast code", "tags": ["code", "fast"]},
    {"name": "starcoder2:7b", "size_gb": 4.0, "ram_required": 8, "description": "StarCoder 2 7B", "tags": ["code"]},
    {"name": "starcoder2:15b", "size_gb": 9.1, "ram_required": 16, "description": "StarCoder 2 15B", "tags": ["code"]},
    {"name": "codeqwen", "size_gb": 4.5, "ram_required": 8, "description": "Qwen for code", "tags": ["code"]},
    
    # Phi family (Microsoft)
    {"name": "phi3", "size_gb": 2.3, "ram_required": 4, "description": "Phi-3 base", "tags": ["fast", "efficient"]},
    {"name": "phi3:mini", "size_gb": 2.3, "ram_required": 4, "description": "Phi-3 Mini - Efficient 3.8B", "tags": ["fast", "efficient"]},
    {"name": "phi3:medium", "size_gb": 7.9, "ram_required": 12, "description": "Phi-3 Medium 14B", "tags": ["general"]},
    {"name": "phi3.5", "size_gb": 2.2, "ram_required": 4, "description": "Phi-3.5 - Latest version", "tags": ["fast", "efficient"]},
    
    # Vision models
    {"name": "llava", "size_gb": 4.7, "ram_required": 8, "description": "LLaVA base - Vision + Language", "tags": ["vision"]},
    {"name": "llava:7b", "size_gb": 4.7, "ram_required": 8, "description": "LLaVA 7B - Understands images", "tags": ["vision"]},
    {"name": "llava:13b", "size_gb": 8.0, "ram_required": 16, "description": "LLaVA 13B - Better vision", "tags": ["vision"]},
    {"name": "llava:34b", "size_gb": 20, "ram_required": 32, "description": "LLaVA 34B - Best vision model", "tags": ["vision", "complex"]},
    {"name": "bakllava", "size_gb": 4.7, "ram_required": 8, "description": "BakLLaVA - Alternative vision", "tags": ["vision"]},
    {"name": "llava-llama3", "size_gb": 4.7, "ram_required": 8, "description": "LLaVA with Llama 3 base", "tags": ["vision"]},
    {"name": "llava-phi3", "size_gb": 2.9, "ram_required": 6, "description": "LLaVA with Phi-3 - Efficient vision", "tags": ["vision", "fast"]},
    
    # Specialized models
    {"name": "neural-chat", "size_gb": 4.1, "ram_required": 8, "description": "Intel's chat model", "tags": ["chat"]},
    {"name": "starling-lm", "size_gb": 4.1, "ram_required": 8, "description": "Berkeley's RLHF model", "tags": ["chat"]},
    {"name": "zephyr", "size_gb": 4.1, "ram_required": 8, "description": "HuggingFace aligned model", "tags": ["chat", "aligned"]},
    {"name": "openchat", "size_gb": 4.1, "ram_required": 8, "description": "OpenChat model", "tags": ["chat"]},
    {"name": "vicuna", "size_gb": 3.8, "ram_required": 8, "description": "Vicuna base", "tags": ["chat"]},
    {"name": "vicuna:7b", "size_gb": 3.8, "ram_required": 8, "description": "Vicuna 7B chat model", "tags": ["chat"]},
    {"name": "vicuna:13b", "size_gb": 7.4, "ram_required": 16, "description": "Vicuna 13B", "tags": ["chat"]},
    {"name": "orca2", "size_gb": 4.1, "ram_required": 8, "description": "Microsoft Orca 2", "tags": ["reasoning"]},
    {"name": "orca2:7b", "size_gb": 4.1, "ram_required": 8, "description": "Orca 2 7B", "tags": ["reasoning"]},
    {"name": "orca2:13b", "size_gb": 7.4, "ram_required": 16, "description": "Orca 2 13B", "tags": ["reasoning"]},
    {"name": "orca-mini", "size_gb": 2, "ram_required": 4, "description": "Orca Mini 3B", "tags": ["fast"]},
    
    # Math/Science models
    {"name": "mathstral", "size_gb": 4.1, "ram_required": 8, "description": "Math-focused Mistral", "tags": ["math"]},
    {"name": "wizard-math", "size_gb": 4.1, "ram_required": 8, "description": "WizardLM Math", "tags": ["math"]},
    {"name": "wizard-math:7b", "size_gb": 4.1, "ram_required": 8, "description": "WizardMath 7B", "tags": ["math"]},
    {"name": "wizard-math:13b", "size_gb": 7.4, "ram_required": 16, "description": "WizardMath 13B", "tags": ["math"]},
    {"name": "wizard-math:70b", "size_gb": 40, "ram_required": 48, "description": "WizardMath 70B", "tags": ["math", "complex"]},
    {"name": "meditron", "size_gb": 4.1, "ram_required": 8, "description": "Medical model", "tags": ["medical"]},
    {"name": "meditron:7b", "size_gb": 4.1, "ram_required": 8, "description": "Meditron 7B", "tags": ["medical"]},
    {"name": "meditron:70b", "size_gb": 40, "ram_required": 48, "description": "Meditron 70B", "tags": ["medical", "complex"]},
    
    # Other notable models
    {"name": "solar", "size_gb": 6.1, "ram_required": 12, "description": "Upstage Solar", "tags": ["general"]},
    {"name": "yi", "size_gb": 3.5, "ram_required": 8, "description": "Yi base model", "tags": ["general"]},
    {"name": "yi:6b", "size_gb": 3.5, "ram_required": 8, "description": "Yi 6B", "tags": ["general"]},
    {"name": "yi:34b", "size_gb": 19, "ram_required": 32, "description": "Yi 34B", "tags": ["complex"]},
    {"name": "nous-hermes2", "size_gb": 6.1, "ram_required": 12, "description": "Nous Research model", "tags": ["general"]},
    {"name": "openhermes", "size_gb": 4.1, "ram_required": 8, "description": "Open Hermes 2.5", "tags": ["general"]},
    {"name": "stable-code", "size_gb": 1.6, "ram_required": 4, "description": "Stable Code 3B", "tags": ["code", "fast"]},
    {"name": "stable-beluga", "size_gb": 40, "ram_required": 48, "description": "Stable Beluga 70B", "tags": ["complex"]},
    {"name": "wizardlm2", "size_gb": 4.1, "ram_required": 8, "description": "WizardLM 2", "tags": ["general"]},
    {"name": "wizardcoder", "size_gb": 7.4, "ram_required": 16, "description": "WizardCoder", "tags": ["code"]},
    {"name": "yarn-llama2", "size_gb": 7.4, "ram_required": 16, "description": "Yarn Llama 2 - 128k context", "tags": ["long-context"]},
    {"name": "yarn-mistral", "size_gb": 4.1, "ram_required": 8, "description": "Yarn Mistral - 128k context", "tags": ["long-context"]},
    
    # Tiny models
    {"name": "tinyllama", "size_gb": 0.6, "ram_required": 2, "description": "TinyLlama 1.1B", "tags": ["tiny", "fast"]},
    {"name": "tinydolphin", "size_gb": 0.6, "ram_required": 2, "description": "Tiny Dolphin - Uncensored tiny", "tags": ["tiny", "uncensored"]},
    
    # Other language models
    {"name": "aya", "size_gb": 4.8, "ram_required": 8, "description": "Aya multilingual", "tags": ["multilingual"]},
    {"name": "aya:8b", "size_gb": 4.8, "ram_required": 8, "description": "Aya 8B - 101 languages", "tags": ["multilingual"]},
    {"name": "aya:35b", "size_gb": 20, "ram_required": 32, "description": "Aya 35B - Large multilingual", "tags": ["multilingual", "complex"]},
    {"name": "granite", "size_gb": 2.0, "ram_required": 4, "description": "IBM Granite", "tags": ["general"]},
    {"name": "granite:3b", "size_gb": 2.0, "ram_required": 4, "description": "Granite 3B", "tags": ["general"]},
    {"name": "granite:8b", "size_gb": 4.6, "ram_required": 8, "description": "Granite 8B", "tags": ["general"]},
    {"name": "falcon", "size_gb": 4.2, "ram_required": 8, "description": "Falcon base", "tags": ["general"]},
    {"name": "falcon:7b", "size_gb": 4.2, "ram_required": 8, "description": "Falcon 7B", "tags": ["general"]},
    {"name": "falcon:40b", "size_gb": 23, "ram_required": 32, "description": "Falcon 40B", "tags": ["complex"]},
    {"name": "falcon:180b", "size_gb": 100, "ram_required": 120, "description": "Falcon 180B", "tags": ["complex", "research"]},
]

def get_model_info(model_name: str) -> dict:
    """Get info for a specific model"""
    for model in OLLAMA_COMPLETE_REGISTRY:
        if model["name"] == model_name:
            return model
    return None

def get_models_by_tag(tag: str) -> list:
    """Get all models with a specific tag"""
    return [m for m in OLLAMA_COMPLETE_REGISTRY if tag in m.get("tags", [])]

def get_compatible_models(ram_gb: int) -> list:
    """Get models compatible with system RAM"""
    available_ram = max(4, ram_gb - 4)  # Leave 4GB for system
    return [m for m in OLLAMA_COMPLETE_REGISTRY if m["ram_required"] <= available_ram]

def check_model_compatibility(model_name: str, ram_gb: int) -> tuple:
    """Check if model is compatible with system"""
    model = get_model_info(model_name)
    if model:
        available_ram = max(4, ram_gb - 4)
        compatible = model["ram_required"] <= available_ram
        return compatible, model["ram_required"], available_ram
    return True, 0, 0  # Unknown model, assume compatible