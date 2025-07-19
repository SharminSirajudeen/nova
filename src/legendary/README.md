# NOVA Legendary Mode - AI Software Development Company

## Overview

The Legendary module adds AI Software Development Company capabilities to NOVA, allowing it to operate as a full AI-powered development team with legendary tech personalities.

## Features

### 1. Dual Mode Operation
- **Personal Mode** (default): Your AI assistant for daily tasks
- **Company Mode**: AI software development company with virtual team

### 2. Legendary Personalities
The company mode embodies the wisdom and expertise of tech legends:

- **Warren Buffett** (CEO) - Business strategy, value analysis
- **Linus Torvalds** (CTO) - Technical architecture, code quality
- **Steve Jobs** (CPO) - Product vision, user experience
- **Jony Ive** (Lead Designer) - Design excellence, minimalism
- **John Carmack** (Lead Engineer) - Performance optimization
- **Elon Musk** (Innovation) - Scale thinking, first principles
- **Jeff Bezos** (Strategy) - Customer focus, platform thinking

### 3. Project Management
- Create and manage software development projects
- AI-driven project analysis and planning
- Automated team formation based on project needs
- Progress tracking and reporting

## Usage

### Switching Modes

```bash
# Check current mode
nova
/mode

# Switch to company mode
/mode company

# Switch back to personal mode
/mode personal
```

### Company Mode Commands

```bash
# Show company dashboard
/company

# Create a new project
/project create Build a real-time chat application with video calling

# List all projects
/project list

# Show project details
/project show <project-id>

# Show AI team
/team
```

### Example Workflow

1. **Switch to Company Mode**
   ```
   /mode company
   ```

2. **Create a Project**
   ```
   /project create Create an AI-powered code review tool that integrates with GitHub
   ```

3. **View Project Details**
   ```
   /project list
   /project show abc123
   ```

4. **Monitor Progress**
   ```
   /company
   ```

## Architecture

### Module Structure
```
src/legendary/
├── personalities/          # Personality engine and traits
│   ├── personality_engine.py
│   └── legendary_personalities.py
├── company/               # Company management
│   ├── legendary_ventures.py
│   └── project_manager.py
└── agents/                # AI agent system (future)
```

### Integration Points

1. **Unified Engine** (`src/core/unified_engine.py`)
   - Combines ReasoningEngine (personal mode) with PersonalityEngine (company mode)
   - Handles mode-based request routing

2. **Enhanced NOVACore** (`src/core/nova_core.py`)
   - Mode switching capability
   - Company initialization
   - Shared model management

3. **Enhanced CLI** (`src/cli/terminal_interface.py`)
   - New commands for mode switching
   - Company-specific command handlers
   - Mode-aware UI elements

## Benefits

1. **Unified System**: One NOVA, multiple capabilities
2. **Shared Resources**: Reuses nova's model management, memory, and automation
3. **Personality-Driven**: Each task gets the perspective of relevant tech legends
4. **Extensible**: Easy to add more personalities or company features

## Future Enhancements

1. **Persistent Projects**: Save projects to disk
2. **Code Generation**: Actual code output for projects
3. **Multi-Agent Collaboration**: Personalities working together
4. **Client Management**: Track multiple clients and projects
5. **Revenue Tracking**: Project financials and metrics

## Technical Notes

- The personality engine selects the best tech legend for each task
- Models are selected based on personality preferences and task requirements
- Company mode uses the same Ollama models as personal mode
- All data is stored locally in `~/.nova/company/`

## Troubleshooting

If company mode doesn't activate:
1. Ensure all imports are working: `python3 test_integration.py`
2. Check logs at `~/.nova/nova.log`
3. Verify Ollama is running and has models installed

## Credits

This integration brings together the best of both nova (personal AI assistant) and nova_claude (AI company) into a unified, powerful system.