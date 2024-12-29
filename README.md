
██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                    



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
├── __main__.py        # Module execution entry point
├── main.py           # Main application logic
├── constants.py      # Configuration and constants
├── formatters.py     # Content formatting
├── parsers.py        # Content parsing
└── utils/
    ├── __init__.py
    ├── ai.py         # AI enhancement
    ├── errors.py     # Error handling
    ├── fetcher.py    # Async content fetching
    └── progress.py   # Progress tracking
```

### Architecture

The project follows these key architectural patterns:
1. Constants Separation - Centralized configuration
2. Security - Secure handling of sensitive data
3. Formatter Chain - Modular content formatting
4. Parser Hierarchy - Flexible content parsing
5. Content Flow Pipeline - Streamlined processing
6. Error Handling - Robust error management
7. Progress Tracking - Real-time user feedback
8. AI Enhancement - Optional content improvement

See `project_docs/patterns.md` for detailed architecture documentation.

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

Configuration is handled through environment variables and an optional `.env` file:

### Together API Configuration

```bash
# Method 1: Environment Variable (recommended)
export TOGETHER_API_KEY='your_api_key'

# Method 2: Environment File
# Create .env in project root:
TOGETHER_API_KEY=your_api_key
```

### Other Settings


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