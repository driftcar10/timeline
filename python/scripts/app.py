print("Hello from Container!")
from flask import Flask, redirect, render_template, request, session
from helpers import login_required, apology
from werkzeug.security import check_password_hash, generate_password_hash
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
        
        if not request.form.get("username"):
            return apology("must provide username", 403)

        
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        cur.execute("SELECT password_hash, id FROM users WHERE name = ?", (request.form.get("username"), ))
        password, user_id = cur.fetchone()
        
        print(password)
        print(user_id)

        if not password:
            return apology("invalid username and/or password", 403)

        if not check_password_hash(password, request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        session["user_id"] = user_id

        return redirect("/")
        #return render_template('indev.html')
    else:
        return render_template('login.html')

app.run(host='0.0.0.0', port=5000)