import weave
from rich.progress import track
from pydantic import BaseModel

from .base import Guardrail


class GuardrailManager(weave.Model):
    guardrails: list[Guardrail]

    @weave.op()
    def guard(self, prompt: str, progress_bar: bool = True, **kwargs) -> dict:
        alerts, summaries, safe = [], "", True
        iterable = (
            track(self.guardrails, description="Running guardrails")
            if progress_bar
            else self.guardrails
        )
        for guardrail in iterable:
            response = guardrail.guard(prompt, **kwargs)
            alerts.append(
                {"guardrail_name": guardrail.__class__.__name__, "response": response}
            )
            if isinstance(response, BaseModel):
                safe = safe and response.safe
                summaries += f"**{guardrail.__class__.__name__}**: {response.explanation}\n\n---\n\n"
            else:
                safe = safe and response["safe"]
                summaries += f"**{guardrail.__class__.__name__}**: {response['summary']}\n\n---\n\n"
        return {"safe": safe, "alerts": alerts, "summary": summaries}

    @weave.op()
    def predict(self, prompt: str, **kwargs) -> dict:
        return self.guard(prompt, progress_bar=False, **kwargs)
