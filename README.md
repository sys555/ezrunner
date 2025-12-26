# EZ Runner

> **Run any LLM, anywhere, offline.**

Pack any LLM model into an offline-runnable Docker image with one command.

## Quick Start

```bash
# Install
pip install -e .

# Pack a model
ezrunner pack qwen/Qwen-7B-Chat -o model.tar

# Run on offline machine
ezrunner run model.tar
```

## Documentation

- **[User Guide](docs/README.md)** - Features and usage
- **[Architecture](docs/ARCHITECTURE.md)** - Design and implementation
- **[Development](docs/DEVELOPMENT.md)** - Setup dev environment
- **[Code Style](docs/CODE_STYLE.md)** - Coding standards
- **[Testing](docs/TESTING.md)** - Testing strategy
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute

## For Developers

```bash
# Clone repository
git clone https://github.com/yourusername/ezrunner.git
cd ezrunner

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
black src/ tests/
ruff check src/ tests/
mypy src/
```

## License

Apache-2.0