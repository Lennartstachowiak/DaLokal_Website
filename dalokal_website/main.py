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
    return render_template('index.html')


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    # cursor.execute("SELECT * from user_table;")
    return render_template('profile.html', page_title='My Page')

# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, debug=True)
