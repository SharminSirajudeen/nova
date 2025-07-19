"""
Legendary AI Company features for NOVA
Integrates AI Software Development Company capabilities
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .personalities.personality_engine import PersonalityEngine
    from .personalities.legendary_personalities import LegendaryPersonality
    from .company.legendary_ventures import LegendaryVentures
    from .agents.base_agent import BaseAgent

__version__ = "1.0.0"
__all__ = [
    'PersonalityEngine',
    'LegendaryPersonality', 
    'LegendaryVentures',
    'BaseAgent'
]

# Lazy imports to avoid circular dependencies
def get_personality_engine():
    from .personalities.personality_engine import PersonalityEngine
    return PersonalityEngine

def get_legendary_ventures():
    from .company.legendary_ventures import LegendaryVentures
    return LegendaryVentures