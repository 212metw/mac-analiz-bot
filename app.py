import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    try:
        requests.post(
            BASE_URL + "/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5
        )
    except Exception as e:
        print("SEND ERROR:", e)


@app.route("/")
def home():
    return "Bot çalışıyor"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return "ok"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        text_lower = text.lower()

        # --- BASİT ANALİZ ---
        if "galatasaray" in text_lower and "fener" in text_lower:
            reply = "Derbi analizi: dengeli maç, KG var ihtimali orta-yüksek"

        elif "galatasaray" in text_lower:
            reply = "Galatasaray: ev sahibi avantajı + hücum gücü etkili"

        elif "fener" in text_lower:
            reply = "Fenerbahçe: tempolu oyun + gol üretimi yüksek"

        else:
            reply = "Takım yaz (örn: galatasaray fenerbahçe)"

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
