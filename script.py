import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
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
driver.maximize_window()

def login_form():
    driver.find_element("xpath", '//*[@id="main-props"]/header/div/div[2]/button[1]').click()
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[1]/label/input').send_keys(EMAIL_SENDER)
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[2]/label/input').send_keys(EMAIL_PASSWORD)
    driver.find_element("xpath", '//*[@id="tabs-dialog-login"]/div/div[1]/div/form/div[4]/button').click()
# GO INTO PAGE BIZNESRADAR.PL
driver.get("https://biznesradar.pl")
driver.implicitly_wait(1)
# COOKIES ACCEPT
if driver.find_element("xpath", '/html/body/div[5]/div[2]/div[2]/div[2]/div[2]/button[1]'):
    driver.find_element("xpath", '/html/body/div[5]/div[2]/div[2]/div[2]/div[2]/button[1]').click()
# LOGIN IF YOU ARE NOT LOGGED YET
if driver.find_element("xpath", '//*[@id="main-props"]/header/div/div[2]/button[1]'):
    login_form()
# GO TO GPW SCANNER
driver.get("https://www.biznesradar.pl/skaner-akcji/5864d929")
time.sleep(5)
# GET TABLE WITH GPW COMPANIES THAT REQUIRES ACCEPTANCE CRITERIA
table_element = driver.find_element("xpath", '//*[@id="sc-results-c"]/table')

table_html = table_element.get_attribute('outerHTML')
tables = pd.read_html(table_html)
df = tables[0]
print(df)
# GET TICKERS OF GPW COMPANIES FROM NAME IN BRACELESS
company_tickers = []
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

print(company_tickers)
data_to_publish = pd.DataFrame(columns=["Ticker", "Data", "Wskaźniki", "Krzywe kroczące"])

for ticker in company_tickers:
    url = f"https://www.biznesradar.pl/analiza-techniczna-wskazniki/{ticker}"
    driver.get(url)
    try:
        driver.find_element("xpath", "/html/body/div[5]/div[1]/a").click()
    except:
        print("nie było reklamy")
    element = driver.find_element("xpath","//a[contains(@class, 'switch-1h')]")
    if element.get_attribute('class') != "btn switch-1d btnOn":
        driver.find_element("xpath", "//a[contains(@class, 'switch-1h')]").click()
    date = driver.find_element("xpath", '//*[@id="profile-indicators"]/div[3]/div[1]/div[1]/div[2]/span').text
    wskazniki = driver.find_element("xpath", '//*[@id="profile-indicators"]/div[3]/div[1]/div[2]/div[1]/span').text
    krzywe_kroczace = driver.find_element("xpath", '//*[@id="profile-indicators"]/div[3]/div[1]/div[2]/div[2]/span').text
    data_to_publish.loc[len(data_to_publish)] = [ticker, date, wskazniki, krzywe_kroczace]
print(data_to_publish)
mask = (data_to_publish["Wskaźniki"] == "neutralnie") | (data_to_publish["Krzywe kroczące"] == "neutralnie")
mask2 = (data_to_publish["Wskaźniki"] == "brak danych") | (data_to_publish["Krzywe kroczące"] == "brak danych")
data_to_publish = data_to_publish.drop(data_to_publish[mask].index)
data_to_publish = data_to_publish.drop(data_to_publish[mask2].index)
print("bez neutralnych i braku danych")
print(data_to_publish)
#LOGOUT
driver.find_element("xpath",'//*[@id="loginbox"]/button[3]')
driver.quit()


# 🔹 Konwersja do HTML
table_html = data_to_publish.to_html(index=False)
table2_html = df.to_html(index=False)
# 🔹 Ustawienia e-maila
SMTP_SERVER = "smtp.gmail.com"  # Dla Gmaila
SMTP_PORT = 587

# 🔹 Tworzenie wiadomości e-mail
msg = MIMEMultipart()
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER
msg["Subject"] = "Automatyczna tabela z Python"

html_body = f"""
<html>
<body>
    <p>Cześć! Najnowsze spółki które warto kupić:</p>
    {table_html}
    <p>A tu wszystkie spółki spełniające zależności</p>
    {table2_html}
</body>
</html>
"""
msg.attach(MIMEText(html_body, "html"))

# 🔹 Wysyłanie e-maila
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    server.quit()
    print("✅ E-mail wysłany pomyślnie!")
except Exception as e:
    print(f"❌ Błąd wysyłania e-maila: {e}")
