# AI English Speaking Partner

AI English Speaking Partner is a full-stack web application designed to help users practice spoken English through natural voice and text-based conversations. The application acts as an AI conversation partner that responds intelligently, speaks back to the user, and provides grammar correction to improve fluency and confidence.

---

## Features

- Voice-to-text input using browser-based speech recognition  
- AI-generated conversational responses using Google Gemini  
- Text-to-speech output for natural interaction  
- Grammar correction with contextual feedback  
- Session-based conversation memory for contextual continuity  
- Clean and modern user interface with smooth animations  
- Fast and lightweight backend API  

---

## Technology Stack

### Frontend
- HTML5  
- CSS3 (Glassmorphism design and animations)  
- Vanilla JavaScript  
- Web Speech API (Speech Recognition and Speech Synthesis)

### Backend
- Python 3  
- FastAPI  
- Uvicorn  
- Google Gemini API  
- python-dotenv  

---

## Application Workflow

1. The user speaks or types a message in English  
2. The browser converts speech input into text  
3. The message is sent to the backend via a REST API  
4. The backend forwards the message and conversation history to the AI model  
5. The AI returns a structured JSON response containing:
   - AI reply  
   - Grammar correction (if applicable)  
6. The frontend displays the response and reads it aloud  

---

## Project Structure


