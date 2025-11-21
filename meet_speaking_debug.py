import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def debug_dump_meet_nodes():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    print("=== DEBUG DUMP GOOGLE MEET NODES ===")

    # 1. On récupère les blocs qui ressemblent à des vignettes de participants.
    # Souvent, chaque participant a un conteneur <div role="listitem"> ou <div data-participant-id=...>
    # Donc on va être large et prendre tous les div qui ont un role listitem OU data-participant-id
    candidates = driver.find_elements(
        By.XPATH,
        "//div[@role='listitem'] | //*[@data-participant-id]"
    )

    print(f"Nombre de candidats trouvés: {len(candidates)}")
    print("")

    idx = 0
    for node in candidates:
        idx += 1
        try:
            aria_label = node.get_attribute("aria-label")
        except Exception:
            aria_label = ""
        try:
            cls = node.get_attribute("class")
        except Exception:
            cls = ""
        try:
            data_pid = node.get_attribute("data-participant-id")
        except Exception:
            data_pid = ""
        try:
            text_content = node.text
        except Exception:
            text_content = ""

        print(f"--- NODE #{idx} ---")
        print(f"class= {cls}")
        print(f"aria-label= {aria_label}")
        print(f"data-participant-id= {data_pid}")
        print("visible text=")
        print(text_content.strip())
        print("-------------------\n")

    try:
        driver.quit()
    except Exception:
        pass

if __name__ == "__main__":
    debug_dump_meet_nodes()
