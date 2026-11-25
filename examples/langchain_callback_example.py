"""
AgentShield + LangChain / LangGraph Quickstart Example
Run: python examples/langchain_callback_example.py
"""

from agentshield.integrations.langchain import AgentShieldCallbackHandler


def main() -> None:
    handler = AgentShieldCallbackHandler()
    prompts = [
        "Connect to staging using AWS key AKIAIOSFODNN7EXAMPLE and inspect logs.",
    ]
    handler.on_llm_start({"name": "ChatModel"}, prompts)
    print("Sanitized prompt:", prompts[0])
    print("Total redactions:", handler.total_redactions)


if __name__ == "__main__":
    main()
