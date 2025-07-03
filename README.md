# STARKAI - Tony Stark Inspired AI Assistant

A comprehensive AI assistant system inspired by Tony Stark's JARVIS, featuring intelligence gathering, proactive problem-solving, system monitoring, hardware integration, and a distinctive personality.

## 🎯 Vision

STARKAI embodies the innovative spirit of Tony Stark, providing:
- **Proactive Intelligence**: Continuously monitors tech trends and your development environment
- **Confident Problem-Solving**: Decisive, technically-focused assistance with a Stark-like personality
- **Multi-Domain Integration**: Seamlessly connects software development, hardware projects, and intelligence gathering
- **Real-World Impact**: Not just text responses, but actionable solutions and hardware control

## 🏗️ Architecture

### Core Modules

- **LLM Engine** (`core/llm_engine.py`) - OpenAI GPT-4 integration with Tony Stark personality prompting
- **Personality Module** (`core/personality.py`) - Implements confident, proactive, technically-focused traits
- **Intel Collector** (`core/intel_collector.py`) - Gathers intelligence from Reddit, GitHub, and other sources
- **System Hooks** (`core/system_hooks.py`) - Real-time monitoring of files, processes, and system resources
- **Code Fixer** (`core/fixer.py`) - Automated code analysis and improvement suggestions
- **Hardware Helper** (`core/hardware_helper.py`) - Serial communication with Arduino, ESP32, and other devices
- **CLI Interface** (`interface/cli.py`) - Interactive command-line interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM functionality)
- Optional: Reddit, GitHub API credentials for intelligence gathering

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pushthev1be/STARKAI.git
cd STARKAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run STARKAI:
```bash
python main.py --interactive
```

## 🎮 Usage

### Interactive Mode

Start the interactive CLI:
```bash
python main.py -i
```

### Available Commands

- **Chat**: Just type your message for AI assistance
- `/intel [topics...]` - Gather intelligence on specified topics
- `/system` - Show current system status
- `/fix <file>` - Analyze and suggest fixes for code files
- `/hardware <action> <device>` - Control hardware devices
- `help` - Show all available commands
- `exit` - Quit STARKAI

### Example Session

```
🚀 STARKAI Interactive Mode
Type 'help' for commands, 'exit' to quit

🤖 STARK> How can I optimize my Python code?

🎯 From an engineering perspective, let's break this down systematically:

1. **Profile first** - Use cProfile to identify bottlenecks
2. **Optimize algorithms** - Choose the right data structures
3. **Leverage built-ins** - Python's C implementations are faster
4. **Consider async/await** - For I/O bound operations

But here's what I'd do differently next time - implement monitoring from the start so you can catch performance anomalies early.

🤖 STARK> /intel python performance

📊 Intelligence Report:
Reddit trends: 5 items
GitHub trends: 5 items
```

## 🔧 Configuration

### API Keys Setup

1. **OpenAI API**: Required for LLM functionality
   - Get your key from https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

2. **Reddit API**: Optional, for social intelligence gathering
   - Create app at https://www.reddit.com/prefs/apps
   - Add to `.env`: `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`

3. **GitHub API**: Optional, for repository intelligence
   - Generate token at https://github.com/settings/tokens
   - Add to `.env`: `GITHUB_TOKEN=your_token_here`

### Hardware Integration

Connect Arduino or ESP32 devices via serial:
```bash
🤖 STARK> /hardware connect arduino /dev/ttyUSB0
🔌 Device arduino: Connected

🤖 STARK> /hardware read arduino
📡 arduino sensors: {"temperature": 23.5, "humidity": 45.2}
```

## 🧪 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
black . --check
flake8 . --max-line-length=100
```

### Project Structure

```
STARKAI/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── setup.py            # Package configuration
├── .env.example        # Environment template
├── core/               # Core business logic
│   ├── llm_engine.py   # AI communication
│   ├── personality.py  # Tony Stark traits
│   ├── intel_collector.py # Intelligence gathering
│   ├── system_hooks.py # System monitoring
│   ├── fixer.py        # Code analysis
│   └── hardware_helper.py # Device communication
├── interface/          # User interfaces
│   ├── cli.py          # Command-line interface
│   └── voice.py        # Voice interface (planned)
└── config/             # Configuration
    ├── project.yml     # Project settings
    └── creds.json      # API credentials template
```

## 🎭 Personality Features

STARKAI embodies Tony Stark's characteristics:

- **Confidence**: "I know" instead of "I think"
- **Proactivity**: Suggests improvements before you ask
- **Technical Focus**: Engineering-first approach to problems
- **Innovation**: Always thinking several steps ahead
- **Wit**: Charismatic but results-focused communication

## 🔮 Roadmap

- [ ] Voice interface integration
- [ ] Advanced hardware project templates
- [ ] Machine learning model training capabilities
- [ ] Web dashboard for system monitoring
- [ ] Plugin system for custom modules
- [ ] Integration with more development tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Tony Stark's JARVIS from the Marvel Cinematic Universe
- Built with modern Python async/await patterns
- Integrates with leading AI and development platforms

---

*"Sometimes you gotta run before you can walk."* - Tony Stark
