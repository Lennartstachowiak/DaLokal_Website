import os

import logging
import pymysql
from flask import Blueprint, render_template, request, session, jsonify, redirect
from datetime import date, datetime, time
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
    cursor.close()
    if checkUser == None:
        return redirect('/signup/complete-signup')
    if checkFarm != 1:
        return redirect('/signup/complete-signup/farm-information')
    return True


def openOrClosed(farmId):
    cursor = connectDatabase()
    # Get current time
    time = datetime.now().time()
    # Convert to timedelta because of html and database type time
    time = datetime.combine(date.min, time) - datetime.min
    # Check the current date
    weekday = date.today().weekday()
    if weekday == 0:
        day = 'Monday'
    if weekday == 1:
        day = 'Tuesday'
    if weekday == 2:
        day = 'Wednesday'
    if weekday == 3:
        day = 'Thursday'
    if weekday == 4:
        day = 'Friday'
    if weekday == 5:
        day = 'Saturday'
    if weekday == 6:
        day = 'Sunday'
    cursor.execute('''
        SELECT opening, closing 
        FROM time_table 
        WHERE farm_id="{farmId}" 
        AND day="{day}";'''.format(
        farmId=farmId, day=day
    ))
    farmTime = cursor.fetchall()
    if farmTime != ():
        opening = farmTime[0][0]
        closing = farmTime[0][1]
        if time > opening and time < closing:
            return 1
        else:
            return 0
    else:
        # Check if closed or no data given
        cursor.execute('''
            SELECT * FROM time_table WHERE farm_id = "{farmId}";'''.format(
            farmId=farmId))
        timeData = cursor.fetchall()
        if timeData != ():
            return 0
        return 2


@app.route('/', methods=['GET', 'POST'])
def index():
    # Use farm id to get all data of all farms
    cursor = connectDatabase()
    cursor.execute('''
        SELECT farm_table.farm_id,
            farm_table.farmname,
            adress_table.street,
            adress_table.postalcode,
            adress_table.city,
            category_table.veg_check,
            category_table.milk_check,
            category_table.wheat_check,
            category_table.meat_check
        FROM farm_table
        JOIN adress_table
        ON adress_table.farm_id=farm_table.farm_id
        JOIN category_table
        ON category_table.farm_id=farm_table.farm_id;
        ''')
    farms = cursor.fetchall()
    cursor.close()
    farmsUpdated = ()

    # Check if farm is open or closed
    # Add open or closed to the farm tuples
    for farm in farms:
        farmId = farm[0]
        farm = farm + (openOrClosed(farmId),)
        farmsUpdated = farmsUpdated + (farm,)

    if 'userId' not in session:
        return render_template('index.html', farms=farmsUpdated)
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
        # Checking if finished signup
        if checkCompleteUser(userId) != True:
            return checkCompleteUser(userId)

        # Get firstname from user table
        cursor.execute(
            'SELECT firstname FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        firstname = cursor.fetchone()[0]
        # Get farm id from farm table
        cursor.execute(
            'SELECT farm_id FROM farm_table WHERE user_id="{userId}";'.format(userId=userId))
        farmId = cursor.fetchone()[0]

        return render_template('index.html', loggedIn=loggedIn, firstname=firstname, farms=farmsUpdated)


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
        times = cursor.fetchall()
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
        return render_template('profile.html', page_title='My Page', farmname=farmname, firstname=firstname, lastname=lastname,  description=description, time=times, adress=adress, products=products)


@app.route('/user/<farmname>', methods=['GET', 'POST'])
def user(farmname):
    cursor = connectDatabase()
    cursor.execute(
        'SELECT * FROM farm_table WHERE farmname="{farmname}";'.format(farmname=farmname))
    farmInfo = cursor.fetchone()
    farmId = farmInfo[0]
    userId = farmInfo[1]
    if userId in session:
        if userId == session['userId']:
            return redirect('/profile')
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
    notMyAccount = 1
    cursor.close()
    return render_template('profile.html', page_title=farmname, farmname=farmname, description=description, time=time, adress=adress, products=products, notMyAccount=notMyAccount)


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

        # Update category table for the farm
        if category == "Vegetable":
            cursor.execute('''
                UPDATE category_table 
                SET veg_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Milk product":
            cursor.execute('''
                UPDATE category_table 
                SET milk_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Wheat":
            cursor.execute('''
                UPDATE category_table 
                SET wheat_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Meat":
            cursor.execute('''
                UPDATE category_table 
                SET meat_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))

        cursor.execute(
            '''INSERT INTO 
                product_table (farm_id, category, product_name, product_description, product_price, product_weight) 
            VALUES ("{farmId}", "{category}", "{productName}", "{productDescription}", "{price}", "{weight}");'''.format(
                farmId=farmId, category=category, productName=productName, productDescription=productDescription, price=price, weight=weight))
        cursor.execute('COMMIT;')
        cursor.close()

        return redirect('/profile')


# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, debug=True)
