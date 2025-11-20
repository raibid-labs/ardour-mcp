# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0](https://github.com/raibid-labs/ardour-mcp/compare/v0.3.0...v0.4.0) (2025-11-20)


### Features

* add Claude organization configuration ([54bc9c3](https://github.com/raibid-labs/ardour-mcp/commit/54bc9c392c108435f5e78457b84e3e07c3ed89d9))
* **music-gen:** Add complete MIDI generation and AI music pipeline ([e9809eb](https://github.com/raibid-labs/ardour-mcp/commit/e9809eb053cb791b8cf7b87c3db7a905dfce64f0))


### Documentation

* add Claude Code setup instructions ([29d60e5](https://github.com/raibid-labs/ardour-mcp/commit/29d60e58a35ac74f1cdbc6d010b21603775f41c8))
* add comprehensive getting started guides and examples ([cd2630b](https://github.com/raibid-labs/ardour-mcp/commit/cd2630ba4c17c349f03782996ead5f957f196dbc))
* add comprehensive MCP registry publishing guide ([36d1827](https://github.com/raibid-labs/ardour-mcp/commit/36d1827ded119fdc03a1d0dfe4b67bbc2289c065))
* reorganize markdown files and rewrite README with comprehensive TOC ([6517864](https://github.com/raibid-labs/ardour-mcp/commit/6517864cf3759a551013e8b2e717caf933bca1cd))

## [Unreleased]

---

## [0.3.0] - 2025-11-06

### Phase 3: Professional Mixing & Mastering

This release implements comprehensive professional mixing and mastering tools, bringing the total to **111 registered MCP tools** with **86% test coverage** across **581 tests**.

### Added

#### Advanced Mixer Operations (15 methods)
- **Send/Return Control**: Set send levels, enable/disable sends, list sends
- **Plugin Management**: Set plugin parameters, activate/deactivate plugins, list plugins
- **Bus Operations**: Create buses, route to buses, list bus sends
- **Mixer Queries**: Get send count, query mixer state, extended mixer information

#### Automation Control (13 methods)
- **Automation Modes**: Set/get modes (off/play/write/touch/latch) per parameter
- **Automation Recording**: Enable/disable automation write, record per parameter
- **Automation Editing**: Clear automation, copy between tracks, check automation status
- **Automation Playback**: Enable/disable playback, query automation state

#### Metering & Monitoring (12 methods)
- **Level Metering**: Track/master/bus level monitoring with peak detection
- **Phase Analysis**: Phase correlation measurement, phase issue detection
- **Loudness Metering**: LUFS estimation, integrated loudness, loudness range (LRA)
- **Clipping Detection**: Real-time clipping alerts with headroom analysis
- **Data Export**: Export metering data for analysis

### Documentation
- Complete usage guides for all Phase 3 features
- `ADVANCED_MIXER_USAGE.md` with 5 workflow examples
- `AUTOMATION_USAGE.md` with automation scenarios
- `METERING_USAGE.md` with metering best practices
- `COVERAGE_REPORT.md` documenting 86% test coverage

### Testing
- **581 total tests** (up from 293 in v0.2.0)
- **86% overall coverage** (up from 67%)
- 42 automation tests (98% coverage)
- 40 metering tests (96% coverage)
- 58 advanced mixer tests (100% coverage)
- New integration tests and state management tests

### Technical Improvements
- Bidirectional OSC feedback for real-time metering
- Async-safe caching with lock protection
- Comprehensive error handling and validation
- Production-ready state management

---

## [0.2.0] - 2025-11-06

### Phase 2: Essential Features

This release adds essential DAW functionality with **86 total tools** and comprehensive test coverage.

### Added

#### Mixer Tools (14 methods)
- Volume, pan, mute, solo, record-enable controls
- Track gain adjustment and reset
- Batch operations for multiple tracks
- Query mixer state

#### Recording Control (13 methods)
- Global recording start/stop
- Punch recording with in/out points
- Input monitoring modes (auto/input/disk)
- Track arming and monitoring state queries
- Recording session management

#### Navigation Tools (17 methods)
- Marker creation, deletion, navigation
- Loop region control
- Tempo and time signature changes
- Timecode format conversion
- Timeline scrubbing and positioning

#### Advanced Mixer Operations (15 methods - preview)
- Send/return level control
- Plugin management
- Bus operations
- Extended mixer state queries

### Documentation
- Recording workflow examples
- Mixer operations guide
- Navigation and timeline control reference

### Testing
- **293 total tests** with 67% coverage
- 61 recording tests (100% coverage)
- Comprehensive integration tests

---

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

[Unreleased]: https://github.com/raibid-labs/ardour-mcp/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/raibid-labs/ardour-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/raibid-labs/ardour-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/raibid-labs/ardour-mcp/releases/tag/v0.1.0
