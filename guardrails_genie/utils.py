import pandas as pd
import streamlit as st
import weave
from transformers.trainer_callback import (
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)


class EvaluationCallManager:
    """
    Manages the evaluation calls for a specific project and entity in Weave.

    This class is responsible for initializing and managing evaluation calls associated with a
    specific project and entity. It provides functionality to collect guardrail guard calls
    from evaluation predictions and scores, and render these calls into a structured format
    suitable for display in Streamlit.

    Args:
        entity (str): The entity name.
        project (str): The project name.
        call_id (str): The call id.
        max_count (int): The maximum number of guardrail guard calls to collect from the evaluation.
    """

    def __init__(self, entity: str, project: str, call_id: str, max_count: int = 10):
        self.base_call = weave.init(f"{entity}/{project}").get_call(call_id=call_id)
        self.max_count = max_count
        self.show_warning_in_app = False
        self.call_list = []

    def collect_guardrail_guard_calls_from_eval(self):
        """
        Collects guardrail guard calls from evaluation predictions and scores.

        This function iterates through the children calls of the base evaluation call,
        extracting relevant guardrail guard calls and their associated scores. It stops
        collecting calls if it encounters an "Evaluation.summarize" operation or if the
        maximum count of guardrail guard calls is reached. The collected calls are stored
        in a list of dictionaries, each containing the input prompt, outputs, and score.

        Returns:
            list: A list of dictionaries, each containing:
                - input_prompt (str): The input prompt for the guard call.
                - outputs (dict): The outputs of the guard call.
                - score (dict): The score of the guard call.
        """
        guard_calls, count = [], 0
        for eval_predict_and_score_call in self.base_call.children():
            if "Evaluation.summarize" in eval_predict_and_score_call._op_name:
                break
            guardrail_predict_call = eval_predict_and_score_call.children()[0]
            guard_call = guardrail_predict_call.children()[0]
            score_call = eval_predict_and_score_call.children()[1]
            guard_calls.append(
                {
                    "input_prompt": str(guard_call.inputs["prompt"]),
                    "outputs": dict(guard_call.output),
                    "score": dict(score_call.output),
                }
            )
            count += 1
            if count >= self.max_count:
                self.show_warning_in_app = True
                break
        return guard_calls

    def render_calls_to_streamlit(self):
        """
        Renders the collected guardrail guard calls into a pandas DataFrame suitable for
        display in Streamlit.

        This function processes the collected guardrail guard calls stored in `self.call_list` and
        organizes them into a dictionary format that can be easily converted into a pandas DataFrame.
        The DataFrame contains columns for the input prompts, the safety status of the outputs, and
        the correctness of the predictions for each guardrail.

        The structure of the DataFrame is as follows:
        - The first column contains the input prompts.
        - Subsequent columns contain the safety status and prediction correctness for each guardrail.

        Returns:
            pd.DataFrame: A DataFrame containing the input prompts, safety status, and prediction
                          correctness for each guardrail.
        """
        dataframe = {
            "input_prompt": [
                call["input_prompt"] for call in self.call_list[0]["calls"]
            ]
        }
        for guardrail_call in self.call_list:
            dataframe[guardrail_call["guardrail_name"] + ".safe"] = [
                call["outputs"]["safe"] for call in guardrail_call["calls"]
            ]
            dataframe[guardrail_call["guardrail_name"] + ".prediction_correctness"] = [
                call["score"]["correct"] for call in guardrail_call["calls"]
            ]
        return pd.DataFrame(dataframe)


class StreamlitProgressbarCallback(TrainerCallback):
    """
    StreamlitProgressbarCallback is a custom callback for the Hugging Face Trainer
    that integrates a progress bar into a Streamlit application. This class updates
    the progress bar at each training step, providing real-time feedback on the
    training process within the Streamlit interface.

    Attributes:
        progress_bar (streamlit.delta_generator.DeltaGenerator): A Streamlit progress
            bar object initialized to 0 with the text "Training".

    Methods:
        on_step_begin(args, state, control, **kwargs):
            Updates the progress bar at the beginning of each training step. The progress
            is calculated as the percentage of completed steps out of the total steps.
            The progress bar text is updated to show the current step and the total steps.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_bar = st.progress(0, text="Training")

    def on_step_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        super().on_step_begin(args, state, control, **kwargs)
        self.progress_bar.progress(
            (state.global_step * 100 // state.max_steps) + 1,
            text=f"Training {state.global_step} / {state.max_steps}",
        )
