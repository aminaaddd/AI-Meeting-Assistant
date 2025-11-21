from fastapi import FastAPI, Response
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google_meet_test.main import get_creds, create_calendar_event_with_meet

from audio_worker import state, start_session, stop_session
from meeting_manager import (
    start_meeting,
    stop_meeting,
    build_live_state,
    generate_export_report,
    answer_question,
    load_current_meeting,
    save_current_meeting,
    build_summary_pdf,
)
from meeting_manager import (
    start_meeting,
    stop_meeting,
    build_live_state,
    generate_export_report,
    build_summary_pdf,
    answer_question,
)

app = FastAPI()

from fastapi import HTTPException

@app.post("/api/meeting/create_link")
def create_link():
    try:
        creds = get_creds()

        guests = ["amina.addi@aivancity.education"]  # later you can send emails from frontend

        event = create_calendar_event_with_meet(
            creds,
            attendees_emails=guests,
            duration_minutes=60,
            start_in_minutes=0,
        )

        if not event:
            return {"ok": False}

        return {
            "ok": True,
            "meet_link": event.get("hangoutLink"),
            "calendar_link": event.get("htmlLink"),
        }
    except Exception as e:
        print("Error creating Meet link:", e)
        raise HTTPException(status_code=500, detail="Failed to create meet link")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev: autorise tout (frontend vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Schemas ----------

class StartMeetingBody(BaseModel):
    source_lang: str
    target_lang: str
    title: str | None = None

class InviteBody(BaseModel):
    emails: list[str]
    title: str
    start_time: str  # ISO string
    duration_minutes: int
    description: str | None = None

class QARequest(BaseModel):
    question: str


# ---------- Routes ----------

@app.post("/api/meeting/start")
def api_meeting_start(body: StartMeetingBody):
    """
    1. reset mémoire, note l'heure de début, configure langues
    2. démarre l'audio worker
    """
    meta = start_meeting(
        source_lang=body.source_lang,
        target_lang=body.target_lang,
    )
    start_session()
    return {
        "ok": True,
        "meeting": meta,
    }


@app.post("/api/meeting/stop")
def api_meeting_stop():
    """
    1. arrête l'audio worker
    2. fige la mémoire et renvoie le rapport final
    """
    stop_session()
    report = stop_meeting()
    return {
        "ok": True,
        "final_report": report,
    }


@app.get("/api/live/state")
def api_live_state():
    live = build_live_state(
        status=state["status"],
        speaker=state.get("speaker"),
        participants=state.get("participants"),
    )
    return live


@app.get("/api/meeting/export")
def api_meeting_export():
    """
    renvoie le résumé final + transcript brut
    (pour la page Summary + download)
    """
    return generate_export_report()


@app.post("/api/meeting/qa")
def api_meeting_qa(body: QARequest):
    """
    chatbot QA basé sur le contenu de la réunion
    """
    ans = answer_question(body.question)
    return { "answer": ans }


from fastapi import HTTPException
@app.post("/api/meeting/invite")
def api_meeting_invite(body: InviteBody):
    try:
        creds = get_creds()

        # body.emails is already a list of multiple emails
        event = create_calendar_event_with_meet(
            creds,
            attendees_emails=body.emails,  # 👈 MULTIPLE INVITEES HERE
            duration_minutes=body.duration_minutes,
            start_in_minutes=0
        )

        if not event:
            return {"ok": False, "error": "Calendar API error"}

        meet_link = event.get("hangoutLink")

        save_current_meeting(
            meet_link=meet_link,
            participants=body.emails,    # 👈 SAVE MULTIPLE PARTICIPANTS
        )

        return {
            "ok": True,
            "meet_link": meet_link,
            "invited": body.emails
        }

    except Exception as e:
        print("Error creating Meet link:", e)
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/meeting/info")
def api_meeting_info():
    """
    Récupérer les infos du meeting courant (pour la HomePage)
    """
    return load_current_meeting()

@app.get("/api/meeting/summary_pdf")
def get_meeting_summary_pdf():
    pdf_bytes = build_summary_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="meeting_summary.pdf"'
        },
    )
    

