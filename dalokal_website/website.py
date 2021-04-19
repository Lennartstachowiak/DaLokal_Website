import os

from flask import Flask, render_template, request, session, jsonify, redirect
""" For hashing the password """
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
# from flaskext.mysql import MySQL

app = Flask(__name__)

# Connect db
def connect_to_database():
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    conn = pymysql.connect(
        user=db_user,
        password=db_password,
        unix_socket=unix_socket,
        db=db_name
    )
    cursor = conn.cursor()
    return cursor

# Close database connection
def close_database_connection():
    conn.close


# websites
@app.route('/index', methods=['GET', 'POST'])
def index():
    # cursor.execute("SELECT * from user_table;")
    data = cursor.fetchall()
    close_database_connection()
    return render_template('index.html', page_title='My Page', data=data)


@app.route('/')
def main():
    return render_template('main.html')

# Sign up page


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # If not POST than returns static page
    if request.method == 'POST':
        connect_to_database()
        email = request.form.get('email')
        # Check if email already exists
        # Wanted to check with SELECT EXISTS(SELECT * F[...]) but this works
        emailCheck = cursor.execute(
            'SELECT * FROM user_basic_table WHERE email="{email}";'.format(email=email))
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
        cursor.execute('INSERT INTO user_basic_table (email, password) VALUES ("{email}","{psw}");'.format(
            email=email, psw=psw))
        # Commit changes to change the db
        cursor.execute('COMMIT;')
        close_database_connection()
        return redirect('/sign-up/complete-sign-up')
    else:
        print('Not POST')
    return render_template('signup.html', flash_message="")


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    return render_template('login.html')


@app.route('/sign-up/complete-sign-up', methods=['GET', 'POST'])
def complete_sign_up():
    return render_template('complete-sign-up.html')


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
