print("Hello from Container!")
from flask import Flask, redirect, render_template, request, session
from helpers import login_required, apology
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import mariadb
import os
import datetime
app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        return render_template('indev.html')
    else:
        cur.execute("SELECT date, description FROM events WHERE user_id = ? ORDER BY date", (session['user_id'], ))
        events = []
        for row in cur:
            event = {}
            date, description = row
            event['date'] = date
            event['description'] = description
            events.append(event)
        
        return render_template("index.html", T_events=events)
#    return 'Web App with Python Flask! And hello from Lev! From container!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not request.form.get("username"):
            return apology("must provide username", 400)

        if not request.form.get("email"):
            return apology("must provide email", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)
        password_hash = generate_password_hash(request.form.get("password"))
        try:
            print(123)
            cur.execute("INSERT INTO users (name, password_hash, mail) VALUES (?, ?, ?)", (request.form.get("username"), password_hash, request.form.get("email")))
            conn.commit()
        except ValueError:
            return apology(f"There's another guy with the same name: {request.form.get('username')}", 400)
        return redirect("/login")
    else:
        return render_template('register.html')

    
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method =='POST':
        if not request.form.get("date"):
            return apology("must provide date", 400)
        
        elif not request.form.get("description"):
            return apology("must provide description", 400)
        print(request.form.get("date"))
        date = datetime.datetime.fromisoformat(request.form.get("date"))
        cur.execute("INSERT INTO events (date, description, user_id) VALUES (?, ?, ?)", 
            (request.form.get("date"),  
            request.form.get("description"), 
            session['user_id']))
        conn.commit()
        return redirect('/')
    else:
        return render_template("add.html")

@app.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html')

app.run(host='0.0.0.0', port=5000)