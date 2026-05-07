# smart-agent-shell

Smart shell for agents with streaming responses and context management.

## Concept

Agents need more than a plain REPL. SmartShell provides:
- Streaming output (callback-based, not blocking)
- Context stack with key-value retrieval
- Session checkpoint/restore for resumability
- Turn counting for audit trails

## Usage

```bash
python src/smartshell.py
```

## Key Features

| Feature | Description |
|---------|-------------|
| set_stream_callback() | Register callback for streaming output |
| push_context(key, value) | Push context frames onto stack |
| get_context(key) | Retrieve most recent value for key |
| execute(command, stream) | Run command with optional streaming |
| checkpoint() | Export shell state as dict |
| restore(checkpoint) | Restore from checkpoint dict |

## Streaming Demo

The demo shows:
1. Stream callback receives chunks as they're generated
2. Context is included in response metadata
3. Checkpoint captures full state for resumability