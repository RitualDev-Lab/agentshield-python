from typing import Any, Dict, List, Optional
from agentshield.redactor import AgentShieldRedactor

class AgentShieldCallbackHandler:
    """
    LangChain & LangGraph callback handler that inspects and redacts secrets
    from LLM inputs, tool execution arguments, and agent thoughts in real-time.
    """

    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or AgentShieldRedactor()
        self.total_redactions = 0

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Inspects prompts before they leave the application boundary."""
        for i, prompt in enumerate(prompts):
            result = self.redactor.redact(prompt)
            if result.redacted_count > 0:
                self.total_redactions += result.redacted_count
                prompts[i] = result.clean_text

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Inspects tool inputs before shell or API execution."""
        result = self.redactor.redact(input_str)
        if result.redacted_count > 0:
            self.total_redactions += result.redacted_count
            return result.clean_text
        return input_str
