import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
API_HOST = "https://v3.football.api-sports.io"


# ---------------- TELEGRAM ----------------
def send_message(chat_id, text):
    requests.post(
        BASE_URL + "/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10
    )


# ---------------- MATCH SEARCH ----------------
def search_fixture(query):
    url = f"{API_HOST}/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"search": query}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json()
    except Exception as e:
        print("API ERROR:", e)
        return None


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)

        if not data or "message" not in data:
            return "ok"

        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not chat_id:
            return "ok"

        result = search_fixture(text)

        if result and result.get("response"):
            match = result["response"][0]

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]

            reply = f"🏟️ {home} vs {away}\n🏆 {league}"
        else:
            reply = "Maç bulunamadı"

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        result = search_fixture(text)

        if result and result.get("response"):
            match = result["response"][0]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]
            date = match["fixture"]["date"]

            reply = f"""
📊 MAÇ BULUNDU

🏟️ {home} vs {away}
🏆 Lig: {league}
📅 Tarih: {date}

🔎 Veri başarıyla çekildi
"""
        else:
            reply = "Maç bulunamadı (API sonucu boş döndü)"

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


@app.route("/")
def home():
    return "Bot çalışıyor"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
