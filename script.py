import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 🔹 Tworzenie przykładowej tabeli
data = {
    "Imię": ["Jan", "Anna", "Piotr"],
    "Wiek": [25, 30, 22],
    "Miasto": ["Warszawa", "Kraków", "Gdańsk"]
}
df = pd.DataFrame(data)

# 🔹 Konwersja do HTML
table_html = df.to_html(index=False)

# 🔹 Ustawienia e-maila
SMTP_SERVER = "smtp.gmail.com"  # Dla Gmaila
SMTP_PORT = 587
EMAIL_SENDER = "twojemail@gmail.com"  # <-- Twój e-mail
EMAIL_PASSWORD = "twoje_haslo"  # <-- Wygeneruj hasło aplikacji!
EMAIL_RECEIVER = "odbiorca@example.com"

# 🔹 Tworzenie wiadomości e-mail
msg = MIMEMultipart()
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER
msg["Subject"] = "Automatyczna tabela z Python"

html_body = f"""
<html>
<body>
    <p>Cześć! Oto Twoja automatyczna tabela:</p>
    {table_html}
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
