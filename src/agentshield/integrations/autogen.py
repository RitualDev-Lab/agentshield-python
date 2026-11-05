from typing import Any, Dict, List, Optional, Union
from agentshield.redactor import AgentShieldRedactor

class AgentShieldAutoGenGuard:
    """
    Microsoft AutoGen filter preventing multi-agent conversations
    from broadcasting credentials between agents or leaking /proc/self/environ.
    """

    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or AgentShieldRedactor()

    def filter_message(
        self,
        message: Union[Dict[str, Any], str],
        sender: Any = None,
        recipient: Any = None
    ) -> Union[Dict[str, Any], str]:
        """Sanitizes outgoing agent message content."""
        if isinstance(message, str):
            res = self.redactor.redact(message)
            return res.clean_text
        elif isinstance(message, dict) and "content" in message:
            content = message["content"]
            if isinstance(content, str):
                res = self.redactor.redact(content)
                message["content"] = res.clean_text
        return message
