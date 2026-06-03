import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


# ---------------- TELEGRAM ----------------
def send_message(chat_id, text):
    try:
        requests.post(
            BASE_URL + "/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5
        )
    except:
        pass


# ---------------- ANALİZ MOTORU ----------------
def analyze_match():
    # Basit ama geniş model (sonradan geliştirilecek)
    home = 50
    draw = 25
    away = 25

    over25 = 60
    under25 = 40

    kg_yes = 58
    kg_no = 42

    x1 = home + draw
    x2 = away + draw
    twelve = home + away

    return {
        "1": home,
        "X": draw,
        "2": away,
        "over25": over25,
        "under25": under25,
        "kg_yes": kg_yes,
        "kg_no": kg_no,
        "x1": x1,
        "x2": x2,
        "12": twelve
    }


# ---------------- API (opsiyonel) ----------------
def get_api_data():
    if not API_KEY:
        return None

    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    try:
        r = requests.get(url, headers=headers, timeout=5)
        return r.json()
    except:
        return None


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "Mac Analiz Botu Aktif"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return "ok"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()

        analysis = analyze_match()
        api_data = get_api_data()

        reply = f"""
📊 MAÇ ANALİZ SİSTEMİ

🏠 1 (Ev): %{analysis['1']}
🤝 X: %{analysis['X']}
✈️ 2 (Dep): %{analysis['2']}

🔁 1X (Ev kaybetmez): %{analysis['x1']}
🔁 X2 (Dep kaybetmez): %{analysis['x2']}
🔥 12 (Beraberlik yok): %{analysis['12']}

⚽ 2.5 ÜST: %{analysis['over25']}
⚽ 2.5 ALT: %{analysis['under25']}

🥅 KG VAR: %{analysis['kg_yes']}
🥅 KG YOK: %{analysis['kg_no']}
"""

        # API çalışıyorsa küçük bilgi ekle
        if api_data:
            reply += "\n\n🟢 API bağlantısı aktif"
        else:
            reply += "\n\n🟡 API kullanılmıyor (statik model)"

        send_message(chat_id, reply)
        return "ok"

    except Exception as e:
        print("ERROR:", e)
        return "ok"


# ---------------- START ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
