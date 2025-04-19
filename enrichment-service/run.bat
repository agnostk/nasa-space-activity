@echo off
call venv\Scripts\activate.bat
set PYTHONPATH=app
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --log-level trace
pause
