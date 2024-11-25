from typing import Optional

import torch
import weave
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from transformers.pipelines.base import Pipeline

from ..base import Guardrail


class PromptInjectionProtectAIGuardrail(Guardrail):
    model_name: str = "ProtectAI/deberta-v3-base-prompt-injection-v2"
    _classifier: Optional[Pipeline] = None

    def model_post_init(self, __context):
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self._classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            max_length=512,
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        )

    @weave.op()
    def classify(self, prompt: str):
        return self._classifier(prompt)

    @weave.op()
    def predict(self, prompt: str):
        response = self.classify(prompt)
        return {"safe": response[0]["label"] != "INJECTION"}

    @weave.op()
    def guard(self, prompt: str):
        response = self.classify(prompt)
        confidence_percentage = round(response[0]["score"] * 100, 2)
        return {
            "safe": response[0]["label"] != "INJECTION",
            "summary": f"Prompt is deemed {response[0]['label']} with {confidence_percentage}% confidence.",
        }
