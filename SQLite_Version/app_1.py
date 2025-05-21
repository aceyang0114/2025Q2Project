from flask import Flask, render_template, g, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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

@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM messages ORDER BY created_at ASC")
    messages = [row[0] for row in cursor.fetchall()]
    return render_template("index.html", messages=messages)

@socketio.on('submit_data')
def handle_submit(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (content) VALUES (?)", (data['text'],))
    conn.commit()
    emit('new_data', data, broadcast=True)

@app.route('/clear', methods=['POST'])
def clear_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM messages')  # 資料表名稱要跟資料庫一致
    conn.commit()
    return redirect(url_for('index'))

@socketio.on('submit_data')
def handle_submit(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (content) VALUES (?)", (data['text'],))
    conn.commit()
    emit('new_data', data, broadcast=True)

if __name__ == '__main__':
    init_db()
    # socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    app.run(host='0.0.0.0', port=5000)