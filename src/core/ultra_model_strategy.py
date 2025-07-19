"""
Ultra-Powerful Model Strategy for NOVA 2025
Uses the latest and most powerful uncensored models for maximum versatility
"""

from typing import Dict, List, Optional, Tuple
from ..models import Model, ModelType
from ..legendary.personalities.legendary_tech_minds import LegendaryTechMinds
import logging

class UltraModelStrategy:
    """
    Strategic model selection using the most powerful uncensored models available
    Based on 2025 research of Ollama's latest offerings
    """
    
    # Ultra-Powerful 4-Model System (2025 Edition)
    ULTRA_MODELS = {
        "reasoning_titan": "deepseek-r1:14b",           # 671B - Latest reasoning powerhouse (Jan 2025)
        "universal_genius": "dolphin-mixtral:8x22b",    # 141B - Most powerful Dolphin uncensored
        "code_virtuoso": "deepseek-coder-v2:16b",       # 16B - Advanced coding specialist
        "creative_master": "dolphin3:8b"                # 8B - Latest Dolphin creative (Llama 3.1 based)
    }
    
    # Fallback models for compatibility
    FALLBACK_MODELS = {
        "reasoning_titan": ["deepseek-r1:8b", "dolphin-mixtral:8x7b"],
        "universal_genius": ["dolphin-mixtral:8x7b", "dolphin3:8b"],
        "code_virtuoso": ["deepseek-coder:33b", "dolphin-mixtral:8x7b"],
        "creative_master": ["dolphin-mistral:7b", "wizard-vicuna-uncensored:13b"]
    }
    
    # Agent to model mapping with legendary personalities
    LEGENDARY_AGENT_MAPPING = {
        # Executive Leadership (Reasoning Titan)
        "alexandra_sterling": {
            "model": "reasoning_titan", 
            "personalities": ["warren_buffett", "linus_torvalds", "steve_jobs", "jony_ive"],
            "description": "CTO combining business acumen, technical excellence, product vision, and design sense"
        },
        "marcus_venture": {
            "model": "reasoning_titan",
            "personalities": ["steve_jobs", "jeff_bezos", "elon_musk"], 
            "description": "CEO with product vision, customer obsession, and first-principles thinking"
        },
        "legendary_cpo": {
            "model": "reasoning_titan",
            "personalities": ["steve_jobs", "satya_nadella"],
            "description": "Chief Product Officer with vision and empathetic leadership"
        },
        
        # Product & Design (Universal Genius + Creative Master)
        "luna_chen": {
            "model": "creative_master",
            "personalities": ["jony_ive", "dieter_rams", "paul_rand"],
            "description": "Design genius with minimalist aesthetics and visual impact"
        },
        "david_park": {
            "model": "universal_genius", 
            "personalities": ["steve_jobs", "julie_zhuo", "satya_nadella"],
            "description": "Product visionary with user research and empathetic leadership"
        },
        "ui_designer": {
            "model": "creative_master",
            "personalities": ["jony_ive", "dieter_rams"],
            "description": "UI specialist focused on beauty and usability"
        },
        "ux_designer": {
            "model": "universal_genius",
            "personalities": ["julie_zhuo", "jony_ive"],
            "description": "UX researcher with deep user empathy"
        },
        
        # Engineering Excellence (Code Virtuoso + Reasoning Titan)
        "kai_nakamura": {
            "model": "code_virtuoso",
            "personalities": ["linus_torvalds", "john_carmack", "jeff_dean"],
            "description": "Senior architect with system efficiency and massive scale expertise"
        },
        "sofia_rodriguez": {
            "model": "code_virtuoso", 
            "personalities": ["dan_abramov", "kent_beck"],
            "description": "Full-stack virtuoso focused on developer experience and methodical practices"
        },
        "dr_aisha_patel": {
            "model": "reasoning_titan",
            "personalities": ["geoffrey_hinton", "andrej_karpathy"],
            "description": "AI researcher combining deep learning theory with practical engineering"
        },
        "fullstack_developer": {
            "model": "code_virtuoso",
            "personalities": ["dan_abramov", "kent_beck"],
            "description": "Full-stack developer with modern practices"
        },
        "backend_engineer": {
            "model": "code_virtuoso",
            "personalities": ["jeff_dean", "linus_torvalds"],
            "description": "Backend specialist for scalable systems"
        },
        "frontend_developer": {
            "model": "code_virtuoso", 
            "personalities": ["dan_abramov"],
            "description": "Frontend expert with React and modern frameworks"
        },
        "mobile_developer": {
            "model": "code_virtuoso",
            "personalities": ["john_carmack", "dan_abramov"],
            "description": "Mobile specialist for iOS/Android"
        },
        
        # Operations & DevOps (Code Virtuoso)
        "ryan_kim": {
            "model": "code_virtuoso",
            "personalities": ["kelsey_hightower", "adrian_cockcroft"],
            "description": "DevOps wizard with infrastructure automation and resilient systems"
        },
        "devops_engineer": {
            "model": "code_virtuoso",
            "personalities": ["kelsey_hightower", "adrian_cockcroft"],
            "description": "Infrastructure and deployment automation specialist"
        },
        "security_expert": {
            "model": "reasoning_titan",
            "personalities": ["linus_torvalds", "adrian_cockcroft"],
            "description": "Security architect with system-level thinking"
        },
        
        # Quality & Testing (Universal Genius)
        "emma_thompson": {
            "model": "universal_genius",
            "personalities": ["james_bach", "lisa_crispin"],
            "description": "QA perfectionist with exploratory testing and agile quality practices"
        },
        "qa_engineer": {
            "model": "universal_genius",
            "personalities": ["james_bach", "lisa_crispin"],
            "description": "Quality assurance with systematic testing approaches"
        },
        
        # Support & Documentation (Creative Master)
        "technical_writer": {
            "model": "creative_master",
            "personalities": ["paul_rand", "jony_ive"],
            "description": "Technical communication with clarity and visual appeal"
        },
        "customer_success": {
            "model": "creative_master",
            "personalities": ["satya_nadella", "jeff_bezos"],
            "description": "Customer-focused support with empathy"
        }
    }
    
    # Task-based intelligent routing
    TASK_ROUTING = {
        "deep_reasoning": "reasoning_titan",      # Complex analysis, strategy, research
        "system_architecture": "code_virtuoso",   # Technical design, scaling, performance  
        "business_strategy": "reasoning_titan",   # Market analysis, growth, investment
        "product_design": "universal_genius",     # Product decisions, user experience
        "visual_design": "creative_master",       # UI, graphics, aesthetics
        "coding": "code_virtuoso",               # Programming, debugging, implementation
        "ai_research": "reasoning_titan",        # Machine learning, algorithms, innovation
        "devops": "code_virtuoso",              # Infrastructure, deployment, automation
        "testing": "universal_genius",           # Quality assurance, exploratory testing
        "documentation": "creative_master",      # Writing, tutorials, communication
        "general": "creative_master"             # Quick tasks, general queries
    }
    
    # Model size estimations (in GB)
    MODEL_SIZES = {
        "deepseek-r1:14b": 8.5,           # Compact but powerful
        "dolphin-mixtral:8x22b": 87.0,    # Largest, most capable
        "deepseek-coder-v2:16b": 9.1,     # Specialized coding
        "dolphin3:8b": 4.7,              # Fast creative
        "total_optimized": 109.3          # Total for all 4 models
    }
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.UltraModelStrategy')
        self.legendary_minds = LegendaryTechMinds()
        
    def get_model_for_agent(self, agent_name: str) -> Tuple[str, List[str], str]:
        """Get optimal model and personalities for an agent"""
        agent_config = self.LEGENDARY_AGENT_MAPPING.get(agent_name)
        
        if not agent_config:
            # Default for unknown agents
            return self.ULTRA_MODELS["creative_master"], ["steve_jobs"], "General AI agent"
            
        model_type = agent_config["model"]
        model_name = self.ULTRA_MODELS[model_type]
        personalities = agent_config["personalities"]
        description = agent_config["description"]
        
        return model_name, personalities, description
    
    def get_model_for_task(self, task_type: str, complexity: str = "medium") -> str:
        """Get optimal model for a specific task"""
        # Route based on task type
        model_type = self.TASK_ROUTING.get(task_type.lower(), "creative_master")
        
        # Upgrade model for complex tasks
        if complexity == "complex":
            if model_type == "creative_master":
                model_type = "universal_genius"
            elif model_type == "universal_genius" and task_type in ["deep_reasoning", "ai_research"]:
                model_type = "reasoning_titan"
                
        return self.ULTRA_MODELS[model_type]
    
    def build_personality_prompt(self, personalities: List[str], task: str) -> str:
        """Build a prompt that embodies multiple personalities"""
        all_minds = self.legendary_minds.get_all_minds()
        
        personality_styles = []
        key_principles = []
        
        for personality in personalities:
            if personality in all_minds:
                mind = all_minds[personality]
                personality_styles.append(f"{mind.name}: {mind.thinking_style}")
                key_principles.extend(mind.key_principles[:2])  # Top 2 principles each
        
        prompt = f"""
Embody the combined wisdom of these legendary minds:
{chr(10).join(personality_styles)}

Key Principles to Apply:
{chr(10).join(f"• {principle}" for principle in key_principles[:6])}

Task: {task}

Approach this with the combined thinking styles above. Be direct, insightful, and actionable.
"""
        return prompt
    
    def get_fallback_chain(self, primary_model: str) -> List[str]:
        """Get fallback models if primary fails"""
        # Find which model type this is
        for model_type, model_name in self.ULTRA_MODELS.items():
            if model_name == primary_model:
                return self.FALLBACK_MODELS.get(model_type, [])
        return list(self.ULTRA_MODELS.values())
    
    def get_download_commands(self) -> List[str]:
        """Get ollama pull commands for all ultra models"""
        return [f"ollama pull {model}" for model in self.ULTRA_MODELS.values()]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model strategy information"""
        return {
            "strategy": "Ultra-Powerful 4-Model System (2025 Edition)",
            "total_size_gb": self.MODEL_SIZES["total_optimized"],
            "models": {
                name: {
                    "model": model,
                    "size_gb": self.MODEL_SIZES.get(model, "Unknown"),
                    "purpose": purpose
                }
                for name, model in self.ULTRA_MODELS.items()
                for purpose in [self._get_model_purpose(name)]
            },
            "legendary_agents": len(self.LEGENDARY_AGENT_MAPPING),
            "total_personalities": len(self.legendary_minds.get_all_minds()),
            "hybrid_personalities": len(self.legendary_minds.get_hybrid_personalities())
        }
    
    def _get_model_purpose(self, model_type: str) -> str:
        """Get the purpose description for a model type"""
        purposes = {
            "reasoning_titan": "Complex reasoning, strategy, AI research (DeepSeek R1 - 2025)",
            "universal_genius": "Universal problem solving, product design (Dolphin Mixtral 8x22B)",
            "code_virtuoso": "Coding, architecture, engineering (DeepSeek Coder V2)",
            "creative_master": "Design, writing, quick tasks (Dolphin 3.0 Llama 3.1)"
        }
        return purposes.get(model_type, "General purpose")
    
    def validate_models_installed(self, installed_models: List[str]) -> Dict[str, bool]:
        """Check which ultra models are installed"""
        status = {}
        for role, model in self.ULTRA_MODELS.items():
            # Check exact match or base name match
            model_installed = any(
                model in installed or installed.startswith(model.split(':')[0])
                for installed in installed_models
            )
            status[role] = model_installed
        return status