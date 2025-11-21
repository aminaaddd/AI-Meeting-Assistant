import os
import json
import datetime
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# === Répertoires ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, "client_secret.json")  # ✅ FIXED

# Fichier partagé avec l'agent
MEETING_STATE_PATH = os.path.join(BASE_DIR, "..", "current_meeting.json")

# === Scopes ===
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

# === Authentification Google ===
def get_creds():
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)

            try:
                # Try local browser flow (no include_granted_scopes)
                creds = flow.run_local_server(
                    port=0,
                    prompt="consent",
                    access_type="offline",
                    open_browser=True,
                )
            except Exception:
                # Console fallback (no include_granted_scopes)
                auth_url, _ = flow.authorization_url(
                    prompt="consent",
                    access_type="offline",
                )
                print("\nNo local browser found.")
                print("Open this URL in your browser, authorize, then paste the code:\n")
                print(auth_url, "\n")
                code = input("Paste the code here: ").strip()
                flow.fetch_token(code=code)
                creds = flow.credentials

        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    granted = getattr(creds, "scopes", []) or []
    print("✅ Scopes accordés :", granted)
    if "https://www.googleapis.com/auth/calendar.events" not in granted:
        raise RuntimeError(
            "❌ Le scope 'calendar.events' n’a pas été accordé. "
            "Active l’API Google Calendar dans le même projet que tes identifiants OAuth, "
            "supprime token.json et relance."
        )
    return creds


# === Création d’un événement Google Meet ===
def create_calendar_event_with_meet(creds, attendees_emails, duration_minutes=60, start_in_minutes=5):
    """
    Crée un événement Google Calendar avec un lien Google Meet.
    duration_minutes = durée totale du meeting
    start_in_minutes = commence dans X minutes à partir de maintenant
    """
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }

    tz = "Europe/Paris"
    now = datetime.datetime.now()

    start_dt = (now + datetime.timedelta(minutes=start_in_minutes)).replace(microsecond=0)
    end_dt = (start_dt + datetime.timedelta(minutes=duration_minutes)).replace(microsecond=0)

    event = {
        "summary": "Réunion (Meet)",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": tz},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": tz},
        "attendees": [{"email": e} for e in attendees_emails],
        "conferenceData": {
            "createRequest": {
                "requestId": "req-" + now.strftime("%Y%m%d%H%M%S")
            }
        }
    }

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"
    r = requests.post(url, headers=headers, data=json.dumps(event))

    print("Calendar create status:", r.status_code)
    print(r.text)

    if not r.ok:
        return None

    data = r.json()

    # Écriture du meeting courant dans current_meeting.json
    meeting_state = {
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "meet_link": data.get("hangoutLink"),
        "calendar_link": data.get("htmlLink"),
        "active_speakers": [],
    }

    with open(MEETING_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(meeting_state, f, indent=2)

    print("\n✅ Créneau meeting enregistré dans current_meeting.json")
    print("Meet link:", data.get("hangoutLink"))
    print("Event (Calendar):", data.get("htmlLink"))
    print("Début :", meeting_state["start"])
    print("Fin   :", meeting_state["end"])

    return data


# === Main ===
if __name__ == "__main__":
    creds = get_creds()

    guests = ["amina.addi@aivancity.education"]

    create_calendar_event_with_meet(
        creds,
        guests,
        duration_minutes=60,
        start_in_minutes=0  # 0 = commence maintenant
    )
