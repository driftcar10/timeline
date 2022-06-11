from crypt import methods
import os
from pydoc import describe
import mariadb
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from flask_session import Session
from helpers import login_required, apology, fill_timeline
from flask import Flask, current_app, redirect, render_template, request, session
from flask_bootstrap import Bootstrap
import logging

logging.basicConfig(level=logging.DEBUG)

print("Hello from Container!")

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Bootstrap(app)

user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DATABASE')

def get_db_conn():
    if not hasattr(current_app,'db_conn') or not current_app.db_conn:
        current_app.db_conn =  mariadb.connect(
            host="db",
            port=3306,
            user=user,
            password=password,
            database=database
        )
    return current_app.db_conn

@app.teardown_appcontext
def close_db_conn(error):
    if hasattr(current_app, 'db_conn'):
        if current_app.db_conn is not None:
            current_app.db_conn.close()
        current_app.db_conn = None


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    cur = get_db_conn().cursor()
    cur.execute("SELECT MIN(date) FROM events WHERE user_id = ?",
                (session['user_id'], ))
    print(cur.rowcount, session['user_id'])
    min_date = cur.fetchone()[0]
    print(min_date)
    events = []
    if min_date:
        cur.execute(
            "SELECT MAX(date) FROM events WHERE user_id = ?", (session['user_id'], ))
        max_date = cur.fetchone()[0]
        print('am i working')
        # iterating over dates

        #importing data from database
        cur.execute(
            "SELECT id, date, description FROM events WHERE user_id = ? ORDER BY date",
            (session['user_id'], )
        )
        data = [d for d in cur]
        data.reverse()

        #setting up date
        current_date = min_date
        end_date = max_date
        delta = datetime.timedelta(days=1)

        #reading the dropdown

        group_by = "month" if request.method == "GET" else request.form.get("group_by")

        current_period = {"date": current_date.strftime("%d/%m/%Y") if group_by == "day" else current_date.strftime(
            "%Y/%m") if group_by == "month" else current_date.strftime("%Y"), "events": []}

        events = fill_timeline(current_date, end_date, delta, group_by, current_period, data)

    # print("going to render!")
    return render_template('index.html', T_events=events)
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    cur = get_db_conn().cursor()
    if request.method == 'POST':

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        cur.execute("SELECT password_hash, id FROM users WHERE name = ?",
                    (request.form.get("username"), ))
        user_row = cur.fetchone()
        if not user_row:
            return apology("invalid username and/or password")
        
        password, user_id = user_row
        print(password)
        print(user_id)

        if not password:
            return apology("invalid username and/or password", 403)

        if not check_password_hash(password, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user_id

        return redirect("/")
        # return render_template('indev.html')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cur = get_db_conn().cursor()
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
            cur.execute("INSERT INTO users (name, password_hash, mail) VALUES (?, ?, ?)",
                        (request.form.get("username"), password_hash, request.form.get("email")))
            get_db_conn().commit()
        except ValueError:
            return apology(f"There's another guy with the same name: {request.form.get('username')}", 400)
        return redirect("/login")
    else:
        return render_template('register.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    cur = get_db_conn().cursor()
    if request.method == 'POST':
        if not request.form.get("date"):
            return apology("must provide date", 400)

        elif not request.form.get("description"):
            return apology("must provide description", 400)
        print(request.form.get("date"))
        date = datetime.datetime.fromisoformat(request.form.get("date"))
        event_id = request.form.get("event_id")
        if event_id:
            cur.execute("UPDATE events SET date = ?, description = ? WHERE id = ?",
                        (date,
                        request.form.get("description"),
                        event_id
                        ))
            get_db_conn().commit()
        else:
            cur.execute("INSERT INTO events (date, description, user_id) VALUES (?, ?, ?)",
                        (date,
                        request.form.get("description"),
                        session['user_id']))
            get_db_conn().commit()
        return redirect('/')
    else:
        event_id = request.args.get("eventid")
        print(event_id)
        if event_id:
            print("have id")
            cur.execute("SELECT date, description FROM events WHERE id = ?", (event_id, ))
            event = cur.fetchone()
            if event:
                event_t = {"date":event[0].strftime("%Y-%m-%d"), "descr":event[1], "event_id":event_id}
                return render_template("add.html", event_t = event_t)
            else:
                return apology("No such event", 404)
            
        return render_template("add.html")


@app.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html')

@app.route('/indev', methods=['GET'])
def indev():
    return render_template('indev.html')

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    cur = get_db_conn().cursor()
    if request.method == "POST":
        if request.form.get('no') == 'No':
            return redirect("/")
        else:
            event_id = request.form.get("event_id")
            if event_id:
                cur.execute("DELETE FROM events WHERE id = ?",
                (event_id, )
                )
                get_db_conn().commit()
                print("deleted")
                return redirect("/")
    else:
        event_id = request.args.get("eventid")
        print(event_id)
        if event_id:
            print("have delete id")
            id = event_id
            return render_template('delete.html', id = id)
        return apology("No such event", 404)

app.run(host='0.0.0.0', port=5000)
