from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

waiting_pool = []
pairs_log = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip().replace(" ", "")

    if not name or not phone:
        return jsonify({"message": "⚠️ Name and phone are required."}), 400

    if any(p["phone"] == phone for p in waiting_pool):
        return jsonify({"message": f"⚠️ {name}, you already joined."})

    waiting_pool.append({"name": name, "phone": phone})

    message = f"🎉 Hi {name}, you successfully joined the event!"

    if len(waiting_pool) >= 8:
        random.shuffle(waiting_pool)
        selected = waiting_pool[:8]
        del waiting_pool[:8]

        while len(selected) >= 2:
            a = selected.pop()
            b = selected.pop()
            pairs_log.append((a, b))

    return jsonify({"message": message})

@app.route("/admin")
def admin():
    return render_template(
        "admin.html",
        waiting=waiting_pool,
        pairs=pairs_log
    )

if __name__ == "__main__":
    app.run(debug=True)
