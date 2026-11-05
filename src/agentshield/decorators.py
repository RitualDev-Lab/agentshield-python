from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
from agentshield.redactor import AgentShieldRedactor, RedactionResult

_default_redactor = AgentShieldRedactor()

def _sanitize_value(val: Any, redactor: AgentShieldRedactor) -> Any:
    """Recursively redacts secrets in strings, dicts, and lists."""
    if isinstance(val, str):
        return redactor.redact(val).clean_text
    elif isinstance(val, dict):
        return {k: _sanitize_value(v, redactor) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        sanitized = [_sanitize_value(item, redactor) for item in val]
        return type(val)(sanitized)
    return val

def protect(
    func: Optional[Callable[..., Any]] = None,
    *,
    strict: bool = False,
    redact_args: bool = True,
    redact_return: bool = True,
    redactor: Optional[AgentShieldRedactor] = None,
    audit_callback: Optional[Callable[[RedactionResult], None]] = None
) -> Callable[..., Any]:
    """
    Decorator for AI agent tools, prompt builders, and LLM completions.
    Automatically intercepts arguments and return values to guarantee zero credential leakage.

    Usage:
        @protect
        def run_tool(command: str) -> str:
            return execute(command)

        @protect(strict=True)
        async def call_llm(prompt: str) -> str:
            return await llm.ainvoke(prompt)
    """
    active_redactor = redactor or _default_redactor

    def decorator(target: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(target):
            @functools.wraps(target)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                sanitized_args = args
                sanitized_kwargs = kwargs

                if redact_args:
                    sanitized_args = tuple(_sanitize_value(a, active_redactor) for a in args)
                    sanitized_kwargs = {k: _sanitize_value(v, active_redactor) for k, v in kwargs.items()}

                result = await target(*sanitized_args, **sanitized_kwargs)

                if redact_return:
                    if isinstance(result, str):
                        redaction = active_redactor.redact(result)
                        if strict and redaction.redacted_count > 0:
                            raise PermissionError(
                                f"[AgentShield Violation] Output contained {redaction.redacted_count} unredacted secret(s): {redaction.matched_rules}"
                            )
                        if audit_callback:
                            audit_callback(redaction)
                        return redaction.clean_text
                    elif isinstance(result, (dict, list)):
                        return _sanitize_value(result, active_redactor)

                return result
            return async_wrapper
        else:
            @functools.wraps(target)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                sanitized_args = args
                sanitized_kwargs = kwargs

                if redact_args:
                    sanitized_args = tuple(_sanitize_value(a, active_redactor) for a in args)
                    sanitized_kwargs = {k: _sanitize_value(v, active_redactor) for k, v in kwargs.items()}

                result = target(*sanitized_args, **sanitized_kwargs)

                if redact_return:
                    if isinstance(result, str):
                        redaction = active_redactor.redact(result)
                        if strict and redaction.redacted_count > 0:
                            raise PermissionError(
                                f"[AgentShield Violation] Output contained {redaction.redacted_count} unredacted secret(s): {redaction.matched_rules}"
                            )
                        if audit_callback:
                            audit_callback(redaction)
                        return redaction.clean_text
                    elif isinstance(result, (dict, list)):
                        return _sanitize_value(result, active_redactor)

                return result
            return sync_wrapper

    if func is not None:
        return decorator(func)
    return decorator

class Shield:
    """Namespace convenience wrapper providing shield.protect."""
    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or _default_redactor

    def protect(self, *args: Any, **kwargs: Any) -> Any:
        if "redactor" not in kwargs:
            kwargs["redactor"] = self.redactor
        return protect(*args, **kwargs)

shield = Shield()
