import os
import subprocess
from typing import Dict, List, Optional
from agentshield.redactor import AgentShieldRedactor, RedactionResult

SENSITIVE_ENV_KEYS = {
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "SLACK_BOT_TOKEN",
    "DATABASE_URL",
    "MONGO_URI",
    "STRIPE_SECRET_KEY",
    "PRIVATE_KEY",
    "SECRET_KEY",
}

def sanitize_env(
    base_env: Optional[Dict[str, str]] = None,
    keep_keys: Optional[List[str]] = None,
    mock_secrets: bool = True
) -> Dict[str, str]:
    """
    Returns an environment dictionary stripped of raw API credentials.
    If mock_secrets is True, sensitive variables are replaced with virtual mock tokens
    so agent code does not crash on missing environment definitions.
    """
    source = base_env if base_env is not None else dict(os.environ)
    clean_env: Dict[str, str] = {}
    allowed_overrides = set(keep_keys or [])

    for k, v in source.items():
        upper_k = k.upper()
        is_sensitive = (
            upper_k in SENSITIVE_ENV_KEYS or
            any(sub in upper_k for sub in ("SECRET", "TOKEN", "PASSWORD", "PRIVATE_KEY"))
        )

        if is_sensitive and k not in allowed_overrides:
            if mock_secrets:
                clean_env[k] = f"agentshield_mock_{upper_k.lower()[:8]}"
            # If not mock_secrets, simply omit
        else:
            clean_env[k] = v

    # Enforce air-gapped isolation flag
    clean_env["AGENTSHIELD_AIR_GAPPED"] = "1"
    clean_env["AGENTSHIELD_SANDBOX"] = "1"
    return clean_env

class AgentShieldSandbox:
    """
    Process sandbox wrapper that executes agent commands under an isolated,
    sanitized environment with real-time output redaction.
    """

    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or AgentShieldRedactor()

    def run_command(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        timeout: int = 30,
        env: Optional[Dict[str, str]] = None
    ) -> RedactionResult:
        """
        Executes a command safely inside the sanitized sandbox.
        Stdout and stderr are captured and passed through the zero-leak redactor.
        """
        sanitized = sanitize_env(env)
        try:
            proc = subprocess.run(
                command,
                cwd=cwd,
                env=sanitized,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            raw_output = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        except subprocess.TimeoutExpired:
            raw_output = f"[AGENTSHIELD_SANDBOX_TIMEOUT]: Execution exceeded {timeout}s limit."
        except Exception as e:
            raw_output = f"[AGENTSHIELD_SANDBOX_ERROR]: {str(e)}"

        return self.redactor.redact(raw_output)
