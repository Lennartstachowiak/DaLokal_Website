import os

from flask import Blueprint, render_template, request, session, jsonify, redirect
""" For hashing the password """
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

""" That connection is for GCloud """
# Connection to database set up
# db_user = os.environ.get('CLOUD_SQL_USERNAME')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
# unix_socket = '/cloudsql/{}'.format(db_connection_name)
# conn = pymysql.connect(
#     user=db_user,
#     password=db_password,
#     unix_socket=unix_socket,
#     db=db_name
# )
# cursor = conn.cursor()

# Database connection for local connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='My2418SQL5765',
    database='dalokalschema'
)
cursor = conn.cursor()

# Sign up page


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If not POST than returns static page
    if request.method == 'POST':
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
        conn.close
        return redirect('/sign-up/complete-sign-up')
    else:
        print('Not POST')
    return render_template('signup.html', flash_message="")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If not post than just return html
    if request.method == 'POST':
        email = request.form.get('email')
        psw = request.form.get('psw')
        remember = True if request.form.get('remember') else False

        cursor.execute('SELECT email FROM user_basic_table WHERE email="{email}";'.format(email=email))
        email_check = cursor.fetchone()
        if not email_check: 
            print('Wrong')
            return render_template('login.html', flash_message='wrong')
        else:
            cursor.execute('SELECT password FROM user_basic_table WHERE email="{email}";'.format(email=email))
            psw_check = cursor.fetchone()[0]
            if not check_password_hash(psw_check,psw):
                return render_template('login.html', flash_message='wrong')
            else:
                """ Work with session and go back to homepage """
                print('True')
    return render_template('login.html', flash_message='')


@auth.route('/sign-up/complete-sign-up', methods=['GET', 'POST'])
def complete_sign_up():
    return render_template('complete-sign-up.html')
