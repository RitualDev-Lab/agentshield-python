<div align="center">

# AgentShield Python SDK 🛡️

[![PyPI version](https://img.shields.io/badge/PyPI-agentshield-3776AB?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/agentshield/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Interactive Playground](https://img.shields.io/badge/Playground-Live%20Demo-00F59B?style=for-the-badge)](https://ritualdev.in/playground)
[![Trust Center](https://img.shields.io/badge/Trust-SIG%20Lite%20%2F%20DPDP-00D4FF?style=for-the-badge)](https://ritualdev.in/trust)

> Enterprise-grade Zero-Leak Secret Defense & Sandbox for Autonomous AI Agents built with LangGraph, CrewAI, AutoGen, Smolagents, and OpenAI Swarm.

[Documentation](https://ritualdev.in/docs) • [Web Portal](https://ritualdev.in) • [Trust Center](https://ritualdev.in/trust) • [Issues](https://github.com/RitualDev-Lab/agentshield-python/issues)

</div>

---

## ⚡ Why AgentShield for Python AI Agents?

Autonomous AI coding agents frequently:
1. Print or dump `/proc/self/environ` to inspect credentials.
2. Leak raw `OPENAI_API_KEY`, `AWS_SECRET_ACCESS_KEY`, or database credentials into LLM completion prompts.
3. Fall victim to prompt injection attacks attempting to exfiltrate `.env` files.

`agentshield` intercepts, redacts, and cryptographically seals sensitive data with linear-time token verification before any byte leaves your runtime or enters an LLM prompt.

---

## 📦 Installation

```bash
pip install agentshield
```

Or install with LangChain support:

```bash
pip install "agentshield[langchain]"
```

---

## 🚀 Quickstart

### 1. Zero-Leak Secret Redactor

```python
from agentshield import AgentShieldRedactor

redactor = AgentShieldRedactor()

agent_output = """
Calling AWS deployment:
AWS_ACCESS_KEY: AKIAIOSFODNN7EXAMPLE
OPENAI_KEY: sk-1234567890abcdef1234567890abcdef
Check /proc/self/environ
"""

result = redactor.redact(agent_output)

print(result.clean_text)
# Output:
# Calling AWS deployment:
# AWS_ACCESS_KEY: [AGENTSHIELD_REDACTED:AWS_ACCESS_KEY:a1b2c3d4e5f6]
# OPENAI_KEY: [AGENTSHIELD_REDACTED:OPENAI_KEY:9f8e7d6c5b4a]
# Check [AGENTSHIELD_REDACTED:PROC_ENVIRON_READ:3c4d5e6f7a8b]

print(f"Redacted {result.redacted_count} secrets in {result.latency_ms}ms")
print(f"HMAC Audit Ledger Seal: {result.audit_hash}")
```

---

### 2. LangGraph & LangChain Integration

Attach `AgentShieldCallbackHandler` to your agent pipeline:

```python
from langchain_openai import ChatOpenAI
from agentshield.integrations.langchain import AgentShieldCallbackHandler

shield = AgentShieldCallbackHandler()

llm = ChatOpenAI(
    model="gpt-4o",
    callbacks=[shield]
)

# All outgoing prompts and tool calls are automatically audited and sanitized
```

---

### 3. CrewAI Safety Hook

```python
from crewai import Agent, Task, Crew
from agentshield.integrations.crewai import AgentShieldCrewHook

hook = AgentShieldCrewHook()

task = Task(
    description="Analyze server environment and deploy database",
    expected_output="Deployment summary"
)

# Pre-execution and post-execution hooks sanitize credentials
hook.before_task_execution(task)
```

---

### 4. Sandboxed Subprocess Execution

Prevent child processes spawned by agents from reading raw host environment secrets:

```python
from agentshield import AgentShieldSandbox

sandbox = AgentShieldSandbox()

# Executes in an isolated environment with credentials virtualized to mock tokens
result = sandbox.run_command(["python", "untrusted_agent_script.py"], timeout=15)
print(result.clean_text)
```

---

## 🔒 Security & Statutory Compliance

- **Zero Cloud Telemetry**: Runs 100% locally with `AGENTSHIELD_AIR_GAPPED=1`.
- **Pre-filled SIG Lite / CAIQ**: Download the Vendor Risk Assessment Packet at [ritualdev.in/trust](https://ritualdev.in/trust).
- **Statutory Controls**: Architected for **India DPDP Act 2023**, **EU GDPR**, and **SOC 2 Type II**.

---

## 📄 License

MIT © [RitualDev Studio](https://ritualdev.in)
