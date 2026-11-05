from typing import Any, Optional
from agentshield.redactor import AgentShieldRedactor

class AgentShieldCrewHook:
    """
    CrewAI task and agent guardrail hook.
    Ensures agent task outputs and tool executions never expose sensitive keys.
    """

    def __init__(self, redactor: Optional[AgentShieldRedactor] = None):
        self.redactor = redactor or AgentShieldRedactor()

    def before_task_execution(self, task: Any) -> None:
        """Inspects task description and expected output templates."""
        if hasattr(task, "description") and isinstance(task.description, str):
            res = self.redactor.redact(task.description)
            task.description = res.clean_text

    def after_task_execution(self, task_output: Any) -> Any:
        """Sanitizes task result before returning to agent or next pipeline step."""
        if isinstance(task_output, str):
            res = self.redactor.redact(task_output)
            return res.clean_text
        elif hasattr(task_output, "raw") and isinstance(task_output.raw, str):
            res = self.redactor.redact(task_output.raw)
            task_output.raw = res.clean_text
        return task_output
