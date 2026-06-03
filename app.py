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


# ---------------- 1. FIXTURE SEARCH ----------------
def search_by_text(text):
    try:
        url = f"{API_HOST}/fixtures"
        headers = {"x-apisports-key": API_KEY}
        params = {"search": text, "next": 10}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json()
    except:
        return None


# ---------------- 2. NEXT MATCHES ----------------
def get_next_matches():
    try:
        url = f"{API_HOST}/fixtures"
        headers = {"x-apisports-key": API_KEY}
        params = {"next": 10}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json()
    except:
        return None


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").lower()

    result = search_by_text(text)

    match = None

    # 1. TEXT SEARCH DENEME
    if result and result.get("response"):
        match = result["response"][0]

    # 2. YOKSA NEXT MATCHES DENEME
    if not match:
        result2 = get_next_matches()

        if result2 and result2.get("response"):
            for m in result2["response"]:
                home = m["teams"]["home"]["name"].lower()
                away = m["teams"]["away"]["name"].lower()

                if text in home or text in away:
                    match = m
                    break

    # ---------------- RESPONSE ----------------
    if match:
        reply = (
            "📊 MAÇ BULUNDU\n\n"
            f"🏟️ {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n"
            f"🏆 {match['league']['name']}\n"
            f"📅 {match['fixture']['date']}"
        )
    else:
        reply = "Maç bulunamadı (API eşleşmedi)"

    send_message(chat_id, reply)
    return "ok"


@app.route("/")
def home():
    return "Bot çalışıyor"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
