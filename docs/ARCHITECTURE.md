# Ardour MCP Architecture

This document describes the system architecture, design decisions, and component interactions for the Ardour MCP server.

## Overview

Ardour MCP bridges AI assistants with the Ardour DAW using a three-layer architecture that separates concerns and enables reliable, maintainable communication.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Assistant                             │
│                  (Claude, GPT-4, etc.)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ MCP Protocol (JSON-RPC)
                         │ (stdio, SSE, or WebSocket)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    MCP Server Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │             Tool Registration & Dispatch               │ │
│  │  - transport_play(), transport_stop()                  │ │
│  │  - create_track(), select_track()                      │ │
│  │  - set_volume(), set_pan()                             │ │
│  │  - get_session_info()                                  │ │
│  └─────────────────────┬──────────────────────────────────┘ │
└────────────────────────┼────────────────────────────────────┘
                         │
                         │ Internal API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 State Management Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Ardour State Cache                        │ │
│  │  - Transport state (playing, recording, position)      │ │
│  │  - Session info (tempo, sample rate, tracks)           │ │
│  │  - Track states (name, mute, solo, volume, pan)        │ │
│  │  - Marker list                                          │ │
│  └─────────────────────┬──────────────────────────────────┘ │
└────────────────────────┼────────────────────────────────────┘
                         │
                         │ State Queries & Updates
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   OSC Bridge Layer                           │
│  ┌───────────────────────────┬────────────────────────────┐ │
│  │     OSC Client            │    OSC Server              │ │
│  │  (Command Sender)         │  (Feedback Receiver)       │ │
│  │                           │                             │ │
│  │  - Send commands          │  - Listen for feedback     │ │
│  │  - Handle responses       │  - Parse OSC messages      │ │
│  │  - Error handling         │  - Update state cache      │ │
│  └───────────┬───────────────┴──────────┬─────────────────┘ │
└──────────────┼──────────────────────────┼───────────────────┘
               │                          │
               │ OSC Protocol (UDP)       │
               │ Port 3819 (default)      │
               │                          │
┌──────────────▼──────────────────────────▼───────────────────┐
│                       Ardour DAW                             │
│  - OSC Server (receives commands)                            │
│  - OSC Feedback (sends state updates)                        │
└──────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. MCP Server Layer

**Responsibilities:**
- Expose MCP tools to AI assistants
- Handle tool registration and dispatch
- Validate inputs and format outputs
- Manage error responses
- Provide tool documentation

**Key Components:**
- `server.py`: Main MCP server implementation
- Tool modules in `tools/`: Individual tool implementations

**Design Decisions:**
- **Stateless tools**: Each tool invocation is independent
- **Synchronous execution**: Tools block until complete for predictable behavior
- **Rich error messages**: Provide context for failures
- **JSON Schema validation**: Ensure type safety

### 2. State Management Layer

**Responsibilities:**
- Cache Ardour's current state
- Handle OSC feedback updates
- Provide fast state queries
- Maintain consistency with Ardour

**Key Components:**
- `ardour_state.py`: State cache implementation
- Data models for session, tracks, transport

**Design Decisions:**
- **Event-driven updates**: State updated from OSC feedback
- **Thread-safe access**: Multiple tools can query state
- **Lazy initialization**: Request initial state on first access
- **Optimistic updates**: Update cache on commands, verify on feedback

**State Data Model:**

```python
@dataclass
class TransportState:
    playing: bool
    recording: bool
    frame: int
    tempo: float
    time_signature: tuple[int, int]

@dataclass
class TrackState:
    strip_id: int
    name: str
    type: str  # "audio" or "midi"
    muted: bool
    soloed: bool
    rec_enabled: bool
    gain_db: float
    pan: float  # -1.0 (left) to 1.0 (right)

@dataclass
class SessionState:
    name: str
    path: str
    sample_rate: int
    tracks: dict[int, TrackState]
    markers: list[tuple[str, int]]
    transport: TransportState
```

### 3. OSC Bridge Layer

**Responsibilities:**
- Send OSC commands to Ardour
- Receive OSC feedback from Ardour
- Handle network errors
- Manage connection lifecycle

**Key Components:**
- `osc_bridge.py`: OSC communication implementation
- OSC client (uses `python-osc`)
- OSC server (feedback receiver)

**Design Decisions:**
- **Bidirectional communication**: Separate client and server
- **Asynchronous feedback**: Non-blocking feedback reception
- **Automatic reconnection**: Handle Ardour restarts
- **Command queuing**: Optional command batching

**OSC Communication Flow:**

```
Tool Call:
  transport_play()
      ↓
  State Management:
    Check current state
      ↓
  OSC Bridge:
    Send /transport_play
      ↓
  Ardour:
    Execute command
    Send /transport_frame feedback
      ↓
  OSC Bridge:
    Receive feedback
      ↓
  State Management:
    Update transport.playing = True
    Update transport.frame
      ↓
  Tool Response:
    Return success
```

## Data Flow Patterns

### Command Execution

1. **AI Assistant** sends MCP tool call
2. **MCP Server** validates inputs
3. **State Management** checks current state (optional)
4. **OSC Bridge** sends command to Ardour
5. **Ardour** executes command, sends feedback
6. **OSC Bridge** receives feedback
7. **State Management** updates cache
8. **MCP Server** returns result to AI

### State Query

1. **AI Assistant** sends MCP tool call
2. **MCP Server** validates inputs
3. **State Management** returns cached state
4. **MCP Server** formats and returns result

No OSC communication needed for cached state!

### Feedback Processing (Continuous)

1. **Ardour** sends OSC feedback (unprompted)
2. **OSC Bridge** receives and parses message
3. **State Management** updates relevant cache
4. Cache ready for next query

## Error Handling Strategy

### Error Categories

1. **Validation Errors**: Invalid tool inputs
   - Caught at MCP server layer
   - Return clear error message
   - Don't send to Ardour

2. **Network Errors**: OSC communication failures
   - Caught at OSC bridge layer
   - Attempt reconnection
   - Return network error to MCP server

3. **Ardour Errors**: Invalid commands or state
   - Detected via feedback or timeout
   - Return Ardour-specific error
   - May need state refresh

4. **State Errors**: Inconsistent state
   - Detected at state management layer
   - Trigger state refresh
   - Retry command if appropriate

### Error Handling Flow

```python
try:
    # Validate inputs
    validate_tool_inputs(params)

    # Check state (optional)
    current_state = state_manager.get_state()

    # Send OSC command
    osc_bridge.send_command("/ardour/command", params)

    # Wait for feedback (with timeout)
    feedback = wait_for_feedback(timeout=1.0)

    # Update state
    state_manager.update(feedback)

    return success_response(feedback)

except ValidationError as e:
    return error_response(f"Invalid input: {e}")

except NetworkError as e:
    return error_response(f"Cannot connect to Ardour: {e}")

except TimeoutError:
    return error_response("Ardour did not respond")

except ArdourError as e:
    return error_response(f"Ardour error: {e}")
```

## Concurrency Model

### Threading Strategy

- **Main Thread**: MCP server, tool dispatch
- **OSC Feedback Thread**: Continuous feedback reception
- **State Lock**: Thread-safe state access

```python
class ArdourState:
    def __init__(self):
        self._lock = threading.RLock()
        self._data = SessionState()

    def update(self, feedback: OSCMessage):
        with self._lock:
            # Update state based on feedback
            self._data.transport.frame = feedback.args[0]

    def get_transport(self) -> TransportState:
        with self._lock:
            return self._data.transport
```

### Performance Considerations

- **Non-blocking feedback**: OSC server runs in background
- **Fast state queries**: No network round-trip
- **Batched updates**: Multiple feedback messages processed together
- **Command queuing**: Optional for rapid commands

## Configuration

### Environment Variables

- `ARDOUR_OSC_HOST`: Ardour host (default: `localhost`)
- `ARDOUR_OSC_PORT`: Ardour OSC port (default: `3819`)
- `OSC_FEEDBACK_PORT`: Port for receiving feedback (default: `3820`)
- `LOG_LEVEL`: Logging verbosity (default: `INFO`)

### Configuration File (Future)

```toml
[ardour]
host = "localhost"
port = 3819

[osc]
feedback_port = 3820
timeout = 1.0
retry_attempts = 3

[state]
cache_ttl = 5.0
refresh_interval = 1.0

[logging]
level = "INFO"
file = "ardour-mcp.log"
```

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock external dependencies (OSC, network)
- Test error handling paths
- Verify state consistency

### Integration Tests

- Test with mock Ardour OSC server
- Verify full command flow
- Test feedback processing
- Verify state synchronization

### End-to-End Tests

- Test with real Ardour instance (optional)
- Verify real-world scenarios
- Test performance under load
- Verify compatibility with Ardour versions

## Security Considerations

### Network Security

- **Local-only by default**: Bind to localhost
- **No authentication** (relies on local security)
- **UDP protocol**: No encryption (local network)

### Input Validation

- Validate all tool inputs
- Sanitize strings before sending to Ardour
- Limit numeric ranges
- Prevent injection attacks

### State Consistency

- Verify feedback matches commands
- Handle stale state
- Refresh state on inconsistencies

## Performance Targets

- **Tool latency**: < 100ms for cached queries
- **Command latency**: < 50ms for OSC commands
- **Feedback latency**: < 10ms for state updates
- **Memory usage**: < 50MB for typical sessions
- **State cache size**: < 1MB for typical sessions

## Future Enhancements

### Phase 2+

- **WebSocket feedback**: Lower latency than UDP
- **Command batching**: Multiple commands in single transaction
- **State snapshots**: Capture and restore full state
- **Plugin discovery**: Enumerate installed plugins
- **Automation recording**: Record parameter changes
- **Session templates**: Apply predefined configurations

### Scalability

- **Multiple Ardour instances**: Support multiple connections
- **Remote connections**: Secure remote access
- **Load balancing**: Distribute commands across instances
- **State replication**: Sync state across instances

---

This architecture provides a solid foundation for reliable, maintainable, and extensible AI control of Ardour.
