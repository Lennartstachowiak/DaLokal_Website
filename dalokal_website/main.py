import os

import logging
import pymysql
from flask import Blueprint, render_template, request, session, jsonify, redirect
""" For hashing the password """
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

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


@main.route('/')
def index():
    if 'userId' in session:
        loggedIn = True
        return render_template('index.html', loggedIn=loggedIn)
    return render_template('index.html')


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    # check if session cookie exist, if not returns to login
    if 'userId' and 'psw' in session:
        userId = session['userId']
        # check if session cookie is using the right data
        psw = session['psw']
        cursor.execute(
            'SELECT password FROM user_basic_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw == psw_check:
            # Chech if user completed his sign up infos
            cursor.execute(
                'SELECT EXISTS(SELECT * from user_info_table WHERE user_id="{userId}");'.format(userId=userId))
            info_check = cursor.fetchone()[0]
            if info_check != 1:
                return redirect('/sign-up/complete-sign-up')

            # Show users data
            cursor.execute(
                'SELECT * FROM user_info_table WHERE user_id="{userId}";'.format(userId=userId))
            userInfo = cursor.fetchone()
            farmname = userInfo[1]
            firstname = userInfo[2]
            lastname = userInfo[3]
            return render_template('profile.html', page_title='My Page', farmname=farmname, firstname=firstname, lastname=lastname)
    else:
        return redirect('/login')

# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, debug=True)
