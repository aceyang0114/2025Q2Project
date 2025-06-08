from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

uploaded_cards = []

@app.route("/")
def index():
    return render_template("RFID.html")

@app.route("/main.html")
def main_page():
    return render_template("main.html")

@app.route("/offline.html")
def offline_page():
    return render_template("offline.html")

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "msg": "沒有資料"})
    for card in data:
        print(f"接收到巡檢資料：{card}")
        uploaded_cards.append(card)
    return jsonify({"success": True})

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
