# Smart Agent Shell

**Streaming shell for agents with context management and checkpoint/restore.**

![Status](https://img.shields.io/badge/Status-Functional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

Agents need more than a plain REPL. SmartShell provides streaming output, a context stack with key-value retrieval, and session checkpointing for resumability across restarts.

---

## Key Features

- **Callback-Based Streaming** — Register a `stream_callback`; output arrives as chunks rather than blocking until complete
- **Context Stack** — Push key-value frames onto a stack; retrieve the most recent value for any key
- **Checkpoint & Restore** — Export full shell state as a dict; restore a session after restart with no lost context
- **Turn Counting** — Every `execute()` call increments a turn counter, useful for audit trails and rate limiting
- **Session History** — Built-in `deque`-backed history with configurable max size

---

## How It Differs from `python-agent-shell`

| Feature | `python-agent-shell` | `smart-agent-shell` |
|---------|---------------------|---------------------|
| Streaming | Blocking stdout only | Callback-based, non-blocking |
| Context | None | Key-value context stack |
| Checkpoint | No | Full state export/restore |
| Turn tracking | No | Atomic turn counter |
| Session ID | No | UUID-based session ID |

---

## Usage

### Basic Streaming Execution

```python
from smartshell import SmartShell

shell = SmartShell()

# Register stream callback
def stream_handler(chunk):
    print(f"  >> {chunk}", end="", flush=True)

shell.set_stream_callback(stream_handler)

# Execute — callback fires per chunk
response = shell.execute("git status", stream=True)
print(response.content)
```

### Context Stack

```python
# Push context frames
shell.push_context("task", "harvest-mode")
shell.push_context("vessel", "Cocapn-7")
shell.push_context("region", "north-pacific")

# Retrieve most recent
print(shell.get_context("task"))      # "harvest-mode"
print(shell.get_context("vessel"))    # "Cocapn-7"

# Context frames track which turn they were pushed on
frame = shell.context_stack[-1]
print(frame["turn"])  # 1
```

### Checkpoint and Restore

```python
import json

# Before shutdown: checkpoint
checkpoint = shell.checkpoint()
print(json.dumps(checkpoint, indent=2))
# {
#   "session_id": "a1b2c3d4",
#   "turn_count": 7,
#   "context_stack": [{"key": "task", "value": "harvest-mode", "turn": 1}, ...],
#   "history_size": 7
# }

# After restart: restore
new_shell = SmartShell()
new_shell.restore(checkpoint)
print(new_shell.get_context("task"))  # "harvest-mode"
```

### Full Demo

```bash
python src/smartshell.py
```

Output:
```
Executing command:
  >> [a1b2c3d4]   >> executing:   >> git status...

Response: [Session a1b2c3d4] Command executed: git status
  Context: vessel=Cocapn-7

Context snapshot: {'turn': 1, 'context_depth': 2}

Checkpoint: {'session_id': 'a1b2c3d4', 'turn_count': 1, 'context_stack': [...], 'history_size': 1}
```

---

## Architecture

```
src/
└── smartshell.py
    ├── ShellResponse (dataclass)
    │       content, stream, timestamp, context_snapshot
    │
    └── SmartShell
            ├── session_id: str              # UUID (first 8 chars)
            ├── history: deque[str]          # command history
            ├── context_stack: list[dict]    # key/value frames
            ├── stream_callback: Callable     # optional chunk handler
            ├── _turn_count: int
            │
            ├── set_stream_callback(fn)      # register chunk handler
            ├── push_context(key, value)     # frame onto stack
            ├── get_context(key) -> str     # most recent value
            ├── execute(cmd, stream) -> ShellResponse
            ├── checkpoint() -> dict         # full state export
            └── restore(checkpoint)          # restore from dict
```

### Context Frame Shape

```python
{
    "key": "task",
    "value": "harvest-mode",
    "turn": 3    # which execute() call pushed this frame
}
```

---

## Related Repos

- [python-agent-shell](https://github.com/SuperInstance/python-agent-shell) — Basic shell base class
- [fleet-agent](https://github.com/SuperInstance/fleet-agent) — Fleet orchestration
- [superinstance](https://github.com/SuperInstance/superinstance) — Agent collective framework
