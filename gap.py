#	imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from flask_sqlalchemy import SQLAlchemy

#	configuration
app = Flask(__name__)
app.config.from_object('app_config')

#	SQLAlchemy init
db = SQLAlchemy(app)



#	db functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode = 'r') as f:
            db.cursor().executescript(f.read())
        db.commit


#	db connection handling
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


#	url routings
@app.route('/')
def home():
    cur = g.db.execute('select title, description, vector, status, impact, confidence, ease from tests order by id desc')
    tests = [dict(title = row[0], 
                    description = row[1], 
                    vector = row[2],
                    status = row[3],
                    impact = row[4],
                    confidence = row[5],
                    ease = row[6]) for row in cur.fetchall()]
    return render_template('show_tests.html', tests = tests)

@app.route('/add')
def add_form():
    return render_template("add_test.html")

@app.route('/add-test/', methods = ['POST'])
def add_test():
    if not session.get('logged in'):
        abort(401)
    g.db.execute('insert into tests (title, description, vector, status, impact, confidence, ease) values (?, ?, ?, ?, ?, ?, ?)',
                 [request.form['title'],
                  request.form['description'], 
                  request.form['vector'], 
                  request.form['status'], 
                  request.form['impact'], 
                  request.form['confidence'], 
                  request.form['ease']])
    g.db.commit()
    flash('New test was successfully created!')
    return redirect(url_for('show_entries'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['userName'] != app.config['USERNAME']:
            error = 'Invalid username'
        if request.form['userPassword'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
