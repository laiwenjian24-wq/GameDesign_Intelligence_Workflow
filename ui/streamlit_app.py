"""Streamlit UI for the v1 Daily Narrative Assistant."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.v1.chat.daily_assistant import run_daily_assistant


QUICK_ACTIONS = [
    "Rin是什么身份？",
    "Branch B中Rin右腿受伤，这样能用吗？",
    "帮我续写Mombasa安全屋里Mouse和Rin的下一场戏，克制一点，不要暧昧。",
    "给我生成Branch B互相包扎场景CG prompt。",
]


def _mode_value(label: str) -> str:
    return {
        "Auto": "auto",
        "Canon QA": "canon_qa",
        "Continuity Check": "continuity_check",
        "Story Brief": "story_brief",
        "Art Prompt": "art_prompt",
    }[label]


def main() -> None:
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit is not installed.")
        print(r"Install with: E:\Desktop\python310\python.exe -m pip install streamlit")
        return

    st.set_page_config(page_title="STUPID Narrative Assistant", layout="wide")
    st.sidebar.title("STUPID Narrative Assistant")
    provider = st.sidebar.selectbox("Provider", ["fake", "deepseek"], index=0)
    mode_label = st.sidebar.selectbox(
        "Mode",
        ["Auto", "Canon QA", "Continuity Check", "Story Brief", "Art Prompt"],
        index=0,
    )
    st.sidebar.markdown("### Quick Actions")
    for action in QUICK_ACTIONS:
        if st.sidebar.button(action):
            st.session_state["request_text"] = action

    st.sidebar.markdown("### Project Status")
    st.sidebar.write("- v1 skeleton available")
    st.sidebar.write("- source policy active")
    st.sidebar.write("- real API opt-in only")

    st.title("Daily Narrative Assistant")
    default_request = st.session_state.get("request_text", QUICK_ACTIONS[0])
    user_request = st.chat_input("输入自然语言需求") or default_request

    if user_request:
        response = run_daily_assistant(
            user_request,
            provider=provider,
            mode=_mode_value(mode_label),
        )
        markdown = response.to_markdown()
        st.chat_message("user").write(user_request)
        st.chat_message("assistant").markdown(markdown)

        with st.expander("Evidence / Source Policy"):
            for item in response.evidence_or_source_policy:
                st.write(f"- {item}")
        with st.expander("Risks / Limitations"):
            for item in response.risks_or_limitations:
                st.write(f"- {item}")
        with st.expander("Debug Task Plan"):
            st.json(response.debug_task_plan)

        st.download_button(
            "Download latest response as Markdown",
            markdown,
            file_name="daily_narrative_assistant_response.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
