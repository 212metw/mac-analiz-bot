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


# ---------------- TEAM ID BUL ----------------
def get_team_id(name):
    url = f"{API_HOST}/teams"
    headers = {"x-apisports-key": API_KEY}
    params = {"search": name}

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    try:
        return data["response"][0]["team"]["id"]
    except:
        return None


# ---------------- FIXTURE BUL ----------------
def get_fixture(team1_id, team2_id):
    url = f"{API_HOST}/fixtures"
    headers = {"x-apisports-key": API_KEY}

    params = {
        "h2h": f"{team1_id}-{team2_id}",
        "next": 10
    }

    r = requests.get(url, headers=headers, params=params)
    return r.json()


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return "ok"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "İki takım yaz: Galatasaray Fenerbahçe")
            return "ok"

        team1_name = parts[0]
        team2_name = parts[1]

        team1_id = get_team_id(team1_name)
        team2_id = get_team_id(team2_name)

        if not team1_id or not team2_id:
            send_message(chat_id, "Takımlar bulunamadı")
            return "ok"

        fixture = get_fixture(team1_id, team2_id)

        if fixture and fixture.get("response"):
            match = fixture["response"][0]

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]
            date = match["fixture"]["date"]

            reply = f"""
📊 MAÇ BULUNDU

🏟️ {home} vs {away}
🏆 {league}
📅 {date}
"""
        else:
            reply = "Maç bulunamadı (H2H yok)"

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


@app.route("/")
def home():
    return "Bot aktif"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
