from crypt import methods
import os
from pydoc import describe
import mariadb
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from flask_session import Session
from helpers import login_required, apology, is_date_in_period
from flask import Flask, redirect, render_template, request, session
print("Hello from Container!")

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DATABASE')

conn = mariadb.connect(
    host="db",
    port=3306,
    user=user,
    password=password,
    database=database
)

cur = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    #if request.method == 'POST':
    cur.execute("SELECT MIN(date) FROM events WHERE user_id = ?",
                (session['user_id'], ))
    print(cur.rowcount, session['user_id'])
    min_date = cur.fetchone()[0]
    print(min_date)
    events = []
    if min_date:
        #min_date = min_date[0]
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

        while current_date <= end_date:

            next_date = current_date + delta

            while data and is_date_in_period(data[-1][1], current_date, group_by):
                event_id = data[-1][0]
                event_descr = data[-1][2]
                current_period["events"].append({"id":event_id,"descr":event_descr})
                data.pop()

            if group_by == 'day':
                if current_date.day < next_date.day:

                    events.append(current_period)
                    current_period = {"date": next_date.strftime("%d/%m/%Y"), "events": []}
                    print("new day")

            if group_by == 'month':
                if current_date.month < next_date.month:

                    events.append(current_period)
                    current_period = {
                        "date": next_date.strftime("%Y/%m"), "events": []}
                    print("new month")

            if group_by == 'year':
                if current_date.year < next_date.year:

                    events.append(current_period)
                    current_period = {
                        "date": next_date.strftime("%Y"), "events": []}
                    print("new year")

            current_date += delta
        events.append(current_period)

    return render_template('index.html', T_events=events)
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        cur.execute("SELECT password_hash, id FROM users WHERE name = ?",
                    (request.form.get("username"), ))
        password, user_id = cur.fetchone()

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
            conn.commit()
        except ValueError:
            return apology(f"There's another guy with the same name: {request.form.get('username')}", 400)
        return redirect("/login")
    else:
        return render_template('register.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
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
            conn.commit()
        else:
            cur.execute("INSERT INTO events (date, description, user_id) VALUES (?, ?, ?)",
                        (date,
                        request.form.get("description"),
                        session['user_id']))
            conn.commit()
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


app.run(host='0.0.0.0', port=5000)
