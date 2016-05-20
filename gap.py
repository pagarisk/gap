#	imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing


#	configuration
app = Flask(__name__)
app.config.from_object('app_config')


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
    return 'Let\'s grow!'

@app.route('/list/')
def show_entries():
    cur = g.db_execute('select title, text from entries order by id desc')
    entries = [dict(title = row[0], text = row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries = entries)

@app.route('/add/', methods = ['POST'])
def add_entry():
    if not session.get('logged in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['tite'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login/')
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        if request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error = error)

@app.route('/logout/')
def logout():
    session.pop('logged in', None)
    flash('You were logged out')
    return redirect(url_for('show entries'))


if __name__ == '__main__':
    app.run()