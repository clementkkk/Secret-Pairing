from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

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
        phone = "+233 " + phone.lstrip("0").replace(" ", "")

    # Prevent duplicates
    if any(p["phone"] == phone for p in waiting_pool):
        return jsonify({"message": f"⚠️ {name}, you have already joined. Please wait."})

    waiting_pool.append({"name": name, "phone": phone})

    # Congratulatory message
    message = f"🎉 Hi {name}, you successfully joined the Christmas Secret Pairing event!"

    # If at least 8 participants, pair them
    if len(waiting_pool) >= 8:
        random.shuffle(waiting_pool)
        selected_pool = waiting_pool[:8]
        waiting_pool[:8] = []  # remove them

        pairs = []
        while len(selected_pool) >= 2:
            p1 = selected_pool.pop()
            p2 = selected_pool.pop()
            pairs.append({p1["name"]: p2["name"], p2["name"]: p1["name"]})

        # For now, just print pairs in console
        print("New Pairs:")
        for pair in pairs:
            print(pair)

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
