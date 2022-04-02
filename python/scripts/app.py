print("Hello from Container!")
from flask import Flask, redirect, render_template, request, session
from helpers import login_required
app = Flask(__name__)

@app.route('/')
@login_required
def index():
    return 'Web App with Python Flask! And hello from Lev! From container!'

@app.route('/login', methods=['GET', 'POST'])
def login():
#    session.clear()

    if request.method == 'POST':
        return render_template('indev.html')
    else:
        return render_template('login.html')

app.run(host='0.0.0.0', port=5000)