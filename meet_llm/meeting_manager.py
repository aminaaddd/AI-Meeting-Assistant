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
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

CURRENT_MEETING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "current_meeting.json"
)

# Fonts configuration (Inter si dispo, sinon fallback Helvetica)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BODY_FONT = "Helvetica"
TITLE_FONT = "Helvetica-Bold"

try:
    font_dir = os.path.join(BASE_DIR, "fonts")
    pdfmetrics.registerFont(TTFont("Inter", os.path.join(font_dir, "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Bold", os.path.join(font_dir, "Inter-Bold.ttf")))
    BODY_FONT = "Inter"
    TITLE_FONT = "Inter-Bold"
except Exception:
    # Si les fonts ne sont pas trouvées, on reste sur Helvetica
    BODY_FONT = "Helvetica"
    TITLE_FONT = "Helvetica-Bold"


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
    Version ChatGPT : le bot peut répondre à tout, 
    et utilise la réunion uniquement comme contexte supplémentaire.
    """

    summary_live = get_summary()
    chunks = get_all_chunks()
    last_chunks = chunks[-10:] if len(chunks) > 10 else chunks

    # Construit un contexte optionnel (pas obligatoire)
    context_txt = ""
    if summary_live:
        context_txt += "Résumé de la réunion:\n" + summary_live + "\n\n"

    if last_chunks:
        context_txt += "Extraits récents:\n"
        for c in last_chunks:
            context_txt += f"- {c.get('text', '')} / {c.get('translated', '')}\n"

    # Prompt type ChatGPT
    prompt_for_llm = f"""
Tu es un assistant IA utile, intelligent et généraliste.
Tu peux répondre à toute question, même si elle ne concerne pas la réunion.

Tu disposes éventuellement d’un contexte de réunion (ci-dessous), que tu peux utiliser 
UNIQUEMENT si c’est pertinent, sinon tu peux ignorer ce contexte et répondre normalement.

CONTEXT (optionnel) :
{context_txt}

QUESTION :
{question}

Réponds en {TARGET_LANG}, de manière claire et naturelle.
"""

    answer = translate_and_summarize(prompt_for_llm, TARGET_LANG)
    return answer


def build_summary_pdf():
    """
    PDF 'Compte-rendu de réunion' avec style glassmorphism :
    - bandeau vert en haut
    - page 1 : titre + carte infos
    - page 2 : résumé dans une carte "verre"
    - page 3 : actions dans une carte "verre"
    """

    meet = load_current_meeting()
    all_chunks = get_all_chunks()
    actions = get_action_items()

    # Texte global (on favorise la traduction)
    transcript_text = ""
    for c in all_chunks:
        t = c.get("translated") or c.get("text") or ""
        if t:
            transcript_text += t + "\n"

    # Résumé via LLM
    summary_paragraphs = summarize_meeting_paragraphs(transcript_text, TARGET_LANG)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Marges & couleurs
    x_margin = 50
    y_margin_top = height - 80
    y = y_margin_top

    ACCENT = colors.HexColor("#10B981")      # vert émeraude
    DARK = colors.HexColor("#111827")        # gris très foncé
    TEXT_MUTED = colors.HexColor("#6B7280")  # gris moyen
    BORDER = colors.HexColor("#E5E7EB")      # border light
    CARD_BG = colors.Color(1, 1, 1, alpha=0.95)  # presque blanc (effet verre)
    SHADOW = colors.Color(0, 0, 0, alpha=0.08)   # ombre légère

    # ---------- Helpers ----------

    def new_page():
        nonlocal y
        p.showPage()
        y = y_margin_top
        draw_header_band()

    def draw_page_number():
        page_num = p.getPageNumber()
        p.setFont(BODY_FONT, 9)
        p.setFillColor(TEXT_MUTED)
        p.drawRightString(width - x_margin, 30, f"Page {page_num}")

    def wrap_text(text, max_chars=95):
        lines = []
        for para in text.split("\n"):
            para = para.strip()
            if not para:
                lines.append("")
                continue
            while len(para) > max_chars:
                chunk = para[:max_chars]
                last_space = chunk.rfind(" ")
                if last_space > 0:
                    chunk = chunk[:last_space]
                lines.append(chunk)
                para = para[len(chunk):].lstrip()
            if para:
                lines.append(para)
        return lines

    def draw_paragraph(text, font=BODY_FONT, size=11, leading=16):
        nonlocal y
        p.setFont(font, size)
        p.setFillColor(DARK)

        for line in wrap_text(text):
            if y < 90:
                draw_page_number()
                new_page()
                p.setFont(font, size)
            if line == "":
                y -= leading / 2
                continue
            p.drawString(x_margin + 22, y, line)
            y -= leading

    def draw_section_title(text):
        nonlocal y
        if y < 110:
            draw_page_number()
            new_page()
        p.setFont(TITLE_FONT, 15)
        p.setFillColor(DARK)
        p.drawString(x_margin, y, text)
        y -= 8
        p.setStrokeColor(BORDER)
        p.setLineWidth(1)
        p.line(x_margin, y, width - x_margin, y)
        y -= 18

    def draw_header_band():
        """Bandeau vert en haut de chaque page."""
        p.setFillColor(ACCENT)
        p.setStrokeColor(ACCENT)
        p.rect(0, height - 32, width, 32, fill=True, stroke=False)

    def draw_glass_card(top_y, card_height, title):
        """
        Dessine une card style glassmorphism :
        - ombre légère derrière
        - fond blanc presque transparent
        - header interne avec titre
        Retourne y de départ pour le texte.
        """
        # Ombre derrière (légèrement décalée)
        p.setFillColor(SHADOW)
        p.setStrokeColor(SHADOW)
        p.roundRect(
            x_margin + 4,
            top_y - card_height - 4,
            width - 2 * x_margin,
            card_height,
            14,
            fill=True,
            stroke=False,
        )

        # Carte principale
        p.setFillColor(CARD_BG)
        p.setStrokeColor(BORDER)
        p.setLineWidth(0.8)
        p.roundRect(
            x_margin,
            top_y - card_height,
            width - 2 * x_margin,
            card_height,
            14,
            fill=True,
            stroke=True,
        )

        # Bandeau titre interne
        inner_top = top_y - 18
        p.setFillColor(colors.Color(1, 1, 1, alpha=0.85))
        p.roundRect(
            x_margin + 10,
            inner_top - 22,
            width - 2 * x_margin - 20,
            22,
            10,
            fill=True,
            stroke=False,
        )
        p.setFont(TITLE_FONT, 11)
        p.setFillColor(DARK)
        p.drawString(x_margin + 18, inner_top - 8, title)

        return inner_top - 32  # y pour commencer le texte

    # ---------- PAGE 1 : Titre + infos ----------

    draw_header_band()

    # Titre centré
    p.setFont(TITLE_FONT, 24)
    p.setFillColor(colors.white)
    title_text = "Compte-rendu de réunion"
    title_width = p.stringWidth(title_text, TITLE_FONT, 24)
    p.drawString((width - title_width) / 2, height - 50, title_text)

    # Sous-titre
    y = y_margin_top
    p.setFont(BODY_FONT, 11)
    p.setFillColor(TEXT_MUTED)
    subtitle = "Meeting Assistant – Rapport généré par IA"
    sub_width = p.stringWidth(subtitle, BODY_FONT, 11)
    p.drawString((width - sub_width) / 2, y, subtitle)
    y -= 40

    # Carte infos réunion (style "verre" léger mais plus petit)
    info_top = y
    info_height = 130

    # Ombre
    p.setFillColor(SHADOW)
    p.setStrokeColor(SHADOW)
    p.roundRect(
        x_margin + 4,
        info_top - info_height - 4,
        width - 2 * x_margin,
        info_height,
        12,
        fill=True,
        stroke=False,
    )

    # Carte principale
    p.setFillColor(CARD_BG)
    p.setStrokeColor(BORDER)
    p.roundRect(
        x_margin,
        info_top - info_height,
        width - 2 * x_margin,
        info_height,
        12,
        fill=True,
        stroke=True,
    )

    p.setFont(TITLE_FONT, 11)
    p.setFillColor(DARK)
    p.drawString(x_margin + 16, info_top - 20, "Informations de la réunion")

    p.setFont(BODY_FONT, 10)
    p.setFillColor(DARK)
    info_lines = [
        f"Date de début : {meet.get('start') or '-'}",
        f"Date de fin   : {meet.get('end') or '-'}",
        f"Lien Meet     : {meet.get('meet_link') or '-'}",
        f"Participants  : {', '.join(meet.get('participants', [])) or '-'}",
    ]
    yy = info_top - 40
    for line in info_lines:
        p.drawString(x_margin + 22, yy, line)
        yy -= 16

    y = info_top - info_height - 35

    draw_page_number()
    new_page()

    # ---------- PAGE 2 : Résumé (glass card) ----------

    draw_section_title("Résumé de la réunion")

    card_top = y
    card_height = 600  # ajuste si besoin
    y = draw_glass_card(card_top, card_height, "Synthèse générée automatiquement")

    draw_paragraph(summary_paragraphs)

    draw_page_number()
    new_page()


