<div align="center">

# AgentShield Python SDK 🛡️

[![PyPI version](https://img.shields.io/badge/PyPI-agentshield--defense-3776AB?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/agentshield-defense/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Interactive Playground](https://img.shields.io/badge/Playground-Live%20Demo-00F59B?style=for-the-badge)](https://ritualdev.in/playground)
[![Trust Center](https://img.shields.io/badge/Trust-SIG%20Lite%20%2F%20DPDP-00D4FF?style=for-the-badge)](https://ritualdev.in/trust)

> Enterprise-grade Zero-Leak Secret Defense & Sandbox for Autonomous AI Agents built with LangGraph, CrewAI, AutoGen, LlamaIndex, and Smolagents.

[Documentation](https://ritualdev.in/docs) • [Web Portal](https://ritualdev.in) • [Trust Center](https://ritualdev.in/trust) • [Issues](https://github.com/RitualDev-Lab/agentshield-python/issues)

</div>

---

## ⚡ Key Features

- **`@shield.protect` Decorator**: Zero-boilerplate function and tool protection. Automatically intercepts arguments and return values.
- **Framework Integrations**:
  - **LangChain & LangGraph**: `AgentShieldCallbackHandler`
  - **CrewAI**: `AgentShieldCrewHook`
  - **LlamaIndex**: `AgentShieldLlamaHandler`
  - **Microsoft AutoGen**: `AgentShieldAutoGenGuard`
- **Zero-Leak Redaction**: 40+ credential types (OpenAI, Anthropic, AWS, GitHub, Stripe, Slack, private keys, `/proc/self/environ`).
- **Environment Sanitization**: `sanitize_env()` replaces sensitive variables with virtual mock tokens.
- **HMAC-SHA256 Audit Ledger**: Cryptographically seals every inspection with microsecond overhead.

---

## 📦 Installation

```bash
pip install agentshield-defense
```

*Note: In code, import as standard `import agentshield` or `from agentshield import shield`.*

---

## 🚀 Usage Guide

### 1. The `@shield.protect` Decorator

Decorate any agent tool, custom function, or LLM wrapper:

```python
from agentshield import shield

@shield.protect
def deploy_infrastructure(target: str, config: str) -> str:
    # Any incoming AWS keys or OpenAI keys in config are automatically masked
    return f"Deployed {target} with token: AKIAIOSFODNN7EXAMPLE"

# When executed:
output = deploy_infrastructure("prod-cluster", "key=sk-1234567890abcdef1234567890abcdef")
print(output)
# -> "Deployed prod-cluster with token: [AGENTSHIELD_REDACTED:AWS_ACCESS_KEY:a1b2c3d4e5f6]"
```

For strict enforcement (raising `PermissionError` on leak):

```python
from agentshield import protect

@protect(strict=True)
def sensitive_operation():
    ...
```

---

### 2. LangGraph & LangChain Integration

```python
from langchain_openai import ChatOpenAI
from agentshield import AgentShieldCallbackHandler

shield_handler = AgentShieldCallbackHandler()

llm = ChatOpenAI(
    model="gpt-4o",
    callbacks=[shield_handler]
)
# Outgoing prompts and tool invocations are inspected and sanitized in real time
```

---

### 3. CrewAI Guardrail Hook

```python
from crewai import Task
from agentshield import AgentShieldCrewHook

hook = AgentShieldCrewHook()

task = Task(
    description="Analyze server environment and deploy database",
    expected_output="Deployment summary"
)

hook.before_task_execution(task)
```

---

### 4. LlamaIndex Callback Handler

```python
from llama_index.core import Settings
from agentshield import AgentShieldLlamaHandler

Settings.callback_manager.add_handler(AgentShieldLlamaHandler())
```

---

### 5. Microsoft AutoGen Message Guard

```python
from agentshield import AgentShieldAutoGenGuard

guard = AgentShieldAutoGenGuard()
clean_message = guard.filter_message(incoming_message)
```

---

## 🔒 Security & Compliance

- **Zero Cloud Exfiltration**: Runs 100% locally with `AGENTSHIELD_AIR_GAPPED=1`.
- **Pre-filled SIG Lite / CAIQ**: Download the Vendor Risk Assessment Packet at [ritualdev.in/trust](https://ritualdev.in/trust).
- **Statutory Alignment**: Designed for **India DPDP Act 2023**, **EU GDPR**, and **SOC 2 Type II**.

---

## 📄 License

MIT © [RitualDev Studio](https://ritualdev.in)
