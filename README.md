# Hunter

![Build Status](https://img.shields.io/github/actions/workflow/status/joenandez/codename_hunter/python-package.yml?branch=main&style=for-the-badge)
![License](https://img.shields.io/github/license/joenandez/codename_hunter?style=for-the-badge)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge)
![Code Style](https://img.shields.io/badge/code%20style-flake8-black?style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/joenandez/codename_hunter/dev?style=for-the-badge)


██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

**Hunter** is a powerful Python tool designed to effortlessly extract and enhance Markdown content from web pages. Whether you're a developer, content creator, or documentation specialist, Hunter streamlines the process of converting web content into clean, well-formatted Markdown, complete with optional AI-powered enhancements.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🔍 **Smart Content Extraction**: Seamlessly extract structured content (headings, paragraphs, lists, code blocks, links, images) from any web page
- 🤖 **AI-Powered Enhancement**: Optional integration with Together.ai to automatically refine and enhance Markdown formatting
- 📋 **Clipboard Integration**: Instantly copy the processed Markdown content to your clipboard



## Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Install from PyPI

```bash
pip install hunter
```

### Install from Source

```bash
git clone https://github.com/joenandez/codename_hunter.git
cd codename_hunter
pip install -e .
```

## Usage

Hunter provides a simple command-line interface to extract and enhance Markdown content from web pages.

### Basic Usage

```bash
# Extract and enhance content from a URL
hunter https://example.com/article

# Extract without AI enhancement
hunter https://example.com/article --no-enhance

# Extract without copying to clipboard
hunter https://example.com/article --no-copy
```

### Command Options

- `--no-enhance`: Disable AI-powered content enhancement
- `--no-copy`: Disable automatic copying to clipboard

## Configuration

Hunter uses environment variables and an optional `.env` file for configuration.

### Together AI Configuration

To enable AI-powered enhancements, you need a Together.ai API key.

#### Method 1: Environment Variable (Recommended)

```bash
export TOGETHER_API_KEY='your_api_key_here'  # On Windows: set TOGETHER_API_KEY=your_api_key_here
```

#### Method 2: .env File

Create a `.env` file in your working directory:

```env
TOGETHER_API_KEY=your_api_key_here
```

### Additional Settings

```env
# Model Selection
TOGETHER_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Token Limits
TOGETHER_MAX_TOKENS=4000

# Temperature Setting
TOGETHER_TEMPERATURE=0.1

# Output Format
OUTPUT_FORMAT=markdown

# Console Style (dark/light)
CONSOLE_STYLE=dark
```

## Development

### Setup Development Environment

1. Clone the repository
```bash
git clone https://github.com/joesuspense/hunter.git
cd hunter
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies
```bash
pip install -e ".[dev]"
```

### Project Structure

```
hunter/
├── hunter/
│   ├── __init__.py
│   ├── main.py
│   ├── constants.py
│   ├── formatters.py
│   └── utils/
│       ├── ai.py
│       ├── errors.py
│       ├── fetcher.py
│       └── progress.py
├── tests/
│   ├── test_formatters.py
│   └── test_utils.py
├── README.md
└── pyproject.toml
```

## Testing

Run the test suite:

```bash
pytest
```

## Contributing

This project is currently in a read-only state and is not accepting pull requests. However, we welcome:

- Bug reports and feature requests through GitHub Issues
- Questions and discussions in the Issues section
- Using and forking the project for your own needs

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details about this policy and how to effectively report issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.