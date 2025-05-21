from flask import Flask, render_template, g, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import pymssql
import os

USERNAME = 'sa'
PASSWORD = 'mxicagb2024'

app = Flask(__name__)
socketio = SocketIO(app)

# SQL Server Express 連線，進行資料庫互動
def get_connection():
    return pymssql.connect(
        server='AIR-PC01\\FIRSTDBFROMACE',
        user=USERNAME,
        password=PASSWORD,  # 同上
        database='InsertDataDB',
        charset='UTF-8'
    )

# 首頁 - 顯示所有歷史資料，頁面刷新時也可使用
@app.route('/')
def index():
    # 與資料庫連線
    conn = get_connection()
    # 寫出 SQL 指令
    cursor = conn.cursor()
    # 搜尋指定資料表的指定內容
    cursor.execute("SELECT InsertDataValue FROM InsertData;")
    # 取得回傳資料
    rows = cursor.fetchall()
    # print('===========================================')
    # print(rows)
    # 中斷連線
    conn.close()

    # 只傳回資料
    messages = [row[0] for row in rows]
    return render_template("index.html", messages=messages)

# Socket.IO 處理資料送出
@socketio.on('submit_data')
def handle_submit(data):
    text = data.get('text')

    if not text:
        return

    # 與資料庫連線
    conn = get_connection()
    # 寫出 SQL 指令
    cursor = conn.cursor()
    # 插入輸入資料到指定資料表的指定欄位
    cursor.execute("INSERT INTO InsertData (InsertDataValue) VALUES (%s);", (text,))
    # 資料上傳
    conn.commit()
    # 中斷連線
    conn.close()

    # 廣播新資料給所有使用者，同步頁面更新
    emit('new_data', {'text': text}, broadcast=True)

# 清除資料
@app.route('/clear', methods=['POST'])
def clear_data():
    # 與資料庫連線
    conn = get_connection()
    # 寫出 SQL 指令
    cursor = conn.cursor()
    # 刪除指定資料表所有資料
    cursor.execute("DELETE FROM InsertData;")
    # 資料上傳
    conn.commit()
    # 中斷連線
    conn.close()

    # 廣播新資料給所有使用者，同步頁面更新
    socketio.emit('clear_data')

    return redirect(url_for('index'))

# 登入功能（接收帳密並返回帳號）
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    return jsonify({'success': True, 'username': username})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
