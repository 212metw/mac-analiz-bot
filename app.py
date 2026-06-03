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
    try:
        requests.post(
            BASE_URL + "/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except:
        pass


# ---------------- FIXTURE SEARCH ----------------
def search_matches(text):
    url = f"{API_HOST}/fixtures"
    headers = {"x-apisports-key": API_KEY}

    params = {
        "search": text,
        "next": 10
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json()
    except:
        return None


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)

        if not data or "message" not in data:
            return "ok"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        result = search_matches(text)

        if result and result.get("response"):
            match = result["response"][0]

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]
            date = match["fixture"]["date"]

            reply = (
                "📊 MAÇ BULUNDU\n\n"
                f"🏟️ {home} vs {away}\n"
                f"🏆 {league}\n"
                f"📅 {date}"
            )
        else:
            reply = "Maç bulunamadı. Lütfen takım adını doğru yaz."

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
