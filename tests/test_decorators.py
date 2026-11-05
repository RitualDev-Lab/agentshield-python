import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agentshield import protect, shield

class TestDecorators(unittest.TestCase):
    def test_protect_bare_decorator(self):
        @protect
        def run_agent_tool(arg: str) -> str:
            return f"Processed: {arg}"

        res = run_agent_tool("Deploy with sk-1234567890abcdef1234567890abcdef key")
        self.assertNotIn("sk-1234567890abcdef", res)
        self.assertIn("[AGENTSHIELD_REDACTED:OPENAI_KEY:", res)

    def test_shield_protect_decorator(self):
        @shield.protect
        def execute_task(task_input: str) -> str:
            return "Output: AKIAIOSFODNN7EXAMPLE is configured"

        res = execute_task("Safe prompt")
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", res)
        self.assertIn("[AGENTSHIELD_REDACTED:AWS_ACCESS_KEY:", res)

    def test_protect_strict_mode(self):
        @protect(strict=True)
        def leaky_function() -> str:
            return "Leaking sk-1234567890abcdef1234567890abcdef"

        with self.assertRaises(PermissionError):
            leaky_function()

if __name__ == "__main__":
    unittest.main()
