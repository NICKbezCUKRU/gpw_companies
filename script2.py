import smtplib
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
# EMAIL CREDENTIALS
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# BIZNESRADAR.PL 
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Jeśli używasz GitHub Actions
options.add_argument("--no-sandbox")  # Wymagane w GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # Rozwiązuje problemy z pamięcią
driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(180)  # Zwiększenie limitu czasu ładowania strony do 180 sekund
driver.maximize_window()
wait = WebDriverWait(driver, 10)
def login_form():
    driver.find_element("xpath", '//*[@id="main-props"]/header/div/div[2]/button[1]').click()
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[1]/label/input').send_keys(EMAIL_SENDER)
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[2]/label/input').send_keys(EMAIL_PASSWORD)
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[4]/button').click()
# GO INTO PAGE BIZNESRADAR.PL
driver.get("https://www.biznesradar.pl")
driver.implicitly_wait(5)
print(f"Page title is: {driver.title}")
# COOKIES ACCEPT
try:
    if driver.find_element("xpath", '/html/body/div[5]/div[2]/div[2]/div[2]/div[2]/button[1]'):
        driver.find_element("xpath", '/html/body/div[5]/div[2]/div[2]/div[2]/div[2]/button[1]').click()
except:
    print("Brak cookies")
# LOGIN IF YOU ARE NOT LOGGED YET
if driver.find_element("xpath", '//*[@id="main-props"]/header/div/div[2]/button[1]'):
    login_form()
    print("Udało się zalogować !")
# GO TO GPW SCANNER
driver.get("https://www.biznesradar.pl/skaner-akcji/5864d929")
print(f"Page title is: {driver.title}")
driver.execute_script("return document.readyState") == "complete"
time.sleep(10)
# html_source = driver.page_source
# print(html_source)
#---------------------------------------------------------------------------------------------------------------------------
time.sleep(60)

# GET TABLE WITH GPW COMPANIES THAT REQUIRES ACCEPTANCE CRITERIA
company_tickers = []
try:
    table_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sc-results-c"]/table/tbody')))
    table_html = table_element.get_attribute('outerHTML')
    tables = pd.read_html(table_html)
    df = tables[0]
    print(df)
    # GET TICKERS OF GPW COMPANIES FROM NAME IN BRACELESS
    for index, row in df.iterrows():
        # Wyciąganie nazwy w nawiasie z kolumny "Profil"
        nazwa = re.search(r'\((.*?)\)', row['Profil'])
        if nazwa:
            company_tickers.append(nazwa.group(1))
        else:
            if row['Profil'] == "Profil":
                continue
            else:
                company_tickers.append(row['Profil'])
except:
    print("Tickery dodane ręcznie - nie znaleziono tablicy")
