# audio_worker.py
import os
import threading
import queue
import tempfile
import sys

from asr import transcribe_with_confidence
from recorder import AlternatingRecorder
from mistral_client import translate_and_summarize
from redis_client import append_chunk, set_summary, get_summary

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# État global exposé à l'API
state = {
    "status": "stopped",   # "listening" | "stopped"
    "speaker": None,
    "participants": [],
}

_stop_event = threading.Event()
_worker_thread = None
_meeting_flag = {"active": False}  # True => on traduit / résume
_out_q: queue.Queue[str] = queue.Queue()

_recorder_obj: AlternatingRecorder | None = None


def _load_meeting_info():
    """
    Optionnel : lire current_meeting.json ici si tu veux garder des infos côté worker.
    Pour l'instant, on laisse ça à meeting_manager.
    """
    pass


def _recording_loop(seconds_per_chunk: int, device_index: int | None):
    """
    Thread qui enregistre l'audio en fichiers alternés dans /tmp
    et pousse le nom du fichier terminé dans _out_q.
    """
    global _recorder_obj
    tmp_dir = os.path.abspath(tempfile.gettempdir())
    base_name = "chunk"

    _recorder_obj = AlternatingRecorder(
        device_index=device_index,
        channels=1,
    )
    _recorder_obj.start_stream()

    try:
        _recorder_obj.alternate_recording(
            seconds_per_chunk,
            tmp_dir,
            base_name,
            _out_q,
            _stop_event,
        )
    finally:
        try:
            _recorder_obj.stop_stream()
        except Exception:
            pass


def _summarize_incrementally(latest_text, latest_translation):
    """
    Logique simple :
    - lire le résumé actuel depuis Redis
    - demander à Mistral une mise à jour du résumé (en FR)
    - sauvegarder
    """
    current_summary = get_summary()
    prompt = (
        "Résumé de la réunion jusqu'à présent (en français) :\n"
        f"{current_summary}\n\n"
        "Nouveau contenu (texte brut) :\n"
        f"{latest_text}\n\n"
        "Nouveau contenu (traduction en français) :\n"
        f"{latest_translation}\n\n"
        "Mets à jour le résumé de la réunion, de manière claire et concise, "
        "EN FRANÇAIS UNIQUEMENT, en gardant seulement les informations importantes."
    )

    updated = translate_and_summarize(prompt)  # on force FR
    set_summary(updated)


def _main_worker(seconds_per_chunk: int = 20, device_index: int | None = None):
    record_thread = threading.Thread(
        target=_recording_loop,
        args=(seconds_per_chunk, device_index),
        daemon=True,
    )
    record_thread.start()

    while not _stop_event.is_set():
        try:
            filename = _out_q.get(timeout=0.5)
        except queue.Empty:
            continue

        if not filename or not os.path.exists(filename):
            continue

        # Transcription brute
        try:
            text, avg_no_speech, segs = transcribe_with_confidence(
                filename,
                language=None,
                vad_filter=False,
            )
        except Exception as e:
            print(f"[worker] transcription error: {e}")
            continue

        if not text:
            continue  # silence

        # Traduction (toujours en français)
        translated = None
        if _meeting_flag["active"]:
            try:
                print("[worker] calling translate_and_summarize (FR)")
                translated = translate_and_summarize(text)  # FR par défaut
                print("[worker] translated snippet:", repr(str(translated)[:120]))
            except Exception as e:
                print("[worker] translation error:", e)
                translated = text  # fallback = texte original

        # Sauvegarde du chunk pour le dashboard (LiveTranslationCard)
        append_chunk(text, translated)

    print("[worker] audio loop ended")


def start_session():
    """
    Démarre / redémarre la capture audio.
    """
    global _worker_thread
    if state["status"] == "stopped":
        _stop_event.clear()
        _meeting_flag["active"] = True
        state["status"] = "listening"

        _worker_thread = threading.Thread(
            target=_main_worker,
            kwargs={"seconds_per_chunk": 20, "device_index": None},
            daemon=True,
        )
        _worker_thread.start()
    else:
        _meeting_flag["active"] = True
        state["status"] = "listening"


def stop_session():
    """
    Arrête tout.
    """
    _meeting_flag["active"] = False
    state["status"] = "stopped"
    _stop_event.set()
