import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_active_speakers():
    """
    Heuristique actuelle :
    - On regarde toutes les tuiles participants (noeuds avec data-participant-id)
    - On récupère le nom affiché
    - S'il n'y a qu'une seule personne dans l'appel => c'est elle qui parle
    - S'il y en a plusieurs => TODO: raffiner quand tu pourras tester à plusieurs
    Retourne une liste de noms.
    """

    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    speakers = []

    # 1. Récupérer toutes les tuiles participants
    # On cible les noeuds qui ont data-participant-id (d'après ton debug)
    tiles = driver.find_elements(By.XPATH, "//*[@data-participant-id]")

    # 2. Pour chaque tuile, on regarde le texte visible (souvent le nom)
    names_found = []
    for t in tiles:
        try:
            visible_name = t.text.strip()
        except Exception:
            visible_name = ""

        if visible_name:
            if visible_name not in names_found:
                names_found.append(visible_name)

    # Logique:
    # - si une seule personne dans l'appel -> c'est elle qui parle
    if len(names_found) == 1:
        speakers = names_found[:]  # copie
    else:
        # Quand tu auras quelqu'un d'autre, on pourra raffiner ici.
        # Pour l'instant on simplifie: on ne sait pas qui parle, donc vide.
        speakers = []

    try:
        driver.quit()
    except Exception:
        pass

    return speakers


if __name__ == "__main__":
    current = get_active_speakers()
    print("Actuellement en train de parler :")
    if current:
        for s in current:
            print(" -", s)
    else:
        print("(personne détectée comme en train de parler)")
