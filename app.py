import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    requests.post(BASE_URL + "/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

@app.route("/")
def home():
    return "Bot çalışıyor"

@app.route(f"/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    text_lower = text.lower()

    if "galatasaray" in text_lower or "fenerbahçe" in text_lower:
        api_data = get_matches()

        if api_data:
            reply = "📊 Maç verisi çekildi. Basit analiz aktif."
        else:
            reply = "❌ Veri alınamadı (API kontrol et)"

    else:
        reply = "Takım adı yaz (örn: galatasaray / fenerbahçe)"

    send_message(chat_id, reply)

    return "ok"
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        text_lower = text.lower()

        if "galatasaray" in text_lower and "fener" in text_lower:
            reply = "Derbi: dengeli maç, gol var ihtimali yüksek"
        else:
            reply = "Takım isimlerini yaz (örnek: galatasaray fenerbahçe)"

        send_message(chat_id, reply)

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
