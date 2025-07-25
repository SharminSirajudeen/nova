# NOVA - Neural Optimization & Versatile Automation

Your AI co-founder that embodies the unified genius of Linus Torvalds, Steve Jobs, and Jony Ive.

## ⚡ Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/SharminSirajudeen/nova/main/install.sh | bash
```

Then open a new terminal and run:
```bash
nova
```

## 🎯 What is NOVA?

NOVA is an intelligent AI assistant that:
- **Detects your Mac hardware** and adapts automatically
- **Uses hybrid LLM routing** (local + cloud) to stay under $10/month
- **Remembers conversations** and learns your preferences
- **Controls your Mac** via AppleScript, Terminal, and UI automation
- **Supports voice commands** and visual analysis
- **Works like Claude Code** - just run `nova` from anywhere

## 🔧 Features

- **🧠 Smart System Detection**: Auto-detects M1/M2/M3/M4 chips and capabilities
- **💰 Cost Optimization**: Hybrid routing keeps costs under $10/month
- **🎙️ Voice Interface**: Voice commands and text-to-speech
- **📷 Visual Analysis**: Screenshot analysis and automation
- **💾 Persistent Memory**: Learns from every interaction
- **🔄 External Storage**: Supports external drives for AI models
- **⚡ Real-time AI**: All responses generated by AI, not scripts

## 🚀 Usage

After installation:

### Interactive Mode
```bash
nova
```

### Direct Commands
```bash
nova "create a Python todo app"
nova "organize my downloads folder"
nova "what's my system performance tier?"
```

### Special Commands
- `/help` - Show all commands
- `/status` - System status
- `/models` - Available AI models
- `/voice` - Toggle voice mode
- `/screenshot` - Take and analyze screenshot
- `/benchmark` - Run system benchmark

## 🏗️ Architecture

```
nova/
├── nova_core.py              # Main entry point
├── install.sh                # One-line installer
├── requirements.txt          # Python dependencies
└── src/
    ├── ai/                   # AI reasoning engine
    ├── automation/           # Mac automation
    ├── cli/                  # Terminal interface
    ├── core/                 # System analysis & storage
    ├── memory/               # Persistent memory
    ├── models/               # Data models
    ├── setup/                # Interactive setup
    ├── utils/                # Helper utilities
    └── voice/                # Voice interface
```

## 🎨 Design Philosophy

NOVA embodies three legendary minds:
- **Linus Torvalds**: Technical precision and efficiency
- **Steve Jobs**: Product vision and user experience
- **Jony Ive**: Design perfection and aesthetic

All unified in one intelligence that thinks, reasons, and creates in real-time.

## 🔐 Privacy & Security

- All data stored locally in `~/.nova/`
- Optional external storage support
- Encrypted sensitive data
- No telemetry or tracking
- You own your data

## 🛠️ Requirements

- macOS 10.15 or later
- Python 3.9 or later
- 8GB+ RAM (16GB+ recommended)
- 10GB+ free storage (more for AI models)

## 📚 Documentation

- [Installation Guide](install.sh)
- [Architecture Overview](src/)

## 🤝 Contributing

NOVA is designed to be your personal AI co-founder. While the core is complete, contributions for new features and improvements are welcome.

## 📄 License

[MIT License](LICENSE)

---

**NOVA learns from every interaction and becomes more capable over time. Build something amazing together.** 🚀
