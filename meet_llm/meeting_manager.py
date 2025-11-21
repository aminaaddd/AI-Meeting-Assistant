import os
import json
import datetime
from dotenv import load_dotenv

from redis_client import (
    reset_meeting_memory,
    append_chunk,
    get_all_chunks,
    get_summary,
    set_summary,
    add_action_item,
    get_action_items,
    get_last_chunks,
)

from mistral_client import translate_and_summarize, summarize_meeting_paragraphs
from config import TARGET_LANG
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CURRENT_MEETING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "current_meeting.json"
)

load_dotenv()


def load_current_meeting():
    """
    Lit current_meeting.json qui contient meet_link etc.
    Garantit toujours les clés : meet_link, start, end, participants.
    """
    if not os.path.exists(CURRENT_MEETING_FILE):
        return {
            "meet_link": None,
            "start": None,
            "end": None,
            "participants": [],
        }

    try:
        with open(CURRENT_MEETING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # En cas de fichier corrompu ou lecture impossible
        return {
            "meet_link": None,
            "start": None,
            "end": None,
            "participants": [],
        }

    # On s'assure que toutes les clés existent
    return {
        "meet_link": data.get("meet_link"),
        "start": data.get("start"),
        "end": data.get("end"),
        "participants": data.get("participants", []),
    }


def save_current_meeting(meet_link=None, start=None, end=None, participants=None):
    """
    Écrit dans current_meeting.json en conservant les champs existants.
    """
    data = load_current_meeting()

    if meet_link is not None:
        data["meet_link"] = meet_link
    if start is not None:
        data["start"] = start
    if end is not None:
        data["end"] = end
    if participants is not None:
        data["participants"] = participants

    with open(CURRENT_MEETING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def start_meeting(source_lang, target_lang):
    """
    Appelé par /api/meeting/start.
    - reset Redis memory
    - note l'heure de début
    - (optionnel) configure langues
    """
    reset_meeting_memory()

    now_iso = datetime.datetime.now().isoformat(timespec="seconds")
    save_current_meeting(start=now_iso)

    return {
        "ok": True,
        "start": now_iso,
    }


def stop_meeting():
    """
    Appelé par /api/meeting/stop.
    - set end time
    - renvoie un résumé final exploitable
    """
    now_iso = datetime.datetime.now().isoformat(timespec="seconds")
    save_current_meeting(end=now_iso)

    summary_live = get_summary()
    actions = get_action_items()

    final_report = {
        "ended_at": now_iso,
        "summary": summary_live,
        "actions": actions,
    }
    return final_report


def build_live_state(status, speaker=None, participants=None):
    """
    Construit l'état live retourné par /api/meeting/info.
    """
    meet = load_current_meeting()
    last_chunks = get_last_chunks(n=6)

    formatted_chunks = [
        {
            "source": c.get("text", ""),
            "translated": c.get("translated", ""),
        }
        for c in last_chunks
    ]

    return {
        "status": status,
        "meet_link": meet.get("meet_link"),
        "participants": participants or meet.get("participants", []),
        "speaker": speaker or None,
        "recent_chunks": formatted_chunks,
    }


def generate_export_report():
    meet = load_current_meeting()
    all_chunks = get_all_chunks()
    actions_list = get_action_items()

    # 1) On récupère un éventuel résumé déjà construit en live (si tu en as).
    summary_live = get_summary()

    # 2) Si pas de résumé live, on en génère un propre
    if not summary_live:
        lines = []

        for c in all_chunks:
            # On favorise la traduction (normalement déjà en TARGET_LANG)
            if c.get("translated"):
                lines.append(c["translated"])
            elif c.get("text"):
                lines.append(c["text"])

        # On limite un peu la taille pour éviter d'envoyer 50km de texte
        # (optionnel, ajuste 4000/8000 selon ton usage)
        context_text = "\n".join(lines)[-8000:]

        if context_text.strip():
            summary_live = summarize_meeting_paragraphs(context_text, TARGET_LANG)
        else:
            summary_live = "Résumé non disponible (aucun contenu exploitable)."

    return {
        "title": f"Meeting report {meet.get('start','')}",
        "meet_link": meet.get("meet_link", ""),
        "start": meet.get("start"),
        "end": meet.get("end"),
        "summary": summary_live,
        "actions": actions_list,
        "raw_transcript": all_chunks,
    }


def answer_question(question: str):
    """
    QA sur la réunion.
    Utilise le résumé + derniers chunks comme contexte.
    """
    summary_live = get_summary()
    chunks = get_all_chunks()
    last_chunks = chunks[-10:] if len(chunks) > 10 else chunks

    context_txt = "Résumé actuel de la réunion:\n" + (summary_live or "") + "\n\n"
    context_txt += "Extraits récents (avec traduction):\n"
    for c in last_chunks:
        context_txt += f"- {c.get('text', '')} / {c.get('translated', '')}\n"

    prompt_for_llm = (
        f"{context_txt}\n\n"
        f"Question de l'utilisateur: {question}\n"
        f"Réponds clairement et brièvement en {TARGET_LANG}."
    )

    answer = translate_and_summarize(prompt_for_llm, TARGET_LANG)
    return answer

def build_summary_pdf():
    """
    Construit un PDF 'Compte-rendu de réunion' avec :
    - infos meeting
    - résumé en paragraphes (LLM)
    - liste des actions
    Retourne: bytes du PDF (pour une réponse HTTP).
    """
    meet = load_current_meeting()
    all_chunks = get_all_chunks()
    actions = get_action_items()

    # On construit un texte global (on privilégie la traduction si dispo)
    transcript_text = ""
    for c in all_chunks:
        t = c.get("translated") or c.get("text") or ""
        if t:
            transcript_text += t + "\n"

    # Résumé en paragraphes via LLM
    summary_paragraphs = summarize_meeting_paragraphs(transcript_text, TARGET_LANG)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marges
    x_margin = 40
    y = height - 60

    def write_line(line: str):
        nonlocal y
        if y < 80:  # nouvelle page si plus de place
            p.showPage()
            y = height - 60
        p.drawString(x_margin, y, line)
        y -= 16

    # Titre
    p.setFont("Helvetica-Bold", 16)
    write_line("Compte-rendu de réunion")

    p.setFont("Helvetica", 10)
    write_line(f"Date de début : {meet.get('start') or '-'}")
    write_line(f"Date de fin   : {meet.get('end') or '-'}")
    write_line(f"Lien Meet     : {meet.get('meet_link') or '-'}")
    participants = ", ".join(meet.get("participants", [])) or "-"
    write_line(f"Participants  : {participants}")

    y -= 20

    # Section résumé
    p.setFont("Helvetica-Bold", 12)
    write_line("Résumé")

    p.setFont("Helvetica", 10)

    # On découpe le texte en lignes qui tiennent dans la page
    max_chars = 100  # ajuster si tu veux plus large
    for para in summary_paragraphs.split("\n"):
        para = para.strip()
        if not para:
            y -= 8
            continue

        while len(para) > max_chars:
            line = para[:max_chars]
            # couper proprement sur l'espace
            last_space = line.rfind(" ")
            if last_space > 0:
                line = line[:last_space]
            write_line(line)
            para = para[len(line):].lstrip()
        if para:
            write_line(para)

    y -= 20

    # Section actions
    if actions:
        p.setFont("Helvetica-Bold", 12)
        write_line("Actions à suivre")
        p.setFont("Helvetica", 10)
        for a in actions:
            # chaque action sur une ligne
            write_line(f"- {a}")
    else:
        p.setFont("Helvetica-Bold", 12)
        write_line("Actions à suivre")
        p.setFont("Helvetica", 10)
        write_line("Aucune action enregistrée.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.getvalue()
