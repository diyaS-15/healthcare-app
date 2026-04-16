# healthcare-app

This repository now uses a single UI: the Streamlit app at `Frontend/UserProfile.py`.

## Run the app

From the repo root on Windows PowerShell:

```powershell
.\myenv\Scripts\python.exe -m streamlit run Frontend\UserProfile.py
```

If you need to install Python dependencies into the project virtual environment first:

```powershell
.\myenv\Scripts\python.exe -m pip install -r requirements.txt
```

## Project entrypoints

- Streamlit UI: `Frontend/UserProfile.py`
- OCR script: `main.py`
- Risk scoring logic: `Risk_Score/`
- Backend API code: `blood-report-ai/backend/`
