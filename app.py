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


# ---------------- TEAM ID BUL ----------------
def get_team_id(name):
    try:
        url = f"{API_HOST}/teams"
        headers = {"x-apisports-key": API_KEY}
        params = {"search": name}

        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()

        return data["response"][0]["team"]["id"]
    except:
        return None


# ---------------- H2H FIXTURE ----------------
def get_h2h(team1_id, team2_id):
    try:
        url = f"{API_HOST}/fixtures"
        headers = {"x-apisports-key": API_KEY}
        params = {"h2h": f"{team1_id}-{team2_id}", "next": 10}

        r = requests.get(url, headers=headers, timeout=10)
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

    parts = text.split()

    if len(parts) < 2:
        send_message(chat_id, "İki takım yaz: Galatasaray Fenerbahçe")
        return "ok"

    team1 = parts[0]
    team2 = parts[1]

    team1_id = get_team_id(team1)
    team2_id = get_team_id(team2)

    if not team1_id or not team2_id:
        send_message(chat_id, "Takım ID bulunamadı")
        return "ok"

    result = get_h2h(team1_id, team2_id)

    try:
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
            reply = "Maç bulunamadı (H2H veri yok)"
    except:
        reply = "Veri işlenemedi"

    send_message(chat_id, reply)
    return "ok"


@app.route("/")
def home():
    return "Bot aktif"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
