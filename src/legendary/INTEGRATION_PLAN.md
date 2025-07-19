# NOVA + NOVA_CLAUDE Integration Plan

## Overview
This plan outlines the integration of nova_claude's AI Software Development Company features into the existing nova personal assistant, creating a unified system that can operate in both personal assistant and company modes.

## Architecture Changes

### 1. Directory Structure
```
nova/
├── src/
│   ├── legendary/              # New: Company features
│   │   ├── __init__.py
│   │   ├── company/            # Company management
│   │   │   ├── __init__.py
│   │   │   ├── legendary_ventures.py
│   │   │   ├── project_manager.py
│   │   │   └── workflow_engine.py
│   │   ├── agents/             # AI agent personalities
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py
│   │   │   ├── executive_agents.py
│   │   │   ├── engineering_agents.py
│   │   │   ├── design_agents.py
│   │   │   └── operations_agents.py
│   │   └── personalities/      # Personality engine
│   │       ├── __init__.py
│   │       ├── personality_engine.py
│   │       └── legendary_personalities.py
│   ├── core/                   # Modified: Enhanced core
│   │   ├── nova_core.py        # Modified to support modes
│   │   └── unified_engine.py   # New: Unified reasoning + personalities
│   └── cli/                    # Modified: Enhanced CLI
│       └── terminal_interface.py # Modified to support mode switching

```

### 2. Core Integration Points

#### A. Mode System
- Add `--mode` flag to nova CLI (personal/company)
- Default mode: personal (current behavior)
- Company mode: Activates AI development company features

#### B. Unified Reasoning Engine
- Merge nova's ReasoningEngine with nova_claude's personality system
- Create UnifiedEngine that:
  - Uses ReasoningEngine for personal mode
  - Uses PersonalityEngine for company mode
  - Shares model management between both

#### C. Model Management
- Use existing nova's AdaptiveModelManager
- Extend to support personality-based model selection
- Share Ollama integration

## Implementation Steps

### Phase 1: Foundation (Files to Create)

1. **Initialize Legendary Module**
   - Create `__init__.py` files
   - Set up proper imports

2. **Port Personality System**
   - Port PersonalityEngine from nova_claude
   - Adapt to use nova's existing model manager
   - Create legendary_personalities.py

3. **Port Agent System**
   - Create base_agent.py
   - Port executive, engineering, design, operations agents
   - Adapt to use nova's automation layer

### Phase 2: Core Integration

1. **Enhance NOVACore**
   - Add mode switching capability
   - Add company initialization
   - Route requests based on mode

2. **Create Unified Engine**
   - Combines ReasoningEngine + PersonalityEngine
   - Handles mode-based processing
   - Shares context and memory

3. **Update CLI**
   - Add --mode flag
   - Add company-specific commands
   - Maintain backward compatibility

### Phase 3: Company Features

1. **Port Company Management**
   - Port LegendaryVentures class
   - Port ProjectManager
   - Port WorkflowEngine

2. **Integrate with Nova Systems**
   - Use nova's memory system for company data
   - Use nova's automation for actions
   - Use nova's storage for persistence

### Phase 4: Testing & Polish

1. **Test Mode Switching**
2. **Test Company Operations**
3. **Ensure Personal Mode Unchanged**
4. **Update Documentation**

## Key Integration Files

### 1. src/legendary/__init__.py
```python
"""Legendary AI Company features for NOVA"""
from .personalities.personality_engine import PersonalityEngine
from .company.legendary_ventures import LegendaryVentures

__all__ = ['PersonalityEngine', 'LegendaryVentures']
```

### 2. src/core/unified_engine.py
```python
"""Unified reasoning engine supporting both personal and company modes"""
# Combines ReasoningEngine + PersonalityEngine
```

### 3. Modified src/core/nova_core.py
```python
# Add mode support
self.mode = 'personal'  # or 'company'
self.company = None  # LegendaryVentures instance when in company mode
```

### 4. Modified src/cli/terminal_interface.py
```python
# Add mode switching command
# Add company-specific commands when in company mode
```

## Command Structure

### Personal Mode (Default)
```bash
nova "help me with..."  # Current behavior
```

### Company Mode
```bash
nova --mode company start
nova --mode company create-project "Build an AI chatbot"
nova --mode company list-agents
nova --mode company show-project <id>
```

### Mode Switching
```bash
nova switch-mode company
nova switch-mode personal
```

## Benefits

1. **Unified System**: One nova, multiple capabilities
2. **Shared Resources**: Model management, memory, automation
3. **Backward Compatible**: Personal mode unchanged
4. **Extensible**: Easy to add more modes/features
5. **Efficient**: Reuses existing nova infrastructure

## Next Steps

1. Create base legendary module structure
2. Port personality engine
3. Create unified engine
4. Modify nova_core for mode support
5. Update CLI with new commands
6. Test integration thoroughly