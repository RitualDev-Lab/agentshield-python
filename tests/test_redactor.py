import unittest
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agentshield.redactor import AgentShieldRedactor

class TestAgentShieldRedactor(unittest.TestCase):
    def test_redact_openai_key(self):
        redactor = AgentShieldRedactor()
        raw = "My OpenAI key is sk-1234567890abcdef1234567890abcdef and should be secret"
        res = redactor.redact(raw)
        self.assertEqual(res.redacted_count, 1)
        self.assertNotIn("sk-1234567890abcdef", res.clean_text)
        self.assertIn("[AGENTSHIELD_REDACTED:OPENAI_KEY:", res.clean_text)

    def test_redact_aws_key(self):
        redactor = AgentShieldRedactor()
        raw = "Deploying to AWS using AKIAIOSFODNN7EXAMPLE key"
        res = redactor.redact(raw)
        self.assertEqual(res.redacted_count, 1)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", res.clean_text)
        self.assertIn("[AGENTSHIELD_REDACTED:AWS_ACCESS_KEY:", res.clean_text)

    def test_redact_proc_environ(self):
        redactor = AgentShieldRedactor()
        raw = "Let's read /proc/self/environ or check .env"
        res = redactor.redact(raw)
        self.assertGreaterEqual(res.redacted_count, 1)
        self.assertNotIn("/proc/self/environ", res.clean_text)

    def test_clean_text_unchanged(self):
        redactor = AgentShieldRedactor()
        raw = "Hello world, standard agent operation."
        res = redactor.redact(raw)
        self.assertEqual(res.redacted_count, 0)
        self.assertEqual(res.clean_text, raw)

    def test_audit_hash_deterministic(self):
        redactor = AgentShieldRedactor(audit_secret="test-salt")
        res1 = redactor.redact("test text")
        res2 = redactor.redact("test text")
        self.assertEqual(res1.audit_hash, res2.audit_hash)

if __name__ == "__main__":
    unittest.main()
