from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允許跨來源請求，支援手機測試

# 模擬儲存用
uploaded_cards = []


@app.route("/")
def index():
    return render_template("RFID.html")


@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "msg": "沒有資料"})

    for card in data:
        print(f"接收到巡檢資料：{card}")
        uploaded_cards.append(card)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
