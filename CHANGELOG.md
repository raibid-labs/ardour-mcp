# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-06

### Added

- Complete OSC bridge with bidirectional communication for Ardour DAW
- State management system with automatic updates from Ardour
- Transport control tools (13 methods):
  - Play, stop, pause, record control
  - Timeline navigation (goto start/end, forward/rewind)
  - Transport state queries
- Session information tools (9 methods):
  - Session properties (name, path, tempo, sample rate, duration)
  - Track counting and buffer size queries
- Track management tools (5 methods):
  - Create audio/MIDI tracks
  - Track selection and naming
  - Track list queries
- MCP server integration with 27 registered tools
- Comprehensive testing suite:
  - 98 unit tests with 100% pass rate
  - 59% overall code coverage
  - 100% coverage for tracks and session modules
  - 94% coverage for transport module
  - 88% coverage for OSC bridge
- Integration testing framework with justfile automation
- Project structure and comprehensive documentation:
  - Architecture overview
  - Development guide
  - OSC API reference
  - Roadmap with feature timeline
  - Contributing guidelines

### Documentation

- Complete README with installation and usage instructions
- Architecture documentation with system design
- OSC API reference for Ardour integration
- Development guide for contributors
- Roadmap outlining Phase 1-4 feature plan

---

[Unreleased]: https://github.com/raibid-labs/ardour-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/raibid-labs/ardour-mcp/releases/tag/v0.1.0
