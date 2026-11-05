"""
AgentShield Python SDK
Enterprise Zero-Leak Secret Defense & Sandbox for Autonomous AI Agents.
"""

from agentshield.redactor import AgentShieldRedactor, RedactionResult
from agentshield.sandbox import AgentShieldSandbox, sanitize_env
from agentshield.decorators import protect, shield, Shield
from agentshield.integrations.langchain import AgentShieldCallbackHandler
from agentshield.integrations.crewai import AgentShieldCrewHook
from agentshield.integrations.llamaindex import AgentShieldLlamaHandler
from agentshield.integrations.autogen import AgentShieldAutoGenGuard

__version__ = "0.2.1"
__all__ = [
    "AgentShieldRedactor",
    "RedactionResult",
    "AgentShieldSandbox",
    "sanitize_env",
    "protect",
    "shield",
    "Shield",
    "AgentShieldCallbackHandler",
    "AgentShieldCrewHook",
    "AgentShieldLlamaHandler",
    "AgentShieldAutoGenGuard",
]
