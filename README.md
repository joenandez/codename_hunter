# Codename Hunter

A powerful tool for extracting and enhancing markdown content from web pages.

## Features

- 🔍 Smart content extraction from web pages
- 🎨 Markdown formatting with code block language detection
- 🤖 Optional AI-powered content enhancement
- 📋 Clipboard integration
- 📊 Progress tracking
- 🎯 Rich console output

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/codename_hunter.git
cd codename_hunter

# Install in development mode
pip install -e .

# Or install directly from git
pip install git+https://github.com/yourusername/codename_hunter.git
```

## Usage

Basic usage:
```bash
# Process a URL (simplest form)
hunter https://example.com

# Alternative forms also supported:
hunter url https://example.com
hunter uri https://example.com

# Or using Python module form
python -m hunter https://example.com
python -m hunter url https://example.com
```

Options:
- `--no-enhance`: Disable AI enhancement
- `--no-copy`: Disable clipboard copy

Examples:
```bash
# Extract and format content (with defaults)
hunter https://example.com/article

# Process without AI enhancement
hunter https://example.com/article --no-enhance

# Process without copying to clipboard
hunter https://example.com/article --no-copy

```

## Development

### Project Structure

```
hunter/
├── __init__.py
├── __main__.py     # Module execution entry point
├── main.py         # Main entry point and CLI
├── constants.py    # Configuration and constants
├── formatters.py   # Content formatting
├── parsers.py      # Content extraction
└── utils.py        # Utilities and helpers

tests/
└── test_*.py       # Test files
```

### Architecture

The project follows these key architectural patterns:
1. Constants Separation
2. Formatter Chain
3. Parser Hierarchy
4. Content Flow Pipeline
5. Error Handling
6. Progress Tracking
7. AI Enhancement
8. Testing Strategy
9. CLI Interface
10. Main Application Facade

See `patterns.md` for detailed architecture documentation.

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_parsers.py

# Run with coverage
pytest --cov=src tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Configuration

There are three ways to configure your Together API key and other settings:

### 1. Environment Variable (Highest Priority)
```bash
# Set for current session
export TOGETHER_API_KEY='your_api_key'

# Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export TOGETHER_API_KEY="your_api_key"' >> ~/.zshrc
```

### 2. Configuration Files
The system checks configuration files in the following order:

1. User config: `~/.config/hunter/config.ini`
2. Local config: `./config/config.ini`
3. Default config: `./config/config.ini.template`

To set up your configuration:
```bash
# Option 1: User-specific configuration (recommended)
mkdir -p ~/.config/hunter
cp config/config.ini.template ~/.config/hunter/config.ini
nano ~/.config/hunter/config.ini

# Option 2: Local project configuration
cp config/config.ini.template config/config.ini
nano config/config.ini
```

### Configuration Priority
1. Environment variables (highest priority)
2. User config file (`~/.config/hunter/config.ini`)
3. Local config file (`./config/config.ini`)
4. Default config file (`./config/config.ini.template`)

### Other Configuration Options
All configuration options can be set via environment variables or config files:

Environment Variables:
- `TOGETHER_API_KEY`: Your Together.ai API key
- `HUNTER_OUTPUT_FORMAT`: Output format (default: markdown)
- `HUNTER_CONSOLE_STYLE`: Console theme (dark/light)

Config File Sections:
```ini
[api]
together_api_key = your_api_key

[output]
format = markdown
style = dark
```

See `config/config.ini.template` for all configuration options and their documentation.

## Performance

Benchmarks for common operations:
- Content extraction: ~1-2s
- Markdown formatting: ~0.1s
- AI enhancement: ~2-3s (when enabled)

## License

MIT License - see LICENSE file for details.

## Credits

Built with:
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Rich](https://rich.readthedocs.io/)
- [Requests](https://requests.readthedocs.io/)
- [PyPerClip](https://pypi.org/project/pyperclip/) 