import time
from typing import Any, Dict, List, Optional

from google.adk.plugins.logging_plugin import LoggingPlugin


class FxObservabilityPlugin(LoggingPlugin):
    """Observability plugin that tracks invocations, timings, payload sizes and errors for models, tools and agents."""

    def __init__(self, log_prompts: bool = False, log_responses: bool = False):
        """Initialize counters, timing stacks and optional flags for prompt/response logging."""
        
        super().__init__()
        self.model_invocations = 0
        self.tool_invocations = 0
        self.agent_invocations = 0
        self.errors: List[str] = []
        self.events: List[Dict[str, Any]] = []

        self._model_start_stack: List[float] = []
        self._tool_start_stack: List[float] = []
        self._agent_start_stack: List[float] = []

        self.total_model_time_ms: float = 0.0
        self.total_tool_time_ms: float = 0.0
        self.total_agent_time_ms: float = 0.0

        self.total_prompt_chars: int = 0
        self.total_response_chars: int = 0

    def _now(self) -> float:
        """Return the current time in seconds since the Unix epoch."""
        return time.time()

    def _ms_since(self, start_ts: float) -> float:
        """Compute elapsed time in milliseconds since the given timestamp."""
        return (self._now() - start_ts) * 1000.0

    def _extract_ids(self, kwargs: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract user_id and session_id from kwargs and normalize them to strings or None."""
        user_id = kwargs.get("user_id")
        session_id = kwargs.get("session_id")
        return {
            "user_id": str(user_id) if user_id is not None else None,
            "session_id": str(session_id) if session_id is not None else None,
        }

    async def before_model_callback(self, *args, **kwargs):
        """Record model invocation start time, prompt size and append a 'model_before' event."""
        
        self.model_invocations += 1
        model_name = kwargs.get("model_name") or kwargs.get("model")
        messages = kwargs.get("messages") or kwargs.get("contents")
        ids = self._extract_ids(kwargs)

        prompt_chars = 0
        if messages:
            for m in messages:
                parts = getattr(m, "parts", []) or []
                for p in parts:
                    text = getattr(p, "text", None)
                    if text:
                        prompt_chars += len(text)

        self.total_prompt_chars += prompt_chars
        self._model_start_stack.append(self._now())

        self.events.append(
            {
                "ts": self._now(),
                "type": "model_before",
                "model": str(model_name),
                "prompt_chars": prompt_chars,
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "before_model_callback"):
            await super().before_model_callback(*args, **kwargs)

    async def after_model_callback(self, *args, **kwargs):
        """Record model response size, elapsed time and append a 'model_after' event."""
        
        response = kwargs.get("response")
        ids = self._extract_ids(kwargs)

        response_chars = 0
        if response and getattr(response, "candidates", None):
            for cand in response.candidates:
                content = getattr(cand, "content", None)
                if content and getattr(content, "parts", None):
                    for p in content.parts:
                        text = getattr(p, "text", None)
                        if text:
                            response_chars += len(text)

        self.total_response_chars += response_chars

        duration_ms = None
        if self._model_start_stack:
            start_ts = self._model_start_stack.pop()
            duration_ms = self._ms_since(start_ts)
            self.total_model_time_ms += duration_ms

        self.events.append(
            {
                "ts": self._now(),
                "type": "model_after",
                "response_chars": response_chars,
                "duration_ms": duration_ms,
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "after_model_callback"):
            await super().after_model_callback(*args, **kwargs)

    async def on_model_error_callback(self, *args, **kwargs):
        """Capture model error information and append a 'model_error' event."""
        err = kwargs.get("error")
        ids = self._extract_ids(kwargs)
        msg = repr(err)
        self.errors.append(msg)
        self.events.append(
            {
                "ts": self._now(),
                "type": "model_error",
                "error": msg,
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )
        if hasattr(super(), "on_model_error_callback"):
            await super().on_model_error_callback(*args, **kwargs)

    async def before_tool_callback(self, *args, **kwargs):
        """Record tool invocation start time and append a 'tool_before' event."""
        self.tool_invocations += 1
        tool_name = kwargs.get("tool_name") or kwargs.get("tool")
        ids = self._extract_ids(kwargs)

        self._tool_start_stack.append(self._now())

        self.events.append(
            {
                "ts": self._now(),
                "type": "tool_before",
                "tool": str(tool_name),
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "before_tool_callback"):
            await super().before_tool_callback(*args, **kwargs)

    async def after_tool_callback(self, *args, **kwargs):
        """Record tool elapsed time and append a 'tool_after' event."""
        tool_name = kwargs.get("tool_name") or kwargs.get("tool")
        ids = self._extract_ids(kwargs)

        duration_ms = None
        if self._tool_start_stack:
            start_ts = self._tool_start_stack.pop()
            duration_ms = self._ms_since(start_ts)
            self.total_tool_time_ms += duration_ms

        self.events.append(
            {
                "ts": self._now(),
                "type": "tool_after",
                "tool": str(tool_name),
                "duration_ms": duration_ms,
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "after_tool_callback"):
            await super().after_tool_callback(*args, **kwargs)

    async def before_agent_callback(self, *args, **kwargs):
        """Record agent invocation start time and append an 'agent_before' event."""
        self.agent_invocations += 1
        agent_name = kwargs.get("agent_name") or kwargs.get("agent")
        ids = self._extract_ids(kwargs)

        self._agent_start_stack.append(self._now())

        self.events.append(
            {
                "ts": self._now(),
                "type": "agent_before",
                "agent": str(agent_name),
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "before_agent_callback"):
            await super().before_agent_callback(*args, **kwargs)

    async def after_agent_callback(self, *args, **kwargs):
        """Record agent elapsed time and append an 'agent_after' event."""
        agent_name = kwargs.get("agent_name") or kwargs.get("agent")
        ids = self._extract_ids(kwargs)

        duration_ms = None
        if self._agent_start_stack:
            start_ts = self._agent_start_stack.pop()
            duration_ms = self._ms_since(start_ts)
            self.total_agent_time_ms += duration_ms

        self.events.append(
            {
                "ts": self._now(),
                "type": "agent_after",
                "agent": str(agent_name),
                "duration_ms": duration_ms,
                "user_id": ids["user_id"],
                "session_id": ids["session_id"],
            }
        )

        if hasattr(super(), "after_agent_callback"):
            await super().after_agent_callback(*args, **kwargs)

    def get_summary(self) -> Dict[str, Any]:
        """Return a compact summary with counts of invocations, errors and events."""
        return {
            "model_invocations": self.model_invocations,
            "tool_invocations": self.tool_invocations,
            "agent_invocations": self.agent_invocations,
            "error_count": len(self.errors),
            "event_count": len(self.events),
        }

    def get_detailed_summary(self) -> Dict[str, Any]:
        """Return a detailed summary including timings, sizes and last error information."""
        
        model_avg = (
            self.total_model_time_ms / self.model_invocations
            if self.model_invocations > 0
            else 0.0
        )
        tool_avg = (
            self.total_tool_time_ms / self.tool_invocations
            if self.tool_invocations > 0
            else 0.0
        )
        agent_avg = (
            self.total_agent_time_ms / self.agent_invocations
            if self.agent_invocations > 0
            else 0.0
        )
        return {
            "model_invocations": self.model_invocations,
            "tool_invocations": self.tool_invocations,
            "agent_invocations": self.agent_invocations,
            "total_model_time_ms": self.total_model_time_ms,
            "total_tool_time_ms": self.total_tool_time_ms,
            "total_agent_time_ms": self.total_agent_time_ms,
            "avg_model_time_ms": model_avg,
            "avg_tool_time_ms": tool_avg,
            "avg_agent_time_ms": agent_avg,
            "total_prompt_chars": self.total_prompt_chars,
            "total_response_chars": self.total_response_chars,
            "error_count": len(self.errors),
            "last_error": self.errors[-1] if self.errors else None,
            "event_count": len(self.events),
        }

    def get_last_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return the last n recorded observability events."""
        return self.events[-n:]


print("✔️ Fx Observability Plugin has been installed!")
