import flask
from flask import flash, Flask, redirect, request, render_template, session
from flask_session import Session
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import hashlib

app = Flask(__name__)

# Session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# SQL
engine = create_engine('sqlite:///ttt_users.db', echo=True)
meta = MetaData()
users = Table(
    'first_table', meta,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('password', String),
)


@app.route('/')
def index():
    if not session.get('username'):
        return redirect('/login')
    else:
        return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password = hashlib.md5(password.encode()).hexdigest()
        s = users.select().where(users.c.username == username)
        conn = engine.connect()
        search_result = conn.execute(s)
        message = 'No such Username'
        for r in search_result:
            message = 'Wrong Password'
            if password == r[2]:
                session['username'] = request.form.get('username')
                message = None
                return redirect('/')
    return render_template('/login.html', message=message)


@app.route('/create_account', methods=['POST', 'GET'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        # check if username already exist
        s = users.select().where(users.c.username == username)
        conn = engine.connect()
        search_result = conn.execute(s)
        for r in search_result:
            message = 'username is taken'
            return render_template('create_account.html', message=message)
        password = request.form.get('password')
        password = hashlib.md5(password.encode()).hexdigest()
        ins = users.insert().values(username=username, password=password)
        conn = engine.connect()
        result = conn.execute(ins)
        session['username'] = request.form.get('username')
        return redirect('/')

    return render_template('create_account.html')


@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')


@app.route('/download')
def download_file():
    return flask.send_file('C:\\Users\\yaron\\Desktop\\PycharmProjects\\TTT_project_pyqt5\\website_with_users\\download_dir\\TTT.exe', as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
