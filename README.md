# AI Meeting Assistant  
*Real-time English-to-French meeting assistant with translation, summaries, chatbot, and PDF export.*

## Overview
AI Meeting Assistant is a real-time assistant designed to improve the quality of online meetings.  
It listens through the local microphone, transcribes speech in **English**, translates it to **French**, and provides live summaries and a final exportable meeting report.

<img width="1601" height="908" alt="image" src="https://github.com/user-attachments/assets/366358db-a2a1-40e8-88ff-c96c12e0d2dc" />


This project integrates:
-  **Real-time speech-to-text (Whisper)**  
-  **Automatic English → French translation**  
-  **Live meeting summary**  
-  **Context-aware meeting chatbot**  
-  **PDF report generation**  
-  **Google Meet invitations via OAuth**  
-  **Modern “Neon Galaxy” UI built with React**

  ---
##  Key Features
###  Real-Time Transcription  
- Uses Whisper (CTranslate2) for fast and accurate English speech recognition.  
- Processes audio directly from the user's microphone.

###  Automatic Translation (EN → FR)  
- Every recognized segment is translated instantly into French.  
- Ensures accessibility for French-speaking participants.

###  Live Summary Generation  
- The assistant builds a progressively updated summary using LLMs.  
- Summaries are always written in **French**, based on translated chunks.

<img width="1407" height="899" alt="image" src="https://github.com/user-attachments/assets/713db1a5-019e-4224-8972-2e6e0f7325e3" />


###  "Ask the Meeting" Chatbot  
Users can ask questions.

###  PDF Export  
Generates a polished meeting report including:  
- Meeting link  
- Start/end time  
- French summary  
- Full transcript (EN + FR)  
- Clean formatted layout

<img width="1379" height="896" alt="image" src="https://github.com/user-attachments/assets/e25a7ed6-83f7-45b6-9c97-502e0f613706" />


###  Neon Galaxy UI  
Custom-designed interface using:  
- TailwindCSS  
- Gradient backgrounds  
- Glassmorphism  
- Smooth shadows  
- Professional card-based layout


### Google OAuth Client Setup (for Google Meet invitations)

The AI Meeting Assistant uses the Google Calendar API to automatically create a Google Meet link and send invitations.
To enable this feature, you must configure a Google OAuth 2.0 Client.

### Create your Google Cloud project

- Go to:
https://console.cloud.google.com/
- Create a new project (or use an existing one)
- Enable the Google Calendar API

### Configure OAuth consent screen

- Go to APIs & Services → OAuth consent screen
- Choose External
- Add your application name (ex: “AI Meeting Assistant”)

---

##  Architecture
```
User Microphone
        │
        ▼
 FastAPI Backend (meet_llm)
        │
   Whisper ASR  →  English transcript
        │
        ▼
  Translation (EN → FR)
        │
        ▼
   Redis (short-term memory)
        │
        ▼
    Live Summary (LLM)
        │
        ▼
 React Frontend (Live View, Chatbot, Summary, PDF export)
```

---

##  Tech Stack

### **Backend**
- FastAPI  
- Python  
- Whisper CTranslate2  
- Mistral / OpenAI (LLM)  
- Redis  
- OAuth Google Calendar API (Meet invitations)  
- ReportLab (PDF)

### **Frontend**
- React (Vite)  
- TailwindCSS  
- Custom Neon Galaxy design  
- Polling-based live updates  

---

## ⚙️ Installation

### Clone the project  
```bash
git clone https://github.com/<username>/AI-Meeting-Assistant.git
cd AI-Meeting-Assistant
```

---

## Backend Setup

### Create virtual environment  
```bash
python -m venv .venv
```

Activate:  
- Windows:  
  ```
  .venv\Scripts\activate
  ```
- macOS/Linux:  
  ```
  source .venv/bin/activate
  ```

### Install dependencies  
```bash
pip install -r requirements.txt
```

### Configure your `.env`  
Inside `meet_llm/`:

```
MISTRAL_API_KEY=xxxx
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
```
### Run backend  
```bash
uvicorn meet_llm.main:app --reload
```
Backend runs at:  
http://127.0.0.1:8000

---

## Frontend Setup

### Install dependencies  
```bash
cd frontend
npm install
```

### Run Vite  
```bash
npm run dev
```

Frontend runs at:  
http://localhost:5173

---

## License

MIT License 


