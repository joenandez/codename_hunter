# Release v0.1.1

## Release Date
2024-01-02

## Overview
This is a patch release that fixes a critical package structure issue that prevented the package from being installed correctly via PyPI.

## What's Changed
### Fixed
- Fixed package structure to properly include the `hunter.utils` subpackage when installing from PyPI
- Updated package configuration in pyproject.toml to ensure all submodules are included in the distribution

## Dependencies
No changes to dependencies in this release.

## Known Issues
No known issues.

## Contributors
- @joenandez 