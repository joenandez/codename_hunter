I'll analyze the codebase and create a patterns document that explains how these components work together.

Search files...


Based on my analysis of the codebase and refactoring plan, I'll create a patterns document that explains how the components work together:

# Hunter.py Architecture Patterns

## Overview
Hunter.py is being refactored from a monolithic script into a modular, maintainable system for extracting and formatting markdown content from web pages. The architecture follows several key patterns:

## 1. Constants Separation Pattern
Located in `constants.py`, this pattern centralizes all configuration and constant values:
- Regular expression patterns for text cleanup
- HTML element skip lists
- Language detection hints
- Content type enums
- API configurations

This separation allows for easy maintenance and configuration changes without touching business logic.

## 2. Formatter Chain Pattern
Implemented in `formatters.py`, this pattern uses a chain of responsibility for content formatting:

```
BaseFormatter
├── CodeFormatter
│   ├── clean_content()
│   ├── is_code_block()
│   ├── detect_language()
│   └── format_code_block()
├── LinkFormatter
│   ├── format_link()
│   └── format_image()
└── (Other formatters)
```

Key characteristics:
- Each formatter handles a specific content type
- Common functionality inherited from `BaseFormatter`
- Clean separation between different formatting concerns
- Consistent interface for all formatting operations

## 3. Parser Hierarchy Pattern
Implemented in `parsers.py`, this pattern uses a combination of Factory and Strategy patterns:

```
ContentParser (Abstract Base)
├── HeadingParser
├── CodeBlockParser
├── ListParser
├── LinkParser
└── ParagraphParser

ParserFactory
└── get_parser() -> ContentParser
```

Features:
- Each parser specializes in one content type
- Factory pattern for parser selection
- Strategy pattern for parsing implementation
- Consistent parsing interface via `ParseResult` dataclass

## 4. Content Flow Pipeline
The overall system works as a pipeline:

```
URL/HTML → ContentExtractor → Parsers → Formatters → Enhanced Markdown
```

1. Content Extraction:
   - Fetches HTML content
   - Identifies main content area
   - Filters unwanted elements using constants

2. Parsing:
   - Factory selects appropriate parser
   - Parser extracts structured content
   - Maintains hierarchy and relationships

3. Formatting:
   - Applies appropriate formatter chain
   - Handles special cases (code, links)
   - Maintains consistent spacing

4. Enhancement:
   - Optional AI-based formatting
   - Preserves content while improving presentation
   - Handles edge cases and cleanup

## 5. Error Handling Pattern
Throughout the system:
- Decorator-based error handling with `@error_handler`
- Custom `HunterError` exception class
- Graceful degradation when components fail
- Comprehensive logging with rich formatting
- Fallback strategies for AI enhancement
- Type hints and validation

## 6. Progress Tracking Pattern
The system implements a context-manager based progress tracking:
```
ProgressManager
└── Rich-based progress indicators
    ├── Spinner animations
    ├── Text descriptions
    └── Task management
```

Features:
- Context manager for automatic cleanup
- Rich console formatting
- Task-based progress tracking
- Non-blocking operation

## 7. AI Enhancement Pattern
Implemented in `utils.py` with configuration in `constants.py`:
```
AIEnhancer
├── Together API integration
│   ├── API key management
│   ├── Model configuration
│   └── Error handling
├── Token calculation
│   ├── Usage tracking
│   └── Cost estimation
└── Content enhancement
    ├── Markdown optimization
    └── Formatting preservation
```

Features:
- Centralized configuration through constants
- Multiple API key configuration methods:
  1. Interactive CLI setup
  2. Environment variables
  3. Config file (~/.config/hunter/config.ini)
- Secure key storage with proper file permissions
- Graceful fallback without API key
- Clear user feedback on API status
- Token usage optimization

## 8. Testing Strategy
The codebase implements:
- Unit tests for each component
- Integration tests for the pipeline
- Test fixtures for common scenarios
- Mocking for external dependencies
- Async test support
- Progress indicator testing

## Success Metrics
The refactored architecture achieves:
1. Separation of concerns
2. Reduced code duplication
3. Improved maintainability
4. Better error handling
5. Easier testing
6. Clear component boundaries
7. Progress visibility
8. AI-ready infrastructure

This architecture allows for independent development and testing of components while maintaining the original functionality of the monolithic script.

## 9. CLI Pattern
Implemented in `main.py` and `__main__.py`, this pattern provides a clean command-line interface:

```
Hunter CLI
├── __main__.py
│   └── Module execution entry point
├── parse_args()
│   ├── URL subcommand
│   │   ├── URL processing
│   │   ├── Enhancement flags
│   │   └── Clipboard flags
│   └── Config subcommand
│       ├── API key management
│       └── Configuration display
└── main()
    ├── Argument validation
    ├── Error handling
    └── Output formatting
```

Features:
- Dual execution modes:
  1. Direct command: `hunter <command> [options]`
  2. Module form: `python -m hunter <command> [options]`
- Subcommand-based interface:
  - `url`: Process web content
  - `config`: Manage settings
- Rich console output formatting
- Clipboard integration
- Proper exit codes
- User-friendly error messages

## 10. Main Application Pattern
The application uses a modular main script pattern that coordinates all components:

```
hunter/
├── __main__.py           # Module execution support
├── main.py               # Main application logic
│   ├── Configuration management
│   │   ├── Config file handling
│   │   ├── Environment variables
│   │   └── Interactive setup
│   ├── Command processing
│   │   ├── URL subcommand
│   │   └── Config subcommand
│   └── Content pipeline
│       ├── Content extraction
│       ├── Formatting
│       └── Enhancement
└── utils.py, constants.py, etc.
```

Features:
- Clean separation of commands via subcommands
- Support for both direct and module execution
- Modular component coordination
- Consistent error handling
- Clear configuration management
- Rich user feedback

## 11. Documentation Pattern
The project follows a comprehensive documentation strategy:

```
Documentation
├── README.md
│   ├── Features overview
│   ├── Installation guide
│   ├── Usage examples
│   └── Development guide
├── Module Documentation
│   ├── Module docstrings
│   ├── Class documentation
│   ├── Method signatures
│   └── Usage examples
└── Architecture Documentation
    ├── Component patterns
    ├── Data flows
    └── Integration points
```

Features:
- Consistent docstring format across modules
- Type hints for all public interfaces
- Rich examples in documentation
- Clear separation of user and developer docs
- Performance benchmarks
- Configuration guides

## 12. Configuration Pattern
The system implements a hierarchical configuration system:

```
Configuration
├── Environment Variables (highest)
│   ├── TOGETHER_API_KEY
│   └── HUNTER_* prefixed settings
├── Config Files (in priority order)
│   ├── User config (~/.config/hunter/config.ini)
│   ├── Local config (./config/config.ini)
│   └── Default config (./config/config.ini.template)
└── Constants (constants.py)
    ├── Configuration loading logic
    └── Default values
```

Features:
- Clear configuration priority:
  1. Environment variables (highest)
  2. User config file (~/.config/hunter/config.ini)
  3. Local config file (./config/config.ini)
  4. Default config file (./config/config.ini.template)
  5. Default values (lowest)
- Secure configuration storage
  - 0o600 permissions for config files
  - 0o700 permissions for config directories
- Template-based configuration
  - Default template in version control
  - Clear documentation of options
  - Easy setup process
- Flexible override system
  - Environment variables for CI/CD
  - User config for personal settings
  - Local config for project-specific needs
- Type-safe configuration access
  - Strong typing in constants.py
  - Validation on load
  - Comprehensive logging

This architecture provides a complete picture of how the system's components work together, from core functionality to documentation and configuration management.
