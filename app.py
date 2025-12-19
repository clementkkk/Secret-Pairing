from flask import Flask, request, jsonify, send_from_directory
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random
import os

app = Flask(__name__)

# =============================
# 🔐 TWILIO CONFIG (EDIT THESE)
# =============================
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Sandbox number

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

waiting_pool = []
pairs_log = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/admin")
def admin():
    return send_from_directory(BASE_DIR, "admin.html")

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip().replace(" ", "")
    gender = data.get("gender", "").lower()

    if not name or not phone or gender not in ["male", "female"]:
        return jsonify({
            "success": False,
            "message": "⚠️ Please fill all fields correctly."
        }), 400

    # Normalize Ghana numbers
    if phone.startswith("0"):
        phone = "+233" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+233" + phone

    if any(p["phone"] == phone for p in waiting_pool):
        return jsonify({
            "success": False,
            "message": f"⚠️ {name}, you have already joined."
        })

    waiting_pool.append({
        "name": name,
        "phone": phone,
        "gender": gender
    })

    # Send confirmation WhatsApp
    try:
        client.messages.create(
            body=f"🎄 Hi {name}! You have successfully joined the Christmas Secret Pairing. Please wait for pairing.",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone}"
        )
    except TwilioRestException as e:
        print("WhatsApp send error:", e.msg)

    # Pairing when 8 join
    if len(waiting_pool) >= 8:
        selected = waiting_pool[:8]
        del waiting_pool[:8]

        males = [p for p in selected if p["gender"] == "male"]
        females = [p for p in selected if p["gender"] == "female"]

        random.shuffle(males)
        random.shuffle(females)

        pairs = []

        while males and females:
            pairs.append((males.pop(), females.pop()))

        leftovers = males + females
        random.shuffle(leftovers)

        while len(leftovers) >= 2:
            pairs.append((leftovers.pop(), leftovers.pop()))

        # Send pairing messages
        for a, b in pairs:
            pairs_log.append((a, b))

            try:
                client.messages.create(
                    body=f"🎁 Hi {a['name']}! Your secret pair is *{b['name']}*. Keep it secret 🤫",
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{a['phone']}"
                )
                client.messages.create(
                    body=f"🎁 Hi {b['name']}! Your secret pair is *{a['name']}*. Keep it secret 🤫",
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{b['phone']}"
                )
            except TwilioRestException as e:
                print("Pairing WhatsApp error:", e.msg)

    return jsonify({
        "success": True,
        "message": f"🎉 Congratulations {name}! You have successfully joined."
    })

@app.route("/data")
def data():
    return jsonify({
        "waiting": waiting_pool,
        "pairs": pairs_log
    })

if __name__ == "__main__":
    app.run(debug=True)
