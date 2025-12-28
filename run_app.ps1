# Run AI English Speaking Partner

Write-Host "Installing/Verifying Dependencies..."
cd backend
pip install -r requirements.txt

Write-Host "Starting Backend Server..."
Start-Process "http://localhost:8000/docs"
Start-Process "http://localhost:8000/"
uvicorn main:app --reload --host 0.0.0.0
