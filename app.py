import os
import requests
import math
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("FOOTBALL_API_KEY")

TG = f"https://api.telegram.org/bot{TOKEN}"
API = "https://v3.football.api-sports.io"
headers = {"x-apisports-key": API_KEY}


# ---------------- TELEGRAM ----------------
def send(chat_id, text):
    try:
        requests.post(TG + "/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        }, timeout=10)
    except:
        pass


# ---------------- FIXTURES ----------------
def get_fixtures():
    r = requests.get(API + "/fixtures",
                     headers=headers,
                     params={"next": 20},
                     timeout=10)
    return r.json()


# ---------------- LAST MATCHES ----------------
def last_matches(team_id):
    r = requests.get(API + "/fixtures",
                     headers=headers,
                     params={"team": team_id, "last": 8},
                     timeout=10)
    return r.json().get("response", [])


# ---------------- BASIC STATS ----------------
def stats(matches, team_id):
    w = d = l = gf = ga = 0

    for m in matches:
        home = m["teams"]["home"]["id"]
        hg = m["goals"]["home"]
        ag = m["goals"]["away"]

        if home == team_id:
            gf += hg
            ga += ag
            if hg > ag:
                w += 1
            elif hg == ag:
                d += 1
            else:
                l += 1
        else:
            gf += ag
            ga += hg
            if ag > hg:
                w += 1
            elif hg == ag:
                d += 1
            else:
                l += 1

    total = len(matches) or 1

    return {
        "w": w,
        "d": d,
        "l": l,
        "gf": gf / total,
        "ga": ga / total
    }


# ---------------- ELO ----------------
def elo(matches, team_id):
    rating = 1500

    for m in matches:
        home = m["teams"]["home"]["id"]
        hg = m["goals"]["home"]
        ag = m["goals"]["away"]

        if hg == ag:
            rating += 1
        elif (home == team_id and hg > ag) or (home != team_id and ag > hg):
            rating += 4
        else:
            rating -= 4

    return rating


# ---------------- POISSON ----------------
def poisson(avg, goals):
    return (math.exp(-avg) * (avg ** goals)) / math.factorial(goals)


def goal_probs(avg):
    return [poisson(avg, i) for i in range(6)]


# ---------------- MODEL ----------------
def predict(teamA, teamB, statsA, statsB, eloA, eloB):

    atkA = statsA["gf"]
    defA = statsA["ga"]
    atkB = statsB["gf"]
    defB = statsB["ga"]

    expA = (atkA + defB) / 2
    expB = (atkB + defA) / 2

    elo_diff = (eloA - eloB) / 400

    expA += elo_diff
    expB -= elo_diff

    A_probs = goal_probs(expA)
    B_probs = goal_probs(expB)

    home_win = draw = away_win = 0
    btts = over25 = 0

    for i in range(6):
        for j in range(6):
            p = A_probs[i] * B_probs[j]

            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p

            if i > 0 and j > 0:
                btts += p

            if i + j >= 3:
                over25 += p

    return {
        "home": home_win * 100,
        "draw": draw * 100,
        "away": away_win * 100,
        "btts": btts * 100,
        "over25": over25 * 100,
        "scoreA": round(expA),
        "scoreB": round(expB)
    }


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    chat = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").lower()

    fixtures = get_fixtures()

    match = None

    for m in fixtures["response"]:
        home = m["teams"]["home"]["name"].lower()
        away = m["teams"]["away"]["name"].lower()

        if text in home or text in away:
            match = m
            break

    if not match:
        send(chat, "Maç bulunamadı")
        return "ok"

    home = match["teams"]["home"]
    away = match["teams"]["away"]

    A_last = last_matches(home["id"])
    B_last = last_matches(away["id"])

    A_stats = stats(A_last, home["id"])
    B_stats = stats(B_last, away["id"])

    eloA = elo(A_last, home["id"])
    eloB = elo(B_last, away["id"])

    p = predict(home, away, A_stats, B_stats, eloA, eloB)

    msg = f"""
📊 ADVANCED ANALİZ BOT

⚽ {home['name']} vs {away['name']}
🏆 {match['league']['name']}

📈 FORM
{A_stats['w']}G {A_stats['d']}B {A_stats['l']}M vs {B_stats['w']}G {B_stats['d']}B {B_stats['l']}M

🧠 ELO
{int(eloA)} vs {int(eloB)}

📊 OLASILIK
🏠 Ev: %{round(p['home'])}
🤝 Beraberlik: %{round(p['draw'])}
✈️ Deplasman: %{round(p['away'])}

🥅 SKOR TAHMİNİ
{home['name']} {p['scoreA']} - {p['scoreB']} {away['name']}

📉 MARKETLER
KG VAR: %{round(p['btts'])}
2.5 ÜST: %{round(p['over25'])}

🎯 VALUE ANALİZ
En güçlü taraf: {'EV' if p['home'] > 50 else 'DEP'}
"""

    send(chat, msg)
    return "ok"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return "ADVANCED BOT ACTIVE"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
