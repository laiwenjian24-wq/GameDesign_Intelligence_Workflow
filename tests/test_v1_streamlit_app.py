from pathlib import Path


APP_PATH = Path("ui/streamlit_app.py")
README_PATH = Path("ui/README.md")


def test_streamlit_app_exists():
    assert APP_PATH.exists()


def test_streamlit_readme_exists_and_has_commands():
    text = README_PATH.read_text(encoding="utf-8")
    assert r"E:\Desktop\python310\python.exe -m pip install streamlit" in text
    assert r"E:\Desktop\python310\python.exe -m streamlit run ui/streamlit_app.py" in text


def test_streamlit_app_contains_required_ui_structures():
    text = APP_PATH.read_text(encoding="utf-8")
    assert "Provider" in text
    assert "fake" in text
    assert "deepseek" in text
    assert "Quick Actions" in text
    assert "chat_input" in text
    assert "download_button" in text
