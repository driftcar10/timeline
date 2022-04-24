from flask import redirect, session, render_template
from functools import wraps
import datetime

def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def is_date_in_period(event_date, current_date, period):
    print(event_date, current_date, period)
    if period == "day":
        return event_date == current_date

    if period == "month":
        return event_date.year == current_date.year and event_date.month == current_date.month

    else:
        return event_date.year == current_date.year