from flask import Flask, render_template, g, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import os

# 建立 Flask 和資料庫
app = Flask(__name__)
socketio = SocketIO(app)
DATABASE = 'database.db'

# 取得資料庫資料
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# 連線斷線
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 初始化資料庫
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ 已建立資料庫")

# 列出資料庫所有資料
@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM messages ORDER BY created_at ASC")
    messages = [row[0] for row in cursor.fetchall()]
    return render_template("index.html", messages=messages)

# 前端資料寫入資料庫
@socketio.on('submit_data')
def handle_submit(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (content) VALUES (?)", (data['text'],))
    conn.commit()
    emit('new_data', data, broadcast=True)

# 清除資料庫資料
@app.route('/clear', methods=['POST'])
def clear_data():
    conn = sqlite3.connect('database.db')  # 換成你的資料庫檔名
    cursor = conn.cursor()
    cursor.execute('DELETE FROM messages')  # 換成你的資料表名稱
    conn.commit()
    conn.close()

    socketio.emit('new_data', {'text': '[系統訊息] 所有資料已被清除'})
    return redirect(url_for('index'))  # 清除後跳回首頁（或你要導去的頁面）

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000)
