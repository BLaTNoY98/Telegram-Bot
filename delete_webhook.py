import requests

BOT_TOKEN = "8079107774:AAE5gujyjgvY89EShQJ7fP3gtf-QtVzdB6Q"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(url)
print(response.json())
