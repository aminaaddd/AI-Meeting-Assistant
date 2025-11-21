import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

BLOCKLIST_SUBSTRINGS = [
    "more_vert",  # bouton menu ⋮
    "more_horiz",
    "present_to_all",
    "add", "Ajouter", "+",  # boutons d'ajout
]

SELF_KEYWORDS = [
    "Vous",
    "you",
    "(You)",
]

def clean_participant_names(raw_names):
    """
    Nettoie la liste brute:
    - enlève les strings techniques style `more_vert`
    - remplace '(Vous)' par rien
    - enlève les vides
    - enlève les doublons
    """
    cleaned = []

    for name in raw_names:
        n = name.strip()

        # ignorer vide
        if not n:
            continue

        # ignorer les libellés techniques genre "more_vert"
        if any(bad.lower() in n.lower() for bad in BLOCKLIST_SUBSTRINGS):
            continue

        # ignorer juste les mots qui ne sont pas des noms
        # ex: "(Vous)" ou "Vous"
        if n in SELF_KEYWORDS:
            continue

        # parfois Google Meet affiche le même nom en plein ET en court
        if n not in cleaned:
            cleaned.append(n)

    return cleaned


def get_meet_participants():
    """
    Retourne une liste de noms de participants détectés dans Google Meet.
    Hypothèse: Chrome est lancé avec --remote-debugging-port=9222
    et tu es déjà dans l'appel.
    """

    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Essayer d'ouvrir le panneau participants
    candidate_xpaths = [
        # Français
        "//button[contains(@aria-label, 'Afficher tous les participants')]",
        "//button[contains(@aria-label, 'Participants')]",
        "//button[contains(@data-tooltip, 'Participants')]",
        "//button[contains(@aria-label, 'Personnes')]",
        "//button[contains(@data-tooltip, 'Personnes')]",
        # Anglais
        "//button[contains(@aria-label, 'People')]",
        "//button[contains(@data-tooltip, 'People')]",
        "//button[contains(@aria-label, 'Show everyone')]",
    ]

    for xp in candidate_xpaths:
        try:
            btns = driver.find_elements(By.XPATH, xp)
            if btns:
                btns[0].click()
                time.sleep(1.2)
                break
        except Exception:
            pass

    # Récupérer les noms
    raw_names = []

    # 1. Première stratégie: spans dans des listitems
    try:
        spans = driver.find_elements(By.XPATH, "//div[@role='listitem']//span")
        for el in spans:
            try:
                txt = el.text.strip()
            except Exception:
                txt = ""
            if txt:
                raw_names.append(txt)
    except Exception:
        pass

    # 2. Stratégie alternative: attribut data-participant-name
    try:
        alt_items = driver.find_elements(By.XPATH, "//*[@data-participant-name]")
        for el in alt_items:
            try:
                txt = el.get_attribute("data-participant-name")
            except Exception:
                txt = ""
            if txt:
                raw_names.append(txt.strip())
    except Exception:
        pass

    # Nettoyage
    final_names = clean_participant_names(raw_names)

    # ferme proprement le driver pour pas accumuler de process
    try:
        driver.quit()
    except Exception:
        pass

    return final_names


if __name__ == "__main__":
    people = get_meet_participants()
    print("Participants détectés :")
    for p in people:
        print(" -", p)
    print(f"Total: {len(people)}")
