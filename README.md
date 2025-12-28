# AI English Speaking Partner

A beautiful, full-stack web application for practicing English conversation with an AI.

## 🚀 How to Run (Quick Way)

**Option 1: Windows Script**
Double-click or run the `run_app.ps1` file in the main folder.

**Option 2: Manual Terminal**
1.  Open your terminal in the project folder.
2.  Navigate to backend: `cd backend`
3.  Start the server:
    ```powershell
    python -m uvicorn main:app --reload
    ```
4.  Open `http://localhost:8000/` in your browser.

## ✨ Features
- **Voice Interaction**: Speak naturally to the AI.
- **Smart Corrections**: Get gentle grammar tips.
- **Premium Design**: Glassmorphism UI with vibrant animations.
- **Context Memory**: Remembers what you talked about.

## 🔑 Setup (First Time Only)
1.  **Install Python Dependencies**:
    ```powershell
    cd backend
    pip install -r requirements.txt
    ```
2.  **Set API Key**:
    - Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Create/Edit `backend/.env`.
    - Add: `GOOGLE_API_KEY=your_key_here`.
