"""
Tiered Model Strategy for NOVA 2025
Local Development → Cloud Production scaling strategy
"""

from typing import Dict, List, Optional, Tuple
from ..models import Model, ModelType
from ..legendary.personalities.legendary_tech_minds import LegendaryTechMinds
import logging

class TieredModelStrategy:
    """
    3-Tier model strategy for different deployment scenarios:
    - Tier 1: Ultra Cloud Models (for production cloud deployment)
    - Tier 2: Local Powerhouse Models (for powerful local development)
    - Tier 3: Local Efficient Models (for resource-constrained local dev)
    """
    
    # TIER 1: Ultra Cloud Models (Production/Cloud Deployment)
    TIER1_ULTRA_MODELS = {
        "reasoning_titan": "deepseek-r1:14b",           # 8.5GB - Latest reasoning powerhouse
        "universal_genius": "dolphin-mixtral:8x22b",    # 87GB - Most powerful Dolphin
        "code_virtuoso": "deepseek-coder-v2:16b",       # 9.1GB - Advanced coding specialist
        "creative_master": "dolphin3:8b"                # 4.7GB - Latest Dolphin creative
    }
    
    # TIER 2: Local Powerhouse Models (Strong local development)
    TIER2_LOCAL_POWERHOUSE = {
        "reasoning_titan": "dolphin-mixtral:8x7b",      # 26GB - Powerful reasoning & leadership
        "universal_genius": "wizard-vicuna-uncensored:13b", # 7.4GB - Versatile uncensored
        "code_virtuoso": "deepseek-coder:33b",          # 19GB - Excellent coding
        "creative_master": "dolphin-mistral:7b"         # 4.1GB - Fast creative tasks
    }
    
    # TIER 3: Local Efficient Models (Resource-friendly development)
    TIER3_LOCAL_EFFICIENT = {
        "reasoning_titan": "dolphin-mistral:7b",        # 4.1GB - All-purpose uncensored
        "universal_genius": "llama2-uncensored:7b",     # 3.8GB - Proven uncensored base
        "code_virtuoso": "deepseek-coder:7b",           # 3.8GB - Coding specialist compact
        "creative_master": "dolphin3:8b"                # 4.7GB - Latest creative (shared)
    }
    
    # Model tier sizes for planning
    TIER_SIZES = {
        "tier1_total": 109.3,  # Ultra models total
        "tier2_total": 56.5,   # Powerhouse models total  
        "tier3_total": 16.3    # Efficient models total
    }
    
    # Current tier selection (can be changed based on system)
    def __init__(self, preferred_tier: str = "auto"):
        self.logger = logging.getLogger('NOVA.TieredModelStrategy')
        self.legendary_minds = LegendaryTechMinds()
        self.current_tier = self._determine_tier(preferred_tier)
        self.current_models = self._get_models_for_tier(self.current_tier)
        
    def _determine_tier(self, preferred_tier: str) -> str:
        """Determine optimal tier based on system or preference"""
        if preferred_tier in ["1", "tier1", "cloud", "ultra"]:
            return "tier1"
        elif preferred_tier in ["2", "tier2", "powerhouse", "local_power"]:
            return "tier2"
        elif preferred_tier in ["3", "tier3", "efficient", "local_efficient"]:
            return "tier3"
        else:
            # Auto-detect based on system (simplified heuristic)
            # In practice, could check available RAM, storage, etc.
            return "tier3"  # Default to most compatible
            
    def _get_models_for_tier(self, tier: str) -> Dict[str, str]:
        """Get models for specified tier"""
        if tier == "tier1":
            return self.TIER1_ULTRA_MODELS
        elif tier == "tier2":
            return self.TIER2_LOCAL_POWERHOUSE
        else:
            return self.TIER3_LOCAL_EFFICIENT
    
    # Agent mapping (same across all tiers, models adjust)
    LEGENDARY_AGENT_MAPPING = {
        # Executive Leadership (Reasoning Titan)
        "alexandra_sterling": {
            "model_role": "reasoning_titan", 
            "personalities": ["warren_buffett", "linus_torvalds", "steve_jobs", "jony_ive"],
            "description": "CTO combining business acumen, technical excellence, product vision"
        },
        "marcus_venture": {
            "model_role": "reasoning_titan",
            "personalities": ["steve_jobs", "jeff_bezos", "elon_musk"], 
            "description": "CEO with product vision, customer obsession, first-principles thinking"
        },
        "legendary_cpo": {
            "model_role": "reasoning_titan",
            "personalities": ["steve_jobs", "satya_nadella"],
            "description": "Chief Product Officer with vision and empathetic leadership"
        },
        
        # Product & Design
        "luna_chen": {
            "model_role": "creative_master",
            "personalities": ["jony_ive", "dieter_rams", "paul_rand"],
            "description": "Design genius with minimalist aesthetics and visual impact"
        },
        "david_park": {
            "model_role": "universal_genius", 
            "personalities": ["steve_jobs", "julie_zhuo", "satya_nadella"],
            "description": "Product visionary with user research and empathetic leadership"
        },
        "ui_designer": {
            "model_role": "creative_master",
            "personalities": ["jony_ive", "dieter_rams"],
            "description": "UI specialist focused on beauty and usability"
        },
        "ux_designer": {
            "model_role": "universal_genius",
            "personalities": ["julie_zhuo", "jony_ive"],
            "description": "UX researcher with deep user empathy"
        },
        
        # Engineering Excellence
        "kai_nakamura": {
            "model_role": "code_virtuoso",
            "personalities": ["linus_torvalds", "john_carmack", "jeff_dean"],
            "description": "Senior architect with system efficiency and massive scale expertise"
        },
        "sofia_rodriguez": {
            "model_role": "code_virtuoso", 
            "personalities": ["dan_abramov", "kent_beck"],
            "description": "Full-stack virtuoso focused on developer experience"
        },
        "dr_aisha_patel": {
            "model_role": "reasoning_titan",
            "personalities": ["geoffrey_hinton", "andrej_karpathy"],
            "description": "AI researcher combining deep learning theory with practical engineering"
        },
        "fullstack_developer": {
            "model_role": "code_virtuoso",
            "personalities": ["dan_abramov", "kent_beck"],
            "description": "Full-stack developer with modern practices"
        },
        "backend_engineer": {
            "model_role": "code_virtuoso",
            "personalities": ["jeff_dean", "linus_torvalds"],
            "description": "Backend specialist for scalable systems"
        },
        "frontend_developer": {
            "model_role": "code_virtuoso", 
            "personalities": ["dan_abramov"],
            "description": "Frontend expert with React and modern frameworks"
        },
        "mobile_developer": {
            "model_role": "code_virtuoso",
            "personalities": ["john_carmack", "dan_abramov"],
            "description": "Mobile specialist for iOS/Android"
        },
        
        # Operations & DevOps
        "ryan_kim": {
            "model_role": "code_virtuoso",
            "personalities": ["kelsey_hightower", "adrian_cockcroft"],
            "description": "DevOps wizard with infrastructure automation"
        },
        "devops_engineer": {
            "model_role": "code_virtuoso",
            "personalities": ["kelsey_hightower", "adrian_cockcroft"],
            "description": "Infrastructure and deployment automation specialist"
        },
        "security_expert": {
            "model_role": "reasoning_titan",
            "personalities": ["linus_torvalds", "adrian_cockcroft"],
            "description": "Security architect with system-level thinking"
        },
        
        # Quality & Testing
        "emma_thompson": {
            "model_role": "universal_genius",
            "personalities": ["james_bach", "lisa_crispin"],
            "description": "QA perfectionist with exploratory testing"
        },
        "qa_engineer": {
            "model_role": "universal_genius",
            "personalities": ["james_bach", "lisa_crispin"],
            "description": "Quality assurance with systematic testing approaches"
        },
        
        # Support & Documentation
        "technical_writer": {
            "model_role": "creative_master",
            "personalities": ["paul_rand", "jony_ive"],
            "description": "Technical communication with clarity and visual appeal"
        },
        "customer_success": {
            "model_role": "creative_master",
            "personalities": ["satya_nadella", "jeff_bezos"],
            "description": "Customer-focused support with empathy"
        }
    }
    
    def get_model_for_agent(self, agent_name: str) -> Tuple[str, List[str], str]:
        """Get optimal model and personalities for an agent in current tier"""
        agent_config = self.LEGENDARY_AGENT_MAPPING.get(agent_name)
        
        if not agent_config:
            # Default for unknown agents
            return self.current_models["creative_master"], ["steve_jobs"], "General AI agent"
            
        model_role = agent_config["model_role"]
        model_name = self.current_models[model_role]
        personalities = agent_config["personalities"]
        description = agent_config["description"]
        
        return model_name, personalities, description
    
    def switch_tier(self, new_tier: str) -> bool:
        """Switch to a different tier"""
        try:
            old_tier = self.current_tier
            self.current_tier = self._determine_tier(new_tier)
            self.current_models = self._get_models_for_tier(self.current_tier)
            
            self.logger.info(f"Switched from {old_tier} to {self.current_tier}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch tier: {e}")
            return False
    
    def get_all_tiers_info(self) -> Dict[str, Any]:
        """Get information about all available tiers"""
        return {
            "tier1_ultra": {
                "name": "Ultra Cloud Models",
                "description": "Most powerful models for cloud production deployment",
                "models": self.TIER1_ULTRA_MODELS,
                "total_size_gb": self.TIER_SIZES["tier1_total"],
                "use_case": "Cloud production, maximum capability"
            },
            "tier2_powerhouse": {
                "name": "Local Powerhouse Models", 
                "description": "Strong models for powerful local development",
                "models": self.TIER2_LOCAL_POWERHOUSE,
                "total_size_gb": self.TIER_SIZES["tier2_total"],
                "use_case": "Local development with high-end hardware"
            },
            "tier3_efficient": {
                "name": "Local Efficient Models",
                "description": "Resource-friendly models for any local machine",
                "models": self.TIER3_LOCAL_EFFICIENT, 
                "total_size_gb": self.TIER_SIZES["tier3_total"],
                "use_case": "Local development, resource-constrained systems"
            },
            "current_tier": self.current_tier
        }
    
    def get_download_commands_for_tier(self, tier: str = None) -> List[str]:
        """Get download commands for specific tier"""
        if tier is None:
            tier = self.current_tier
            
        models = self._get_models_for_tier(tier)
        return [f"ollama pull {model}" for model in models.values()]
    
    def get_migration_plan(self, from_tier: str, to_tier: str) -> Dict[str, Any]:
        """Get plan for migrating between tiers"""
        from_models = set(self._get_models_for_tier(from_tier).values())
        to_models = set(self._get_models_for_tier(to_tier).values())
        
        # Models that can be kept
        shared_models = from_models.intersection(to_models)
        
        # Models to download for new tier
        new_models = to_models - from_models
        
        # Models that can be removed from old tier
        removable_models = from_models - to_models
        
        return {
            "shared_models": list(shared_models),
            "models_to_download": list(new_models),
            "models_to_remove": list(removable_models),
            "download_commands": [f"ollama pull {model}" for model in new_models],
            "remove_commands": [f"ollama rm {model}" for model in removable_models]
        }
    
    def validate_models_installed(self, installed_models: List[str]) -> Dict[str, Any]:
        """Check which models are installed for current tier"""
        status = {}
        missing = []
        
        for role, model in self.current_models.items():
            # Check exact match or base name match
            model_installed = any(
                model in installed or installed.startswith(model.split(':')[0])
                for installed in installed_models
            )
            status[role] = model_installed
            if not model_installed:
                missing.append(model)
                
        return {
            "tier": self.current_tier,
            "all_installed": len(missing) == 0,
            "status": status,
            "missing_models": missing,
            "download_commands": [f"ollama pull {model}" for model in missing]
        }
    
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
        
        # Adjust prompt complexity based on current tier
        if self.current_tier == "tier1":
            # More sophisticated prompt for ultra models
            prompt = f"""
Embody the combined wisdom of these legendary minds with deep analysis:
{chr(10).join(personality_styles)}

Core Principles:
{chr(10).join(f"• {principle}" for principle in key_principles[:8])}

Task: {task}

Approach this with the full depth of combined thinking styles. Provide comprehensive analysis, strategic insights, and actionable recommendations. Consider multiple perspectives and long-term implications.
"""
        elif self.current_tier == "tier2":
            # Balanced prompt for powerhouse models
            prompt = f"""
Channel these legendary minds:
{chr(10).join(personality_styles)}

Key Principles:
{chr(10).join(f"• {principle}" for principle in key_principles[:6])}

Task: {task}

Apply the combined thinking styles above. Be insightful, strategic, and practical in your approach.
"""
        else:
            # Concise prompt for efficient models
            prompt = f"""
Think like: {', '.join([mind.split(':')[0] for mind in personality_styles])}

Principles: {', '.join(key_principles[:4])}

Task: {task}

Be direct, practical, and actionable.
"""
        
        return prompt