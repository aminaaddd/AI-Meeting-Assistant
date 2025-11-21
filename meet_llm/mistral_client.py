# mistral_client.py
from mistralai import Mistral
from config import MISTRAL_API_KEY

try:
    from mistralai.exceptions import MistralAPIException
except ImportError:
    MistralAPIException = Exception

# Client global Mistral
_client = Mistral(api_key=MISTRAL_API_KEY)


def ask_mistral(
    prompt: str,
    model: str = "mistral-small-latest",
    temperature: float = 0.0,
):
    """
    Appel Mistral robuste.
    Retourne:
      - str : réponse du modèle
      - None : en cas d'erreur (429, quota, etc.)
    """
    system = (
        "You are a precise, literal translator and summarizer. "
        "Do not add information, do not infer, and avoid paraphrasing unless asked. "
        "Return only the requested formats."
    )

    try:
        resp = _client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        content = resp.choices[0].message.content

        # Parfois le SDK renvoie une liste de blocs
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )

        return content.strip()

    except MistralAPIException as e:
        print("[ERROR] Mistral API error:", e)
        return None

    except Exception as e:
        print("[ERROR] Unexpected Mistral error:", e)
        return None


def translate_and_summarize(text: str, target_lang: str = "fr") -> str:
    """
    Traduit le texte en FRANÇAIS.
    On ignore la valeur réelle de target_lang et on force le français.
    Si l'API échoue, on renvoie le texte source (fallback doux).
    """
    prompt = (
        "Traduire le texte suivant en **français**.\n"
        "- Réponds UNIQUEMENT en français.\n"
        "- Ne donne aucune explication.\n"
        "- Ne mélange pas d'autres langues.\n\n"
        f"Texte source :\n{text}"
    )

    print("[mistral_client] translate_and_summarize (FR)")

    result = ask_mistral(prompt, temperature=0.0)

    if result is None:
        print("[mistral_client] Fallback: Mistral a retourné None, on renvoie le texte source.")
        return text

    return result.strip()


def summarize_meeting_paragraphs(text: str, target_lang: str = "fr") -> str:
    """
    Génère un compte-rendu clair, structuré, en FRANÇAIS.
    (utilisé pour le résumé final / PDF)
    """
    if not text.strip():
        return "Résumé non disponible (aucun contenu exploitable)."

    prompt = (
        "Ton rôle : rédiger un compte-rendu clair, structuré et synthétique d'une réunion.\n"
        "- Le compte-rendu doit être UNIQUEMENT en français.\n"
        "- Ne pas mélanger plusieurs langues dans la réponse.\n"
        "- Ne pas copier mot pour mot les phrases du texte source.\n"
        "- Structure en 3 à 6 paragraphes, sans listes à puces.\n"
        "- Mentionner : le contexte de la réunion, les thèmes principaux abordés, "
        "les points clés discutés, les décisions importantes, et les actions à suivre.\n"
        "- Ignore les répétitions, hésitations et phrases sans intérêt.\n\n"
        "Voici la transcription à analyser et synthétiser :\n"
        f"{text}"
    )

    print("[mistral_client] summarize_meeting_paragraphs (FR)")

    result = ask_mistral(prompt, temperature=0.3)

    if result is None:
        print("[INFO] Résumé indisponible (erreur modèle).")
        return "Résumé non disponible (le service de génération automatique est temporairement indisponible)."

    return result.strip()
