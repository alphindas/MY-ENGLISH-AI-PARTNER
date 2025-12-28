@echo off
start http://localhost:8000/
python -m uvicorn main:app --reload --host 0.0.0.0
