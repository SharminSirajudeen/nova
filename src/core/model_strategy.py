"""
Model Reusability Strategy for NOVA
Minimizes model downloads while maximizing capabilities
"""

from typing import Dict, List, Optional
from ..models import Model, ModelType
import logging

class ModelStrategy:
    """Strategic model selection for agent reusability"""
    
    # Core 3-model system
    CORE_MODELS = {
        "universal": "dolphin-mixtral:8x7b",      # 47B - Universal powerhouse
        "technical": "deepseek-coder:33b",        # 33B - Code specialist  
        "creative": "dolphin-mistral:7b"          # 7B - Fast creative
    }
    
    # Agent to model mapping
    AGENT_MODEL_MAP = {
        # Executive & Senior (Universal Model)
        "legendary_ceo": "universal",
        "legendary_cto": "universal", 
        "chief_product_officer": "universal",
        "senior_architect": "universal",
        "ai_researcher": "universal",
        "product_manager": "universal",
        "business_analyst": "universal",
        "security_expert": "universal",
        
        # Engineering (Technical Model)
        "fullstack_developer": "technical",
        "backend_engineer": "technical",
        "frontend_developer": "technical",
        "mobile_developer": "technical",
        "devops_engineer": "technical",
        "qa_engineer": "technical",
        "performance_engineer": "technical",
        
        # Design & Support (Creative Model)
        "ui_designer": "creative",
        "ux_designer": "creative",
        "product_designer": "creative",
        "technical_writer": "creative",
        "customer_success": "creative",
        "junior_developer": "creative"
    }
    
    # Task-based routing
    TASK_ROUTING = {
        "architecture": "universal",
        "business_analysis": "universal",
        "coding": "technical",
        "debugging": "technical",
        "design": "creative",
        "documentation": "creative",
        "general": "creative"  # Start with fast model
    }
    
    # Personality prompt modifiers
    PERSONALITY_PROMPTS = {
        "buffett": {
            "style": "Think like Warren Buffett - focus on long-term value, margin of safety, and sustainable competitive advantages. Be analytical and patient.",
            "preferred_model": "universal"
        },
        "jobs": {
            "style": "Channel Steve Jobs - obsess over user experience, demand perfection, think different. Simplicity is the ultimate sophistication.",
            "preferred_model": "universal"
        },
        "linus": {
            "style": "Embody Linus Torvalds - be technically rigorous, efficiency-focused, and brutally honest. Code quality matters above all.",
            "preferred_model": "technical"
        },
        "ive": {
            "style": "Think like Jony Ive - focus on design purity, emotional connection, and the intersection of technology and liberal arts.",
            "preferred_model": "creative"
        },
        "musk": {
            "style": "Channel Elon Musk - think from first principles, aim for 10x improvements, move fast and iterate. Make the impossible possible.",
            "preferred_model": "universal"
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.ModelStrategy')
        self._model_cache = {}
        
    def get_model_for_agent(self, agent_name: str) -> str:
        """Get the optimal model for a specific agent"""
        model_type = self.AGENT_MODEL_MAP.get(agent_name, "creative")
        return self.CORE_MODELS[model_type]
        
    def get_model_for_task(self, task_type: str) -> str:
        """Get the optimal model for a task type"""
        model_type = self.TASK_ROUTING.get(task_type.lower(), "creative")
        return self.CORE_MODELS[model_type]
        
    def get_personality_prompt(self, personality: str) -> tuple[str, str]:
        """Get personality styling prompt and preferred model"""
        personality_data = self.PERSONALITY_PROMPTS.get(
            personality.lower(), 
            self.PERSONALITY_PROMPTS["buffett"]
        )
        
        model_type = personality_data["preferred_model"]
        model_name = self.CORE_MODELS[model_type]
        
        return personality_data["style"], model_name
        
    def get_fallback_chain(self, primary_model: str) -> List[str]:
        """Get fallback models if primary fails"""
        if primary_model == self.CORE_MODELS["universal"]:
            return [
                self.CORE_MODELS["technical"],
                self.CORE_MODELS["creative"]
            ]
        elif primary_model == self.CORE_MODELS["technical"]:
            return [
                self.CORE_MODELS["universal"],
                self.CORE_MODELS["creative"]
            ]
        else:  # creative
            return [
                self.CORE_MODELS["universal"],
                self.CORE_MODELS["technical"]
            ]
            
    def estimate_total_size(self) -> Dict[str, float]:
        """Estimate total model sizes"""
        return {
            self.CORE_MODELS["universal"]: 26.0,  # GB
            self.CORE_MODELS["technical"]: 19.0,  # GB
            self.CORE_MODELS["creative"]: 4.1,    # GB
            "total": 49.1  # GB total vs 300+ GB for all models
        }
        
    def get_download_commands(self) -> List[str]:
        """Get ollama pull commands for all core models"""
        return [
            f"ollama pull {model}" 
            for model in self.CORE_MODELS.values()
        ]
        
    def validate_models_installed(self, installed_models: List[str]) -> Dict[str, bool]:
        """Check which core models are installed"""
        status = {}
        for role, model in self.CORE_MODELS.items():
            status[role] = model in installed_models
        return status