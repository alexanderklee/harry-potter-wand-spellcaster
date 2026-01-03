# Contributing to Wand Spellcaster

Thank you for your interest in contributing! This project welcomes contributions of all kinds.

## Ways to Contribute

### 🐛 Bug Reports
- Check existing issues first to avoid duplicates
- Include your hardware setup (Pi model, camera, display)
- Provide steps to reproduce the issue
- Include relevant log output

### ✨ Feature Requests
- Open an issue describing the feature
- Explain the use case and why it would be useful
- Consider if it fits Phase 1 (single player) or Phase 2 (voice/multiplayer)

### 🔧 Code Contributions

#### Getting Started
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/wand-spellcaster.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test on actual hardware if possible
6. Submit a Pull Request

#### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and reasonably sized
- Comment complex logic

#### Testing
```bash
# Run any tests (if available)
python -m pytest tests/

# Test on hardware
python src/main.py --debug
```

### 📖 Documentation
- Fix typos or unclear explanations
- Add examples or diagrams
- Translate documentation
- Improve setup instructions

### 🎨 Design Contributions
- 3D printable enclosure designs
- Improved spell gesture patterns
- Display themes
- Hardware mounting solutions

## Areas Needing Help

### High Priority
- [ ] Better spell recognition training data
- [ ] Pi Zero 2 W performance optimization
- [ ] Additional display support (e-ink, LED matrix)

### Phase 2 Implementation
- [ ] Text-to-speech integration (`voice_manager.py`)
- [ ] Multiplayer networking (`multiplayer_manager.py`, `network_sync.py`)
- [ ] Duel resolution system

### Nice to Have
- [ ] Web-based configuration interface
- [ ] Custom spell training UI
- [ ] Integration with home automation (Home Assistant, etc.)
- [ ] Mobile app for spell reference

## Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Test your changes** on real hardware if possible
3. **Keep commits focused** - one feature/fix per commit
4. **Write a clear PR description** explaining what and why
5. **Link related issues** using "Fixes #123" or "Relates to #456"

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers warmly
- Focus on constructive feedback
- Keep discussions on-topic

## Questions?

- Open an issue for project-related questions
- Tag with `question` label

---

*"Help will always be given at Hogwarts to those who ask for it."* — Albus Dumbledore
