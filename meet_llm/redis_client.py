import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_meeting_id():
    """
    Pour l'instant on utilise une seule réunion active => 'current'.
    Plus tard tu peux mettre un vrai ID unique par réunion.
    """
    return "current"

def append_chunk(text, translated):
    """
    Ajoute une nouvelle phrase dans l'historique brut.
    """
    mid = get_meeting_id()
    entry = {"text": text, "translated": translated}
    r.rpush(f"meeting:{mid}:raw", json.dumps(entry))

def get_all_chunks():
    """
    Lis l'historique brut (toutes les phrases).
    """
    mid = get_meeting_id()
    raw = r.lrange(f"meeting:{mid}:raw", 0, -1)
    out = []
    for item in raw:
        try:
            out.append(json.loads(item))
        except Exception:
            pass
    return out

def set_summary(summary_text):
    """
    Sauvegarde le résumé live.
    """
    mid = get_meeting_id()
    r.set(f"meeting:{mid}:summary", summary_text or "")

def get_summary():
    mid = get_meeting_id()
    return r.get(f"meeting:{mid}:summary") or ""

def add_action_item(item_text):
    """
    Sauvegarde les actions / next steps détectés.
    """
    mid = get_meeting_id()
    r.rpush(f"meeting:{mid}:actions", item_text)

def get_action_items():
    mid = get_meeting_id()
    return r.lrange(f"meeting:{mid}:actions", 0, -1)

def reset_meeting_memory():
    """
    Appelé quand la réunion démarre.
    On efface l'ancienne mémoire.
    """
    mid = get_meeting_id()
    r.delete(f"meeting:{mid}:raw")
    r.delete(f"meeting:{mid}:summary")
    r.delete(f"meeting:{mid}:actions")
    
def get_last_chunks(n=6):
    """
    Retourne les n derniers chunks (texte source + traduction).
    """
    mid = get_meeting_id()
    raw = r.lrange(f"meeting:{mid}:raw", 0, -1)
    out = []
    for item in raw:
        try:
            out.append(json.loads(item))
        except Exception:
            pass
    return out[-n:]

# --- meeting info helpers expected by meeting_manager.py ---

def _info_key():
    return f"meeting:{get_meeting_id()}:info"

def save_current_meeting(meeting: dict) -> None:
    """
    Store the current meeting metadata (dict).
    Example keys often used: id, status, title, participants, link, etc.
    """
    r.set(_info_key(), json.dumps(meeting or {}))

def load_current_meeting(default: dict | None = None) -> dict:
    """
    Load current meeting metadata. Returns a sensible default if missing.
    """
    raw = r.get(_info_key())
    if not raw:
        return default or {"id": get_meeting_id(), "status": "idle", "title": "", "participants": []}
    try:
        return json.loads(raw)
    except Exception:
        return default or {"id": get_meeting_id(), "status": "idle", "title": "", "participants": []}

def delete_current_meeting() -> None:
    """Remove current meeting metadata."""
    r.delete(_info_key())


