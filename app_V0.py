from flask import Flask, render_template, g, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import pymssql
import os

app = Flask(__name__)
socketio = SocketIO(app)

# 與資料庫連線
def get_connection():
    try:
        conn = pymssql.connect(
            server='AIR-PC01\\FIRSTDBFROMACE',
            user='sa',
            password='mxicagb2024',
            database='InsertDataDB',
            charset='UTF-8',
        )
        print("==========Successfully Connected to Database==========")
        return conn
    except Exception as e:
        print("==========Failed to Connected to Database==========", e)

# 連線後的第一個動作
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM InsertData;")
    rows = cursor.fetchall()
    conn.close()
    return render_template("index.html", data=rows)

@socketio.on('submit_data')
def handle_submit(data):
    text = data.get('text')  # 使用 text

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO InsertData (InsertDataValue) VALUES (%s)", (text,))
    conn.commit()
    conn.close()

    emit('new_data', {'text': text}, broadcast=True)

@app.route('/clear', methods=['POST'])
def clear_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM InsertData")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, debug=True)