import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agentshield.sandbox import sanitize_env, AgentShieldSandbox

class TestAgentShieldSandbox(unittest.TestCase):
    def test_sanitize_env_masks_secrets(self):
        dirty = {
            "PATH": "/usr/bin",
            "AWS_SECRET_ACCESS_KEY": "supersecretvalue",
            "OPENAI_API_KEY": "sk-1234567890abcdef1234567890abcdef",
            "CUSTOM_SECRET_TOKEN": "mysecret",
            "SAFE_SETTING": "production"
        }
        clean = sanitize_env(dirty)
        self.assertEqual(clean["PATH"], "/usr/bin")
        self.assertEqual(clean["SAFE_SETTING"], "production")
        self.assertEqual(clean["AWS_SECRET_ACCESS_KEY"], "agentshield_mock_aws_secr")
        self.assertEqual(clean["OPENAI_API_KEY"], "agentshield_mock_openai_a")
        self.assertEqual(clean["AGENTSHIELD_AIR_GAPPED"], "1")

    def test_sandbox_run_command_echo(self):
        sandbox = AgentShieldSandbox()
        res = sandbox.run_command(["python", "-c", "print('hello from sandbox')"])
        self.assertIn("hello from sandbox", res.clean_text)

if __name__ == "__main__":
    unittest.main()
