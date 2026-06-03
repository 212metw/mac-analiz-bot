import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    requests.post(BASE_URL + "/sendMessage", json={"chat_id": chat_id, "text": text})

def get_team_stats():
    api_key = FOOTBALL_API_KEY
    url = "https://api.football-data.org/v4/matches"
    headers = {
        "X-Auth-Token": api_key
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API çağrısı hatası: {e}")
        return None

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
        text = data["message"].get("text", "").lower()

        api_data = get_team_stats()

        if api_data:
            # Basit analiz, ilk maçı alalım
            match = api_data.get("matches", [])[0] if api_data.get("matches") else None
            if match:
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']
                reply = f"İlk maç: {home_team} vs {away_team} - API verisi çekildi."
            else:
                reply = "Maç verisi bulunamadı."
        else:
            reply = "API çalışmıyor ya da veri alınamadı."

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print(f"WEBHOOK HATASI: {e}")
        return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
