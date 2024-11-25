import importlib

import streamlit as st
import weave
from dotenv import load_dotenv

from guardrails_genie.guardrails import GuardrailManager
from guardrails_genie.llm import OpenAIModel

st.title(":material/robot: Guardrails Genie Playground")

load_dotenv()
weave.init(project_name="guardrails-genie")

if "guardrails" not in st.session_state:
    st.session_state.guardrails = []
if "guardrail_names" not in st.session_state:
    st.session_state.guardrail_names = []
if "guardrails_manager" not in st.session_state:
    st.session_state.guardrails_manager = None
if "initialize_guardrails" not in st.session_state:
    st.session_state.initialize_guardrails = False
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ""
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""
if "test_guardrails" not in st.session_state:
    st.session_state.test_guardrails = False
if "llm_model" not in st.session_state:
    st.session_state.llm_model = None


def initialize_guardrails():
    st.session_state.guardrails = []
    for guardrail_name in st.session_state.guardrail_names:
        if guardrail_name == "PromptInjectionSurveyGuardrail":
            survey_guardrail_model = st.sidebar.selectbox(
                "Survey Guardrail LLM", ["", "gpt-4o-mini", "gpt-4o"]
            )
            if survey_guardrail_model:
                st.session_state.guardrails.append(
                    getattr(
                        importlib.import_module("guardrails_genie.guardrails"),
                        guardrail_name,
                    )(llm_model=OpenAIModel(model_name=survey_guardrail_model))
                )
        else:
            st.session_state.guardrails.append(
                getattr(
                    importlib.import_module("guardrails_genie.guardrails"),
                    guardrail_name,
                )()
            )
    st.session_state.guardrails_manager = GuardrailManager(
        guardrails=st.session_state.guardrails
    )


openai_model = st.sidebar.selectbox(
    "OpenAI LLM for Chat", ["", "gpt-4o-mini", "gpt-4o"]
)
chat_condition = openai_model != ""

guardrails = []

guardrail_names = st.sidebar.multiselect(
    label="Select Guardrails",
    options=[
        cls_name
        for cls_name, cls_obj in vars(
            importlib.import_module("guardrails_genie.guardrails")
        ).items()
        if isinstance(cls_obj, type) and cls_name != "GuardrailManager"
    ],
)
st.session_state.guardrail_names = guardrail_names

if st.sidebar.button("Initialize Guardrails") and chat_condition:
    st.session_state.initialize_guardrails = True

if st.session_state.initialize_guardrails:
    with st.sidebar.status("Initializing Guardrails..."):
        initialize_guardrails()
        st.session_state.llm_model = OpenAIModel(model_name=openai_model)

    user_prompt = st.text_area("User Prompt", value="")
    st.session_state.user_prompt = user_prompt

    test_guardrails_button = st.button("Test Guardrails")
    st.session_state.test_guardrails = test_guardrails_button

    if st.session_state.test_guardrails:
        with st.sidebar.status("Running Guardrails..."):
            guardrails_response, call = st.session_state.guardrails_manager.guard.call(
                st.session_state.guardrails_manager, prompt=st.session_state.user_prompt
            )

        if guardrails_response["safe"]:
            st.markdown(
                f"\n\n---\nPrompt is safe! Explore prompt trace on [Weave]({call.ui_url})\n\n---\n"
            )

            with st.sidebar.status("Generating response from LLM..."):
                response, call = st.session_state.llm_model.predict.call(
                    st.session_state.llm_model,
                    user_prompts=st.session_state.user_prompt,
                )
            st.markdown(
                response.choices[0].message.content
                + f"\n\n---\nExplore LLM generation trace on [Weave]({call.ui_url})"
            )
        else:
            st.warning("Prompt is not safe!")
            st.markdown(guardrails_response["summary"])
            st.markdown(f"Explore prompt trace on [Weave]({call.ui_url})")
