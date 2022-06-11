from flask import redirect, session, render_template
from functools import wraps
import datetime
import logging

logger = logging.getLogger(__name__)


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
    logger.debug(f"{event_date}, {current_date}, {period}")
    if period == "day":
        return event_date == current_date

    if period == "month":
        return event_date.year == current_date.year and event_date.month == current_date.month

    else:
        return event_date.year == current_date.year


def fill_timeline(current_date, end_date, delta, group_by, current_period, data):
    events = []
    while current_date <= end_date:

        next_date = current_date + delta
        logger.debug(f" Current date {current_date}, next_date {next_date}")
        while data and is_date_in_period(data[-1][1], current_date, group_by):
            event_id = data[-1][0]
            event_descr = data[-1][2]
            current_period["events"].append(
                {"id": event_id, "descr": event_descr})
            logger.debug(f" adding event {data[-1]}, to current period {current_period}")
            data.pop()
        logger.debug("Finished period")
        if group_by == 'day':
            logger.debug(f"current {current_date.day} next {next_date.day}")
            if current_date.day != next_date.day:

                events.append(current_period)
                current_period = {"date": next_date.strftime(
                    "%d/%m/%Y"), "events": []}
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
    if current_period["events"]: events.append(current_period)
    return events
