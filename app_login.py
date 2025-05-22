# from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit
import pymssql
import os

USERNAME = 'sa'
PASSWORD = 'mxicagb2024'

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用來啟用 session
socketio = SocketIO(app)

# 假設帳號密碼為 admin / 1234
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '1234':
            session['username'] = username
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error='帳號或密碼錯誤')
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'username' in session:
        return render_template('menu.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
