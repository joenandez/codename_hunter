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
Implemented in `AIEnhancer`:
```
AIEnhancer
├── API key management
├── Token calculation
└── Content enhancement
```

Features:
- Environment-based configuration
- Graceful fallback without API key
- Token usage tracking
- Error resilient enhancement

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
