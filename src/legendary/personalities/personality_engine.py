"""
Personality Engine for NOVA
Manages legendary personality selection and prompt enhancement
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from .legendary_personalities import LegendaryPersonality, PERSONALITY_PROFILES, PersonalityTraits
from ...models import Task, TaskComplexity


@dataclass
class PersonalityContext:
    """Context for personality-based processing"""
    task: Task
    personality: LegendaryPersonality
    traits: PersonalityTraits
    reasoning: str


class PersonalityEngine:
    """
    Manages personality selection and prompt enhancement for NOVA
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.PersonalityEngine')
        self.current_mode = LegendaryPersonality.HYBRID
        self.personality_history: List[Tuple[str, LegendaryPersonality]] = []
        self.usage_stats: Dict[LegendaryPersonality, int] = {p: 0 for p in LegendaryPersonality}
        
    def select_personality(self, task: Task) -> Tuple[LegendaryPersonality, str]:
        """
        Select the best personality for a given task
        Returns: (personality, reasoning)
        """
        task_lower = task.content.lower()
        
        # Check for explicit personality requests
        for personality in LegendaryPersonality:
            if personality.value in task_lower:
                reasoning = f"User explicitly requested {personality.value} perspective"
                return personality, reasoning
                
        # Task-based selection
        if any(word in task_lower for word in ['invest', 'business', 'profit', 'market', 'stock']):
            return LegendaryPersonality.BUFFETT, "Business and investment analysis suits Buffett's expertise"
            
        elif any(word in task_lower for word in ['linux', 'kernel', 'system', 'performance', 'optimize']):
            return LegendaryPersonality.LINUS, "System-level programming aligns with Linus's expertise"
            
        elif any(word in task_lower for word in ['design', 'user experience', 'product', 'beautiful']):
            if 'industrial' in task_lower or 'material' in task_lower:
                return LegendaryPersonality.IVE, "Industrial design focus matches Jony Ive's expertise"
            else:
                return LegendaryPersonality.JOBS, "Product vision and user experience is Jobs's domain"
                
        elif any(word in task_lower for word in ['scale', 'mars', 'rocket', 'first principles']):
            return LegendaryPersonality.MUSK, "Ambitious scale and first principles thinking"
            
        elif any(word in task_lower for word in ['customer', 'platform', 'aws', 'cloud']):
            return LegendaryPersonality.BEZOS, "Customer focus and platform thinking"
            
        elif any(word in task_lower for word in ['graphics', 'game', 'vr', 'optimization', '3d']):
            return LegendaryPersonality.CARMACK, "Graphics and optimization expertise"
            
        # Complexity-based fallback
        if task.complexity == TaskComplexity.COMPLEX:
            return LegendaryPersonality.HYBRID, "Complex task benefits from multiple perspectives"
        elif task.complexity == TaskComplexity.SIMPLE:
            return LegendaryPersonality.LINUS, "Simple tasks benefit from direct, practical approach"
        else:
            return self.current_mode, f"Using current mode: {self.current_mode.value}"
            
    def build_prompt(self, task: Task, personality: LegendaryPersonality, context: Dict[str, Any]) -> str:
        """
        Build a personality-enhanced prompt for the LLM
        """
        traits = PERSONALITY_PROFILES[personality]
        
        # Build personality context
        personality_context = f"""You are embodying {traits.name}: {traits.description}

Your thinking style: {traits.thinking_style}
Your communication style: {traits.communication_style}
Your decision-making approach: {traits.decision_making}

Key strengths: {', '.join(traits.strengths)}

Remember to:
- Think and communicate in the style of {traits.name}
- Apply their unique perspective and expertise
- Use their characteristic phrases and approach when appropriate
"""

        # Add some quotes for flavor
        if traits.famous_quotes:
            quote = random.choice(traits.famous_quotes)
            personality_context += f"\n\nAs {traits.name} would say: \"{quote}\"\n"
            
        # Build the full prompt
        prompt = f"""{personality_context}

Context:
- Current task complexity: {task.complexity.value}
- Requires code generation: {task.requires_code_gen}
- System context: {context.get('system_info', 'Mac')}
- User preferences: {context.get('user_preferences', {})}

User request: {task.content}

Please respond as {traits.name} would, applying their unique perspective and expertise to this request."""

        # Track usage
        self.usage_stats[personality] += 1
        self.personality_history.append((task.content[:50], personality))
        
        return prompt
        
    def get_temperature(self, personality: LegendaryPersonality) -> float:
        """Get the appropriate temperature for a personality"""
        return PERSONALITY_PROFILES[personality].temperature
        
    def get_approach(self, personality: LegendaryPersonality, task: Task) -> str:
        """Get how a personality would approach a task"""
        traits = PERSONALITY_PROFILES[personality]
        
        approach_templates = {
            LegendaryPersonality.BUFFETT: f"""
- First, analyze the fundamental value and long-term implications
- Look for sustainable competitive advantages
- Consider the downside risk and margin of safety
- Think in terms of compound returns over time
- Evaluate if this aligns with circle of competence
""",
            LegendaryPersonality.LINUS: f"""
- Start with the simplest solution that could work
- Focus on code quality and maintainability
- Avoid over-engineering and unnecessary complexity
- Test thoroughly and consider edge cases
- Document clearly for other developers
""",
            LegendaryPersonality.JOBS: f"""
- Begin with the user experience and work backwards
- Iterate until it's not just good, but insanely great
- Say no to 1000 things to focus on what matters
- Ensure seamless integration of technology and design
- Create something that delights users
""",
            LegendaryPersonality.IVE: f"""
- Study the materials and manufacturing constraints
- Sketch and prototype multiple iterations
- Remove everything unnecessary until only essence remains
- Consider how form serves function
- Obsess over every detail, even those unseen
""",
            LegendaryPersonality.MUSK: f"""
- Break down to first principles - what's physically possible?
- Set an ambitious timeline and work backwards
- Vertical integration where it provides advantage
- Rapid prototyping and iteration
- Think exponentially, not linearly
""",
            LegendaryPersonality.CARMACK: f"""
- Profile first to find the real bottlenecks
- Optimize the critical path relentlessly
- Use the right algorithm before micro-optimizing
- Consider cache efficiency and memory patterns
- Measure everything, assume nothing
""",
            LegendaryPersonality.HYBRID: f"""
- Analyze from multiple perspectives
- Combine best practices from different domains
- Balance innovation with pragmatism
- Consider both short-term execution and long-term vision
- Synthesize insights from various approaches
"""
        }
        
        return approach_templates.get(personality, "Approach with expertise and wisdom")
        
    def get_stats(self) -> Dict[str, Any]:
        """Get personality usage statistics"""
        total_uses = sum(self.usage_stats.values())
        
        return {
            'current_mode': self.current_mode.value,
            'total_uses': total_uses,
            'usage_breakdown': {
                p.value: {
                    'count': count,
                    'percentage': (count / total_uses * 100) if total_uses > 0 else 0
                }
                for p, count in self.usage_stats.items()
            },
            'recent_history': [
                {'query': q, 'personality': p.value}
                for q, p in self.personality_history[-10:]
            ]
        }
        
    def reset_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {p: 0 for p in LegendaryPersonality}
        self.personality_history = []