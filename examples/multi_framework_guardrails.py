"""
AgentShield + CrewAI / AutoGen / LlamaIndex Guardrail Example
Run: python examples/multi_framework_guardrails.py
"""

from types import SimpleNamespace

from agentshield.integrations.autogen import AgentShieldAutoGenGuard
from agentshield.integrations.crewai import AgentShieldCrewHook
from agentshield.integrations.llamaindex import AgentShieldLlamaHandler


def main() -> None:
    # 1. CrewAI task hook
    crew_hook = AgentShieldCrewHook()
    task = SimpleNamespace(description="Audit token ghp_1234567890abcdef1234567890abcdef1234")
    crew_hook.before_task_execution(task)
    print("CrewAI sanitized task:", task.description)

    # 2. AutoGen message guard
    autogen_guard = AgentShieldAutoGenGuard()
    msg = autogen_guard.filter_message({"role": "user", "content": "Read .env.local secrets"})
    print("AutoGen sanitized message:", msg)

    # 3. LlamaIndex callback handler
    llama_handler = AgentShieldLlamaHandler()
    payload = {"query_str": "Search sk-test99a8b7c6d5e4f3a2b1c012345 in notes"}
    llama_handler.on_event_start("query", payload=payload)
    print("LlamaIndex sanitized query:", payload["query_str"])


if __name__ == "__main__":
    main()
