from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import pymssql

app = Flask(__name__)
socketio = SocketIO(app)

def get_connection():
    # 測試連線（你可以放在 app.py 最下方）
    try:
        conn = pymssql.connect(
            server='AIR-PC01\\FIRSTDBFROMACE',
            user='',
            password='mxicagb2024',
            database='Login_Page',
            charset='UTF-8',
        )
        print("✅ 連線成功")
        return conn
    except Exception as e:
        print("❌ 連線失敗：", e)

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM LoginINFO ORDER BY ID ASC")
    rows = cursor.fetchall()
    conn.close()
    return render_template("index.html", data=rows)

@socketio.on('submit_data')
def handle_submit(data):
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return  # 防呆，空值不處理

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO LoginINFO (Name, Password) VALUES (%s, %s)", (name, password))
    conn.commit()
    conn.close()
    emit('new_data', {'name': name}, broadcast=True)

@app.route('/clear', methods=['POST'])
def clear_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM LoginINFO")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, debug=True)
