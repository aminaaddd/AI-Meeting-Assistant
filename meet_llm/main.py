
import os
import threading
import queue
import tempfile
from config import TARGET_LANG
from asr import transcribe_file, transcribe_with_confidence
from mistral_client import translate_and_summarize
from recorder import AlternatingRecorder


INPUT_DEVICE_INDEX = None

def user_control_loop(meeting_flag, stop_event):
    """
    Petit thread pour écouter tes commandes clavier :
    - 'start' => active la traduction (meeting ouvert)
    - 'stop'  => désactive la traduction (meeting fermé)
    - 'quit'  => arrête tout proprement
    """
    while not stop_event.is_set():
        try:
            cmd = input().strip().lower()
        except EOFError:
            # terminal fermé
            break

        if cmd == "start":
            meeting_flag["active"] = True
            print("✅ Meeting ACTIVÉ : traduction en cours.")
        elif cmd == "stop":
            meeting_flag["active"] = False
            print("⏸ Meeting EN PAUSE : pas de traduction.")
        elif cmd == "quit":
            print("👋 Arrêt demandé.")
            stop_event.set()
            break
        else:
            print("Commande inconnue. Utilise: start | stop | quit")


def run_live_loop(seconds_per_chunk: int = 20):
    out_q: queue.Queue = queue.Queue()
    stop_event = threading.Event()

    meeting_flag = {"active": False}
    out_dir = os.path.abspath(tempfile.gettempdir())
    base_name = "chunk"

    rec = AlternatingRecorder(device_index=INPUT_DEVICE_INDEX, channels=1)
    rec.start_stream()

    # start alternating recorder in background thread
    worker = threading.Thread(target=rec.alternate_recording, args=(seconds_per_chunk, out_dir, base_name, out_q, stop_event), daemon=True)
    worker.start()

    controller = threading.Thread(
        target=user_control_loop,
        args=(meeting_flag, stop_event),
        daemon=True,
    )
    controller.start()

    try:
        while not stop_event.is_set():
            # attend qu'un nouveau chunk audio soit prêt
            try:
                filename = out_q.get(timeout=0.5)
            except queue.Empty:
                continue

            if not filename or not os.path.exists(filename):
                # chunk vide, on passe
                continue

            print(f"\n📂 Nouveau chunk: {filename}")

            # 1) Transcrire (on transcrit quand même pour voir ce qu'il entend)
            try:
                text, avg_no_speech, segs = transcribe_with_confidence(
                    filename,
                    language=None,
                    vad_filter=False,
                )
            except Exception as e:
                print(f"❌ Erreur transcription: {e}")
                continue

            if not text:
                print("… silence / bruit faible")
                continue

            print(f"📝 Reconnu: {text}")

            # 2) Vérifier si le meeting est actif
            if not meeting_flag["active"]:
                print("⏸ Meeting OFF → pas de traduction envoyée.")
                continue

            # 3) Meeting actif → on traduit avec Mistral
            try:
                out = translate_and_summarize(text, TARGET_LANG)
                print("🤖 Traduction Mistral:")
                print(out)
            except Exception as e:
                print(f"❌ Erreur Mistral: {e}")

    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel (Ctrl+C).")
        stop_event.set()

    # arrêt propre
    stop_event.set()
    worker.join(timeout=2)
    rec.stop_stream()
    print("✅ Fini.")


if __name__ == "__main__":
    run_live_loop()
