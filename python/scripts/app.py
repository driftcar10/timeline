print("Hello from Container!")
from flask import Flask, redirect, render_template, request, session
from helpers import login_required
import mariadb
import os
app = Flask(__name__)

user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DATABASE')

conn = mariadb.connect(
        host = "db",
        port = 3306,
        user = user,
        password = password,
        database = database
    )

cur = conn.cursor()

@app.route('/')
@login_required
def index():
    return 'Web App with Python Flask! And hello from Lev! From container!'

@app.route('/login', methods=['GET', 'POST'])
def login():
#    session.clear()

    if request.method == 'POST':
        cur.execute("SELECT * FROM users")
        for user in cur:
            print(user)
        return render_template('indev.html')
    else:
        return render_template('login.html')

app.run(host='0.0.0.0', port=5000)