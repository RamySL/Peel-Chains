from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configurer Selenium avec Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Initialiser le WebDriver
service = Service(ChromeDriverManager().install())
URL = "https://intel.arkm.com/explorer/address/"

def scrapp_tags (addr):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL+addr)

    res=[]
    parent_element = None
    try:
        # Attendre que le conteneur avec les classes 'Header_tagsContainer__AE66N' soit visible
        parent_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'Header_tagsContainer__AE66N'))
        )
    except Exception as e:
        print(f" Pas de tags ou Erreur lors du chargement du conteneur parent pour: {addr}")
       
    try:
        if parent_element:
            # Rechercher tous les éléments <div> avec la classe 'Header_tag__U86bs' à l'intérieur du parent
            tag_elements = parent_element.find_elements(By.XPATH, ".//div[contains(@class, 'Header_tag__U86bs')]")
            if tag_elements :
                for tag in tag_elements:
                    print("Texte du tag :", tag.text)
            
                res = list(map(lambda tag: tag.text, tag_elements))
        
    except Exception as e:
        print(f"Erreur lors du chargement des tags pour: {addr}")

    driver.quit()
    return res
