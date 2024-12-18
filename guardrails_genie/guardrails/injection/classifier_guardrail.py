from typing import Optional

import torch
import weave
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from transformers.pipelines.base import Pipeline

import wandb

from ..base import Guardrail


class PromptInjectionClassifierGuardrail(Guardrail):
    """
    A guardrail that uses a pre-trained text-classification model to classify prompts
    for potential injection attacks.

    Args:
        model_name (str): The name of the HuggingFace model or a WandB
            checkpoint artifact path to use for classification.
    """

    model_name: str = "ProtectAI/deberta-v3-base-prompt-injection-v2"
    _classifier: Optional[Pipeline] = None

    def model_post_init(self, __context):
        if self.model_name.startswith("wandb://"):
            api = wandb.Api()
            artifact = api.artifact(self.model_name.removeprefix("wandb://"))
            artifact_dir = artifact.download()
            tokenizer = AutoTokenizer.from_pretrained(artifact_dir)
            model = AutoModelForSequenceClassification.from_pretrained(artifact_dir)
        else:
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
    def guard(self, prompt: str):
        """
        Analyzes the given prompt to determine if it is safe or potentially an injection attack.

        This function uses a pre-trained text-classification model to classify the prompt.
        It calls the `classify` method to get the classification result, which includes a label
        and a confidence score. The function then calculates the confidence percentage and
        returns a dictionary with two keys:

        - "safe": A boolean indicating whether the prompt is safe (True) or an injection (False).
        - "summary": A string summarizing the classification result, including the label and the
          confidence percentage.

        Args:
            prompt (str): The input prompt to be classified.

        Returns:
            dict: A dictionary containing the safety status and a summary of the classification result.
        """
        response = self.classify(prompt)
        confidence_percentage = round(response[0]["score"] * 100, 2)
        return {
            "safe": response[0]["label"] != "INJECTION",
            "summary": f"Prompt is deemed {response[0]['label']} with {confidence_percentage}% confidence.",
        }

    @weave.op()
    def predict(self, prompt: str):
        return self.guard(prompt)
