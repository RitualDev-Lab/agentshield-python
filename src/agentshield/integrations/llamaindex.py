from typing import Any, Dict, List, Optional
from agentshield.redactor import AgentShieldRedactor

class AgentShieldLlamaHandler:
    """
    LlamaIndex callback handler to sanitize embeddings, retrieval nodes,
    and LLM responses against secret leaks and environment exfiltration.
    """

    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or AgentShieldRedactor()

    def on_event_start(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any
    ) -> str:
        """Sanitizes outgoing query texts and prompt templates."""
        if payload and "query_str" in payload and isinstance(payload["query_str"], str):
            res = self.redactor.redact(payload["query_str"])
            payload["query_str"] = res.clean_text
        return event_id

    def on_event_end(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any
    ) -> None:
        """Sanitizes synthesized responses from nodes and LLMs."""
        if payload and "response" in payload:
            resp = payload["response"]
            if isinstance(resp, str):
                res = self.redactor.redact(resp)
                payload["response"] = res.clean_text
            elif hasattr(resp, "response") and isinstance(resp.response, str):
                res = self.redactor.redact(resp.response)
                resp.response = res.clean_text
