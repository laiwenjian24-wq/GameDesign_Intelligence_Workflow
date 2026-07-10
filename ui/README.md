# STUPID Narrative Assistant UI

This is a local Streamlit demo for the v1 Daily Narrative Assistant prototype.

Install Streamlit:

```powershell
E:\Desktop\python310\python.exe -m pip install streamlit
```

Run the app:

```powershell
E:\Desktop\python310\python.exe -m streamlit run ui/streamlit_app.py
```

Notes:

- The default `fake` provider does not call any API.
- The `deepseek` provider requires `DEEPSEEK_API_KEY` in the environment.
- The UI does not replace the CLI.
- This is a local resume demo / daily assistant prototype.
- The app does not modify Canon, source files, or `import_manifest.json`.
