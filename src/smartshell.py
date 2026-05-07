"""Smart shell for agents with streaming responses and context management."""
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import deque

@dataclass
class ShellResponse:
    content: str
    stream: bool
    timestamp: float = field(default_factory=time.time)
    context_snapshot: dict = field(default_factory=dict)

class SmartShell:
    """Streaming shell with context awareness for agentic operations."""
    
    def __init__(self, max_history: int = 100, max_context: int = 10):
        self.max_history = max_history
        self.max_context = max_context
        self.session_id = str(uuid.uuid4())[:8]
        self.history: deque[str] = deque(maxlen=max_history)
        self.context_stack: list[dict] = []
        self.stream_callback: Optional[Callable] = None
        self._turn_count = 0
    
    def set_stream_callback(self, callback: Callable[[str], None]):
        self.stream_callback = callback
    
    def push_context(self, key: str, value: str):
        """Push a context frame onto the stack."""
        self.context_stack.append({
            "key": key, "value": value,
            "turn": self._turn_count
        })
        # Keep only max_context frames
        if len(self.context_stack) > self.max_context:
            self.context_stack.pop(0)
    
    def get_context(self, key: str) -> Optional[str]:
        """Retrieve most recent value for a context key."""
        for frame in reversed(self.context_stack):
            if frame["key"] == key:
                return frame["value"]
        return None
    
    def execute(self, command: str, stream: bool = True) -> ShellResponse:
        """Execute command with optional streaming output."""
        self._turn_count += 1
        self.history.append(command)
        
        if stream and self.stream_callback:
            # Simulate streaming by chunks
            chunks = [f"[{self.session_id}] ", f"executing: ", f"{command[:20]}..."]
            for chunk in chunks:
                self.stream_callback(chunk)
        
        # Build response
        content = f"[Session {self.session_id}] Command executed: {command}"
        if self.context_stack:
            recent = self.context_stack[-1]
            content += f"\n  Context: {recent['key']}={recent['value']}"
        
        return ShellResponse(
            content=content,
            stream=stream,
            context_snapshot={"turn": self._turn_count, "context_depth": len(self.context_stack)}
        )
    
    def checkpoint(self) -> dict:
        """Export current shell state for resumability."""
        return {
            "session_id": self.session_id,
            "turn_count": self._turn_count,
            "context_stack": self.context_stack.copy(),
            "history_size": len(self.history)
        }
    
    def restore(self, checkpoint: dict):
        """Restore shell from checkpoint."""
        self.session_id = checkpoint["session_id"]
        self._turn_count = checkpoint["turn_count"]
        self.context_stack = checkpoint["context_stack"].copy()

if __name__ == "__main__":
    shell = SmartShell()
    
    # Stream callback for demo
    def show_stream(chunk):
        print(f"  >> {chunk}", end="", flush=True)
    shell.set_stream_callback(show_stream)
    
    # Push context
    shell.push_context("task", "harvest-mode")
    shell.push_context("vessel", "Cocapn-7")
    
    # Execute with streaming
    print("Executing command:")
    resp = shell.execute("git status", stream=True)
    print(f"\n\nResponse: {resp.content}")
    print(f"Context snapshot: {resp.context_snapshot}")
    
    # Checkpoint
    cp = shell.checkpoint()
    print(f"\nCheckpoint: {cp}")