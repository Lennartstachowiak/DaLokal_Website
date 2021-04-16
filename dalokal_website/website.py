import os

from flask import Flask, render_template, request, session, jsonify, redirect
""" For hashing the password """
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL

app = Flask(__name__)

conn = pymysql.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'My2418SQL5765',
    db = 'dalokalschema'
)

# These lines represent the db configuration required for Flask.
# app.config['MYSQL_DATABASE_HOST'] = '35.242.230.227'
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'My2418SQL5765'
# app.config['MYSQL_DATABASE_DB'] = 'dalokalschema'
# The next line ‘mysql = MySQL(app)’ creates an instance which will provide us the access.
mysql = MySQL()
mysql.init_app(app)

@app.route('/index', methods=['GET', 'POST'])
def index():
    # conn = mysql.connect()
    cursor =conn.cursor()
    # cursor.execute("SELECT * from user_table;")
    data = cursor.fetchall()
    return render_template('index.html', page_title='My Page', data=data)

@app.route('/')
def main():
    return render_template('main.html')

# Sign up page
@app.route('/sign-up', methods=['GET','POST'])
def sign_up():
    # If not POST than returns static page
    if request.method == 'POST':
        # Connect db
        conn = mysql.connect()
        cursor =conn.cursor()
        email = request.form.get('email')
        # Check if email already exists
        # Wanted to check with SELECT EXISTS(SELECT * F[...]) but this works better
        emailCheck = cursor.execute('SELECT * FROM user_basic_table WHERE email="{email}";'.format(email=email))
        if emailCheck == 1:
            return render_template('signup.html', flash_message='email')
        # hash the password for safty reasons
        psw = request.form.get('psw')
        psw_repeat = request.form.get('psw_repeat')
        # Checks if the psw's match each other
        if psw != psw_repeat:
            return render_template('signup.html', flash_message='psw')
        # Try to INSERT INTO the db
        psw = generate_password_hash(psw)
        cursor.execute('INSERT INTO user_basic_table (email, password) VALUES ("{email}","{psw}");'.format(email=email, psw=psw))
        # Commit changes to change the db
        cursor.execute('COMMIT;')
        return redirect('/sign-up/complete-sign-up')
    else:
        print('Not POST')
    return render_template('signup.html', flash_message="")

@app.route('/log-in', methods=['GET','POST'])
def log_in():
    return render_template('login.html')

@app.route('/sign-up/complete-sign-up', methods=['GET','POST'])
def complete_sign_up():
    return render_template('complete-sign-up.html')

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)

