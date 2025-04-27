# Contributing to Self-Realization Bot

Thank you for your interest in contributing to Self-Realization Bot! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Test your changes
5. Submit a pull request

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/selfrealization_bot.git
cd selfrealization_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your bot token:
```
BOT_TOKEN=your_bot_token
LOG_LEVEL=DEBUG
```

5. Run the bot:
```bash
python bot.py
```

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request
- Update documentation as needed

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with details of changes
3. The PR must pass all CI checks
4. The PR must be reviewed and approved by at least one maintainer

## Questions?

If you have any questions, feel free to open an issue or contact the maintainers. 