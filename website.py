import os

from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)

# These lines represent the db configuration required for our Flask.
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Lennart2418'
app.config['MYSQL_DATABASE_DB'] = 'dalokalschema'
# The next line ‘mysql = MySQL(app)’ creates an instance which will provide us the access.
mysql = MySQL()
mysql.init_app(app)

@app.route('/index', methods=['GET', 'POST'])
def index():
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("SELECT * from user_table WHERE user_id = 1;")
    data = cursor.fetchall()
    return render_template('index.html', page_title='My Page', data=data)

@app.route('/')
def main():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)

