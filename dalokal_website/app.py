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
            farm_table.farm_img,
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
        cursor.close()

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
        farmImg = farmInfo[3]
        description = farmInfo[4]
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
        timesUpdated = ()
        for time in times:
            if str(time[2]) != '0:00:00':
                timesUpdated = timesUpdated + (time,)
                
                
        # Adress
        cursor.execute(
            '''SELECT * FROM adress_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
        farmAdress = cursor.fetchone()
        adress = farmAdress[1]+', '+str(farmAdress[2])+' '+farmAdress[3]
        cursor.execute('''
            SELECT 
                product_id, farm_id, category, product_name, product_img, product_description, product_price, product_weight 
            FROM product_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
        products = cursor.fetchall()
        cursor.close()
        return render_template('profile.html', page_title='My Page', farmname=farmname, farmImg=farmImg, firstname=firstname, lastname=lastname,  description=description, time=timesUpdated, adress=adress, products=products)


@app.route('/user/<farmname>', methods=['GET', 'POST'])
def user(farmname):
    cursor = connectDatabase()
    cursor.execute(
        'SELECT * FROM farm_table WHERE farmname="{farmname}";'.format(farmname=farmname))
    farmInfo = cursor.fetchone()
    farmId = farmInfo[0]
    userId = farmInfo[1]
    farmImg = farmInfo[3]
    if 'userId' in session:
        # to remove or keep the logout btn if logged in or not
        notLoggedIn = 0
        if userId == session['userId']:
            return redirect('/profile')
    else:
        notLoggedIn = 1
    farmname = farmInfo[2]
    description = farmInfo[4]
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
    timesUpdated = ()
    for time in times:
        if str(time[2]) != '0:00:00':
            timesUpdated = timesUpdated + (time,)
    # Adress
    cursor.execute(
        '''SELECT * FROM adress_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
    farmAdress = cursor.fetchone()
    adress = farmAdress[1]+', '+str(farmAdress[2])+' '+farmAdress[3]
    cursor.execute('''
        SELECT 
            product_id, farm_id, category, product_name, product_img, product_description, product_price, product_weight 
        FROM product_table WHERE farm_id="{farmId}";'''.format(farmId=farmId))
    products = cursor.fetchall()
    notMyAccount = 1
    cursor.close()
    return render_template('profile.html', page_title=farmname, farmname=farmname, farmImg=farmImg, description=description, time=timesUpdated, adress=adress, products=products, notMyAccount=notMyAccount, notLoggedIn = notLoggedIn)


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
        productName = request.form.get('productName').capitalize()
        productDescription = request.form.get('productDescription').capitalize()
        price = request.form.get('priceEuro')+'.'+request.form.get('priceCent')
        weight = request.form.get('weight')
        category = request.form.get('category')

        # Update category table for the farm and give it a img depending on the category of the product
        if category == "Vegetable":
            img = 'vegetable.jpg'
            cursor.execute('''
                UPDATE category_table 
                SET veg_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Milk product":
            img = 'milk.jpg'
            cursor.execute('''
                UPDATE category_table 
                SET milk_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Wheat":
            img = 'wheat.jpg'
            cursor.execute('''
                UPDATE category_table 
                SET wheat_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))
        if category == "Meat":
            img = 'meat.jpg'
            cursor.execute('''
                UPDATE category_table 
                SET meat_check = 1 
                WHERE farm_id = "{farmId}";'''.format(
                farmId=farmId))

        cursor.execute(
            '''INSERT INTO 
                product_table (farm_id, category, product_name, product_img, product_description, product_price, product_weight) 
            VALUES ("{farmId}", "{category}", "{productName}", "{productImg}", "{productDescription}", "{price}", "{weight}");'''.format(
                farmId=farmId, category=category, productName=productName, productImg=img, productDescription=productDescription, price=price, weight=weight))
        cursor.execute('COMMIT;')
        cursor.close()

        return redirect('/profile')

@app.route('/profile/delete-product/<productId>', methods=['GET', 'POST'])
def deleteProduct(productId):
    cursor = connectDatabase()
    cursor.execute('''
    DELETE
    FROM product_table
    WHERE product_id="{productId}";
    '''.format(productId=productId))
    cursor.execute('COMMIT;')
    cursor.close()
    return redirect('/profile')



@app.route('/profile/edit', methods=['GET', 'POST'])
def edit():
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

        cursor.execute('''
        SELECT farm_table.user_id,
            farm_table.farmname,
            farm_table.description,
            user_table.email,
            user_table.firstname,
            user_table.lastname,
            adress_table.street,
            adress_table.postalcode,
            adress_table.city
        FROM farm_table
        JOIN user_table
        ON user_table.user_id=farm_table.user_id
        JOIN adress_table
        ON adress_table.farm_id=farm_table.farm_id
        WHERE farm_table.user_id ="{userId}";'''.format(
            userId=userId))
        userData = cursor.fetchone()
        cursor.execute('''
        SELECT time_table.day, 
            time_table.opening, 
            time_table.closing
        FROM farm_table
        JOIN time_table
        ON time_table.farm_id=farm_table.farm_id
        WHERE user_id="{userId}";'''.format(
            userId=userId))
        userTime = cursor.fetchall()

        # If method Post than...
        if request.method == 'POST':
            email = request.form.get('email')
            if email:
                try:
                    # Update db
                    cursor.execute('''
                    UPDATE user_table SET email="{email}" WHERE user_id="{userId}";
                    '''.format(email=email, userId=userId))
                except:
                    return render_template('edit.html', edit=1, userTime=userTime, userData=userData, flash_message='emailEdit')

            password = request.form.get('psw')
            password_repeat = request.form.get('psw_repeat')
            if password:
                # check if psw are same
                if password == password_repeat:
                    # Hash changed password
                    password = generate_password_hash(password)
                    # Update db
                    cursor.execute('''
                    UPDATE user_table
                    SET password="{password}"
                    WHERE user_id="{userId}";
                    '''.format(password=password, userId=userId))
                else:
                    return render_template('edit.html', edit=1, userTime=userTime, userData=userData, flash_message='psw')

            firstname = request.form.get('firstname')
            if firstname:
                cursor.execute('''
                UPDATE user_table
                SET firstname="{firstname}"
                WHERE user_id="{userId}";
                '''.format(firstname=firstname, userId=userId))

            lastname = request.form.get('lastname')
            if lastname:
                cursor.execute('''
                UPDATE user_table
                SET lastname="{lastname}"
                WHERE user_id="{userId}";
                '''.format(lastname=lastname, userId=userId))

            farmname = request.form.get('farmname')
            if farmname:
                try:
                    cursor.execute('''
                    UPDATE farm_table
                    SET farmname="{farmname}"
                    WHERE user_id="{userId}";
                    '''.format(farmname=farmname, userId=userId))
                except:
                    return render_template('edit.html', edit=1, userTime=userTime, userData=userData, flash_message='name')

            street = request.form.get('farmStreet')
            postalCode = request.form.get('farmPostalCode')
            city = request.form.get('farmCity')
            if street:
                cursor.execute('''
                UPDATE farm_table
                JOIN adress_table
                ON adress_table.farm_id=farm_table.farm_id
                SET adress_table.street="{street}",
                    adress_table.postalcode="{postalCode}",
                    adress_table.city="{city}"
                WHERE farm_table.user_id="{userId}";
                '''.format(userId=userId, street=street, postalCode=postalCode, city=city))

            cursor.execute('''
            SELECT time_table.day, 
                time_table.opening, 
                time_table.closing
            FROM farm_table
            JOIN time_table
            ON time_table.farm_id=farm_table.farm_id
            WHERE user_id="{userId}";
            '''.format(userId=userId))
            timeCheck  = cursor.fetchall()

            # Check if days time is different in db and given value. If yes it will update db
            mon_b = request.form.get('mon_b')
            mon_e = request.form.get('mon_e')
            if str(mon_b) != str(timeCheck[0][1]) and str(mon_e) != str(timeCheck[0][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{mon_b}",
                    closing="{mon_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Monday";
                '''.format(mon_b=mon_b, mon_e=mon_e, userId=userId))
           

            tue_b = request.form.get('tue_b')
            tue_e = request.form.get('tue_e')
            if str(tue_b) != str(timeCheck[1][1]) and str(tue_e) != str(timeCheck[1][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{tue_b}",
                    closing="{tue_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Tuesday";
                '''.format(tue_b=tue_b, tue_e=tue_e, userId=userId))
            

            wed_b = request.form.get('wed_b')
            wed_e = request.form.get('wed_e')
            if str(wed_b) != str(timeCheck[2][1]) and str(wed_e) != str(timeCheck[2][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{wed_b}",
                    closing="{wed_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Wednesday";
                '''.format(wed_b=wed_b, wed_e=wed_e, userId=userId))
            

            thu_b = request.form.get('thu_b')
            thu_e = request.form.get('thu_e')
            if str(thu_b) != str(timeCheck[3][1]) and str(thu_e) != str(timeCheck[3][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{thu_b}",
                    closing="{thu_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Thursday";
                '''.format(thu_b=thu_b, thu_e=thu_e, userId=userId))
            

            fri_b = request.form.get('fri_b')
            fri_e = request.form.get('fri_e')
            if str(fri_b) != str(timeCheck[4][1]) and str(fri_e) != str(timeCheck[4][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{fri_b}",
                    closing="{fri_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Friday";
                '''.format(fri_b=fri_b, fri_e=fri_e, userId=userId))
            

            sat_b = request.form.get('sat_b')
            sat_e = request.form.get('sat_e')
            if str(sat_b) != str(timeCheck[5][1]) and str(sat_e) != str(timeCheck[5][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{sat_b}",
                    closing="{sat_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Saturday";
                '''.format(sat_b=sat_b, sat_e=sat_e, userId=userId))
            

            sun_b = request.form.get('sun_b')
            sun_e = request.form.get('sun_e')
            if str(sun_b) != str(timeCheck[6][1]) and str(sun_e) != str(timeCheck[6][2]):
                cursor.execute('''
                UPDATE farm_table
                JOIN time_table
                ON time_table.farm_id=farm_table.farm_id
                SET opening="{sun_b}",
                    closing="{sun_e}"
                WHERE farm_table.user_id="{userId}"
                AND time_table.day="Sunday";
                '''.format(sun_b=sun_b, sun_e=sun_e, userId=userId))
            

            cursor.execute('COMMIT;')
            return redirect('/profile')

        cursor.close()
        return render_template('edit.html', edit=1, userData=userData, userTime=userTime, flash_message='')


# if __name__ == "__main__":
#     app.run(host="localhost", port=8080, debug=True)
