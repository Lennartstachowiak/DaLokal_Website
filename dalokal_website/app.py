import os

import logging
import pymysql
from flask import Blueprint, render_template, request, session, jsonify, redirect
""" For hashing the password """
from werkzeug.security import generate_password_hash, check_password_hash

app = Blueprint('app', __name__)

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


def connectDatabase():
    cursor = pymysql.connect(
        host='localhost',
        user='root',
        password='My2418SQL5765',
        database='dalokalschema'
    ).cursor()
    # cursor = conn.cursor()
    return cursor


def checkCompleteUser(userId):
    cursor = connectDatabase()
    cursor.execute(
        'SELECT firstname FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
    checkUser = cursor.fetchone()[0]
    cursor.execute(
        'SELECT EXISTS(SELECT * FROM farm_table WHERE user_id="{userId}");'.format(userId=userId))
    checkFarm = cursor.fetchone()[0]
    if checkUser == None:
        return redirect('/signup/complete-signup')
    if checkFarm != 1:
        return redirect('/signup/complete-signup/farm-information')
    return True


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'userId' not in session:
        return render_template('index.html')
    else:
        userId = session['userId']
        # check if session cookie is using the right data, if not logout
        psw = session['psw']
        cursor = connectDatabase()
        cursor.execute(
            'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw != psw_check:
            return redirect('/logout')

        # If everything right start this code
        loggedIn = True
        userId = session['userId']
        # Checking if finished signup
        if checkCompleteUser(userId) != True:
            return checkCompleteUser(userId)

        cursor = connectDatabase()
        cursor.execute(
            'SELECT firstname FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        firstname = cursor.fetchone()[0]
        cursor.close()
        return render_template('index.html', loggedIn=loggedIn, firstname=firstname)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # check if session cookie exist, if not returns to login
    if 'userId' not in session:
        return redirect('/login')
    else:
        userId = session['userId']
        # check if session cookie is using the right data, if not logout
        psw = session['psw']
        cursor = connectDatabase()
        cursor.execute(
            'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw != psw_check:
            return redirect('/logout')

        # Check if user completed his sign up infos
        cursor.execute(
            'SELECT EXISTS(SELECT * from user_table WHERE user_id="{userId}");'.format(userId=userId))
        info_check = cursor.fetchone()[0]
        if info_check != 1:
            return redirect('/signup/complete-signup')

        # Show users data
        cursor.execute(
            'SELECT * FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        userInfo = cursor.fetchone()
        firstname = userInfo[3]
        lastname = userInfo[4]
        cursor.execute(
            'SELECT * FROM farm_table WHERE user_id="{userId}";'.format(userId=userId))
        farmInfo = cursor.fetchone()
        farmId = farmInfo[0]
        farmname = farmInfo[2]
        description = farmInfo[3]
        # Time
        cursor.execute('''SELECT * FROM time_table WHERE farm_id="{farmId}" 
                        ORDER BY 
                            CASE WHEN day = 'Monday' THEN 1
                                WHEN day = 'Tuesday' THEN 2
                                WHEN day = 'Wednesday' THEN 3
                                WHEN day = 'Thursday' THEN 4
                                WHEN day = 'Friday' THEN 5
                                WHEN day = 'Saturday' THEN 6
                                WHEN day = 'Sunday' THEN 7
                        END ASC;'''.format(farmId=farmId))
        time = cursor.fetchall()
        # Adress
        cursor.execute(
            '''SELECT * FROM adress_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
        farmAdress = cursor.fetchone()
        adress = farmAdress[1]+', '+str(farmAdress[2])+' '+farmAdress[3]
        cursor.execute('''
            SELECT 
                farm_id, category, product_name, product_description, product_price, product_weight 
            FROM product_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
        products = cursor.fetchall()
        cursor.close()
        return render_template('profile.html', page_title='My Page', farmname=farmname, firstname=firstname, lastname=lastname,  description=description, time=time, adress=adress, products=products)


@app.route('/profile/product-add', methods=['GET', 'POST'])
def addProduct():
    # check if session cookie exist, if not returns to login
    if 'userId' not in session:
        return redirect('/login')
    else:
        userId = session['userId']
        # check if session cookie is using the right data, if not logout
        psw = session['psw']
        cursor = connectDatabase()
        cursor.execute(
            'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw != psw_check:
            return redirect('/logout')

        # Get farmId
        cursor = connectDatabase()
        cursor.execute(
            'SELECT farm_id FROM farm_table WHERE user_id="{userId}";'.format(userId=userId))
        farmId = cursor.fetchone()[0]

        # Create product
        productName = request.form.get('productName')
        productDescription = request.form.get('productDescription')
        price = request.form.get('priceEuro')+'.'+request.form.get('priceCent')
        weight = request.form.get('weight')
        category = request.form.get('category')

        cursor.execute(
            '''INSERT INTO 
                product_table (farm_id, product_name, product_description, product_price, product_weight) 
            VALUES ("{farmId}", "{category}" "{productName}", "{productDescription}", "{price}", "{weight}");'''.format(
                farmId=farmId, category=category, productName=productName, productDescription=productDescription, price=price, weight=weight))
        cursor.execute('COMMIT;')
        cursor.close()

        return redirect('/profile')


# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, debug=True)
