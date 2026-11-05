import hashlib
import hmac
import os
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class RedactionResult:
    clean_text: str
    redacted_count: int
    matched_rules: List[str]
    latency_ms: float
    audit_hash: str
    violations: List[Dict[str, str]] = field(default_factory=list)

class AgentShieldRedactor:
    """
    High-performance zero-leak secret redaction engine for AI agent inputs,
    tool execution arguments, and LLM completions.
    """

    # Bounded, ReDoS-safe compiled patterns
    DEFAULT_PATTERNS = [
        ("AWS_ACCESS_KEY", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
        ("OPENAI_KEY", re.compile(r"\b(sk-[a-zA-Z0-9]{20,64})\b")),
        ("ANTHROPIC_KEY", re.compile(r"\b(sk-ant-[a-zA-Z0-9_\-]{20,80})\b")),
        ("GITHUB_PAT", re.compile(r"\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})\b")),
        ("SLACK_TOKEN", re.compile(r"\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b")),
        ("STRIPE_KEY", re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,34})\b")),
        ("JWT_TOKEN", re.compile(r"\b(ey[A-Za-z0-9_-]{10,}\.ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")),
        ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]{20,2500}?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("PROC_ENVIRON_READ", re.compile(r"(?:/proc/(?:self|\d+)/environ|\.e[\"']?n[\"']?v|\.env\.local)", re.IGNORECASE)),
        ("GENERIC_SECRET_ASSIGN", re.compile(r"(?i)\b(api[_-]?key|secret|password|access[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{16,64})['\"]?")),
    ]

    def __init__(
        self,
        custom_patterns: Optional[List[Tuple[str, re.Pattern]]] = None,
        audit_secret: Optional[str] = None,
        mask_template: str = "[AGENTSHIELD_REDACTED:{rule}:{digest}]"
    ):
        self.patterns = list(self.DEFAULT_PATTERNS)
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self.audit_secret = (audit_secret or os.getenv("AGENTSHIELD_AUDIT_SECRET", "agentshield-vault-key")).encode("utf-8")
        self.mask_template = mask_template

    def redact(self, text: str) -> RedactionResult:
        """
        Redacts credentials, tokens, and prohibited environment queries from text.
        Returns RedactionResult containing clean text and audit metadata.
        """
        if not text:
            return RedactionResult(
                clean_text="",
                redacted_count=0,
                matched_rules=[],
                latency_ms=0.0,
                audit_hash=self._compute_hash("")
            )

        start_time = time.perf_counter()
        clean = text
        redacted_count = 0
        matched_rules: List[str] = []
        violations: List[Dict[str, str]] = []

        for rule_name, pattern in self.patterns:
            matches = list(pattern.finditer(clean))
            if not matches:
                continue

            # Process matches in reverse to preserve index offsets
            for match in reversed(matches):
                secret_str = match.group(0)
                # Compute irreversible HMAC token digest
                token_digest = hmac.new(self.audit_secret, secret_str.encode("utf-8"), hashlib.sha256).hexdigest()[:12]
                replacement = self.mask_template.format(rule=rule_name, digest=token_digest)

                start, end = match.span()
                clean = clean[:start] + replacement + clean[end:]
                redacted_count += 1
                matched_rules.append(rule_name)
                violations.append({
                    "rule": rule_name,
                    "digest": token_digest,
                    "offset": str(start)
                })

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        audit_hash = self._compute_hash(clean)

        return RedactionResult(
            clean_text=clean,
            redacted_count=redacted_count,
            matched_rules=list(set(matched_rules)),
            latency_ms=round(elapsed_ms, 3),
            audit_hash=audit_hash,
            violations=violations
        )

    def _compute_hash(self, content: str) -> str:
        return hmac.new(self.audit_secret, content.encode("utf-8"), hashlib.sha256).hexdigest()
