# Release v0.1.2

**Release Date:** 2024-01-02

## Overview

This release includes a bug fix to improve the main content detection algorithm in the HTML parser, making it more reliable across different website structures.

## What's New

### Bug Fixes
- Enhanced main content detection algorithm in HTML parser:
  - Implemented multi-strategy approach for finding main content area
  - Added support for HTML5 semantic `<main>` tag
  - Improved detection using IDs containing 'main', 'content', or 'article'
  - Added fallback strategies using class names and `<article>` tags
  - Final fallback to `<body>` tag when needed
  - Added comprehensive test coverage for all detection strategies

## Dependencies
No changes to dependencies in this release.

## Known Issues
No known issues.

## Contributors
- Joe (@joenandez) - Bug fix implementation and testing 