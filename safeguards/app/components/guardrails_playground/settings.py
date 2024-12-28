import importlib

from fasthtml.common import Div, Form, Input, Label, Option, Select, Span


def GuardrailsPlaygroundLLMSelection():
    return Div(
        Form(
            Div(
                Span("Select the LLM for Playground Chat", cls="label-text"),
                cls="label",
            ),
            Select(
                Option(""),
                Option("gpt-4o"),
                Option("gpt-4o-mini"),
                cls="select select-bordered",
                name="playground_llm_selection",
                hx_post="/playground_llm_selection_update",
                hx_target="#playground_llm_selection_target",
            ),
            Div(id="playground_llm_selection_target"),
            cls="form-control w-full max-w-xs",
        ),
        cls="container mx-auto p-6",
    )


def GuardrailsPlaygroundCheckbox(label: str):
    return Label(
        Input(
            type="checkbox",
            value=label,
            cls="checkbox checkbox-primary",
            name="selected_playground_guardrails",
            hx_post="/playground_guardrail_selection",
            hx_target="#playground_guardrail_selection_target",
            hx_trigger="change",
        ),
        Span(label),
        cls="flex items-center gap-2",
    )


def GuardrailsPlaygroundGuardrailSelection():
    guardrail_checkboxes = [
        GuardrailsPlaygroundCheckbox(label=cls_name)
        for cls_name, _ in vars(
            importlib.import_module("safeguards.guardrails")
        ).items()
        if not cls_name.startswith("__") and cls_name.endswith("Guardrail")
    ]
    return Div(
        Form(
            Div(
                Span("Select Guardrails", cls="label-text"),
                cls="label",
            ),
            *guardrail_checkboxes,
            cls="flex flex-col gap-4 p-6 rounded-lg",
        ),
        Div(id="playground_guardrail_selection_target"),
        cls="container mx-auto p-6",
    )


def GuardrailsPlaygroundSettings():
    return Div(
        GuardrailsPlaygroundLLMSelection(),
        GuardrailsPlaygroundGuardrailSelection(),
        cls="flex flex-col",
    )