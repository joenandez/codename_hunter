# Changelog

## [0.1.3] - 2024-01-01

### Fixed
- Fixed article parsing bug affecting content extraction

## [0.1.2] - 2024-01-02

### Fixed
- Enhanced main content detection algorithm in HTML parser with multi-strategy approach:
  - Added HTML5 semantic `<main>` tag support
  - Improved detection using content-related IDs
  - Added fallback strategies with class names and `<article>` tags
  - Final fallback to `<body>` tag
  - Added comprehensive test coverage

## [0.1.1] - 2024-01-02

### Fixed
- Fixed package structure to properly include the `hunter.utils` subpackage when installing from PyPI
- Updated package configuration in pyproject.toml to ensure all submodules are included in the distribution

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Web page content extraction to Markdown
- AI-powered content enhancement via Together.ai
- Clipboard integration
- File saving with automatic naming 