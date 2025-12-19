from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# Twilio Credentials (replace with your own)
TWILIO_SID = 'YOUR_TWILIO_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Twilio sandbox WhatsApp
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

waiting_pool = []

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    if not data:
        return jsonify({"message": "⚠️ Invalid request. JSON expected."}), 400

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"message": "⚠️ Name and phone are required."}), 400

    # Auto format phone to +233
    if not phone.startswith("+233"):
        phone = "+233" + phone.lstrip("0").replace(" ", "")

    # Prevent duplicate
    if any(p["phone"] == phone for p in waiting_pool):
        return jsonify({"message": f"⚠️ {name}, you have already joined. Please wait."})

    waiting_pool.append({"name": name, "phone": phone})
    message = f"🎉 Hi {name}, you successfully joined the Christmas Secret Pairing event!"

    # Only pair when 8 participants are ready
    if len(waiting_pool) >= 8:
        random.shuffle(waiting_pool)
        selected_pool = waiting_pool[:8]
        waiting_pool[:8] = []  # Remove them from pool

        pairs = []
        while len(selected_pool) >= 2:
            p1 = selected_pool.pop()
            p2 = selected_pool.pop()
            pairs.append((p1, p2))

        # Send WhatsApp messages
        for p1, p2 in pairs:
            msg1 = f"🎁 Hi {p1['name']}, your secret pairing is {p2['name']}!"
            msg2 = f"🎁 Hi {p2['name']}, your secret pairing is {p1['name']}!"
            try:
                client.messages.create(
                    body=msg1,
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{p1['phone']}"
                )
                client.messages.create(
                    body=msg2,
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{p2['phone']}"
                )
            except Exception as e:
                print(f"Error sending WhatsApp: {e}")

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
