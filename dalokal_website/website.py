import os
import pymysql
from flask import Flask
from flask import Blueprint, render_template, request, session, jsonify, redirect
from datetime import date, datetime, time
""" For hashing the password """
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "hello"

createDatabase()

""" That connection is for GCloud """
# Connection to database set up+
def connectDatabase():
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    cursor = pymysql.connect(
        user=db_user,
        password=db_password,
        unix_socket=unix_socket,
        db=db_name
    )
    return cursor

# Database connection for local connection


# def connectDatabase():
#     cursor = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='My2418SQL5765',
#         database='dalokalschema'
#     ).cursor()
#     return cursor

def createDatabase():
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    cursor = pymysql.connect(
        user=db_user,
        password=db_password,
        unix_socket=unix_socket,
    )
    cursor.execute('''
        CREATE SCHEMA IF NOT EXISTS dalokalschema;
        ''')
        cursor.execute('USE dalokalschema;')
        cursor.execute('SET autocommit=1')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_table (
                user_id INT(11) NOT NULL AUTO_INCREMENT,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(500) NOT NULL,
                firstname VARCHAR(45),
                lastname VARCHAR(45),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id),
            UNIQUE KEY unique_email (email),
            UNIQUE KEY unique_user_id (user_id)
            );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_table (
            farm_id INT(11) NOT NULL AUTO_INCREMENT,
            user_id INT(11) NOT NULL,
            farmname VARCHAR(100) NOT NULL,
            farm_img VARCHAR(100) NOT NULL,
            description VARCHAR(1000) NOT NULL,
            total_products INT(11) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (farm_id),
            UNIQUE KEY unique_farm_id (farm_id),
            UNIQUE KEY unique_farmname (farmname),
            CONSTRAINT farmToTable FOREIGN KEY (user_id)
            REFERENCES user_table(user_id)
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_table (
            product_id INT(11) NOT NULL AUTO_INCREMENT,
            farm_id INT(11) NOT NULL,
            category VARCHAR(45) NOT NULL,
            product_name VARCHAR(45) NOT NULL,
            product_img VARCHAR(100) NOT NULL,
            product_description VARCHAR(500) NOT NULL,
            product_price DECIMAL (10,2) NOT NULL,
            product_weight DECIMAL (10,3) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (product_id),
            UNIQUE KEY unique_product_id (product_id),
            CONSTRAINT productToFarm FOREIGN KEY (farm_id)
            REFERENCES farm_table(farm_id)
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_table (
            farm_id INT(11) NOT NULL,
            day VARCHAR(45),
            opening TIME,
            closing TIME,
            CONSTRAINT timeToFarm FOREIGN KEY (farm_id)
            REFERENCES farm_table(farm_id)
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_table (
            farm_id INT(11) NOT NULL,
            veg_check TINYINT(4) NOT NULL DEFAULT '0',
            milk_check TINYINT(4) NOT NULL DEFAULT '0',
            wheat_check TINYINT(4) NOT NULL DEFAULT '0',
            meat_check TINYINT(4) NOT NULL DEFAULT '0',
            CONSTRAINT categoryToFarm FOREIGN KEY (farm_id)
            REFERENCES farm_table(farm_id)
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS adress_table (
            farm_id INT(11) NOT NULL,
            street VARCHAR(100) NOT NULL,
            postalcode INT(11) NOT NULL,
            city VARCHAR(45) NOT NULL,
            CONSTRAINT adressToFarm FOREIGN KEY (farm_id)
            REFERENCES farm_table(farm_id)
        );''')
        cursor.execute('DROP TRIGGER IF EXISTS farm_total_products_increase;')
        cursor.execute('DROP TRIGGER IF EXISTS farm_total_products_decrease;')
        cursor.execute('''
        CREATE TRIGGER farm_total_products_increase
        AFTER INSERT ON product_table
        FOR EACH ROW
            UPDATE farm_table
                SET total_products = total_products + 1
            WHERE farm_id = NEW.farm_id;''')
        cursor.execute('''
        CREATE TRIGGER farm_total_products_decrease
        AFTER DELETE ON product_table
        FOR EACH ROW
            UPDATE farm_table
                SET total_products = total_products - 1
            WHERE farm_id = OLD.farm_id;''')
        cursor.close()

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
    try:
        # Use farm id to get all data of all farms
        cursor = connectDatabase()
        cursor.execute('''
            SELECT farm_table.farm_id,
                farm_table.farmname,
                farm_table.farm_img,
                farm_table.total_products,
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
    except:
        return redirect('/error/problem')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
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
    except:
        return redirect('/error/problem')

@app.route('/user/<farmname>', methods=['GET', 'POST'])
def user(farmname):
    try:
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
        return render_template('profile.html', page_title=farmname, farmname=farmname, farmImg=farmImg, description=description, time=timesUpdated, adress=adress, products=products, notMyAccount=notMyAccount, notLoggedIn=notLoggedIn)
    except:
        return redirect('/error/problem')


@app.route('/profile/product-add', methods=['GET', 'POST'])
def addProduct():
    try:
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
            productDescription = request.form.get(
                'productDescription').capitalize()
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
    except:
        return redirect('/error/problem')


@app.route('/profile/delete-product/<productId>', methods=['GET', 'POST'])
def deleteProduct(productId):
    cursor = connectDatabase()
    # Get farm id and product category
    cursor.execute('''
    SELECT farm_id,
        category
    FROM product_table
    WHERE product_id="{productId}";
    '''.format(productId=productId))
    data = cursor.fetchall()
    if data == ():
        return redirect('/error/delete')
    farmId = data[0][0]
    category = data[0][1]
    # Get session id to check if user is allowed to delete the product
    sessionUserId = session['userId']
    # Get userId form farm_table
    cursor.execute('''
    SELECT user_id
    FROM farm_table
    WHERE farm_id="{farmId}"
    '''.format(farmId=farmId))
    userId = cursor.fetchone()[0]
    if userId != sessionUserId:
        error = 'delete'
        return redirect('/error/{error}'.format(error=error))
    else:
        cursor.execute('''
        DELETE
        FROM product_table
        WHERE product_id="{productId}";
        '''.format(productId=productId))
        cursor.execute('COMMIT;')
        # Check if product with this category still exists
        cursor.execute('''
        SELECT EXISTS(SELECT *
            FROM product_table
            WHERE category="{category}"
                AND farm_id="{farmId}");
        '''.format(category=category, farmId=farmId))
        checkCategory = cursor.fetchone()[0]
        if checkCategory != 1:
            if category == "Vegetable":
                changeCategory = "veg_check"
            if category == "Milk product":
                changeCategory = "milk_check"
            if category == "Wheat":
                changeCategory = "wheat_check"
            if category == "Meat":
                changeCategory = "meat_check"
            cursor.execute('''
            UPDATE category_table
            SET {changeCategory} = 0
            WHERE farm_id="{farmId}";
            '''.format(changeCategory=changeCategory, farmId=farmId))
            cursor.execute('COMMIT;')
        cursor.close()
        return redirect('/profile')


@app.route('/profile/delete-profile/<userId>', methods=['GET', 'POST'])
def deleteProfile(userId):
    # Get session userId
    sessionUserId = session['userId']
    if str(userId) != str(sessionUserId):
        error = 'delete'
        return redirect('/error/{error}'.format(error=error))
    else:
        cursor = connectDatabase()
        # Delete products if exists
        cursor.execute('''
        SELECT product_table.product_id
        FROM farm_table
        JOIN product_table
        ON product_table.farm_id=farm_table.farm_id
        WHERE user_id="{userId}";
        '''.format(userId=userId))
        productIds = cursor.fetchall()
        # Delete ever product after the other because of trigger 'after delete'
        for productId in productIds:
            cursor.execute('''
            DELETE
            FROM product_table
            WHERE product_id="{productId[0]}"
            '''.format(productId=productId))

        # Delete time_table if exists
        cursor.execute('''
        DELETE time_table
        FROM farm_table
        JOIN time_table
        ON time_table.farm_id=farm_table.farm_id
        WHERE farm_table.user_id="{userId}";
        '''.format(userId=userId))

        # Delete category_table if exists
        cursor.execute('''
        DELETE category_table
        FROM farm_table
        JOIN category_table
        ON category_table.farm_id=farm_table.farm_id
        WHERE farm_table.user_id="{userId}";
        '''.format(userId=userId))

        # Delete adress
        cursor.execute('''
        DELETE adress_table
        FROM farm_table
        JOIN adress_table
        ON adress_table.farm_id=farm_table.farm_id
        WHERE farm_table.user_id="{userId}";
        '''.format(userId=userId))
        cursor.execute('COMMIT;')
        # Have to be separeted deleted because of foreign key constraints
        cursor.execute('''
        DELETE
        FROM farm_table
        WHERE user_id="{userId}";
        '''.format(userId=userId))
        cursor.execute('COMMIT;')
        # Have to be separeted deleted because of foreign key constraints
        cursor.execute('''
        DELETE
        FROM user_table
        WHERE user_id="{userId}";
        '''.format(userId=userId))
        cursor.execute('COMMIT;')
        cursor.close()
        # go to logout to delete session and than jump to main
        return redirect('/logout')


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit():
    # Error handling
    try:
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

                description = request.form.get('description')
                if description:
                    cursor.execute('''
                    UPDATE farm_table
                    SET description="{description}"
                    WHERE user_id="{userId}";
                    '''.format(description=description, userId=userId))


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
                timeCheck = cursor.fetchall()

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

                farmImg = request.form.get('farmImg')
                if farmImg:
                    cursor.execute('''
                    UPDATE farm_table
                    SET farm_img="{farmImg}"
                    WHERE user_id="{userId}";
                    '''.format(farmImg=farmImg, userId=userId))

                cursor.execute('COMMIT;')
                return redirect('/profile')

            cursor.close()
            return render_template('edit.html', edit=1, userData=userData, userTime=userTime, flash_message='')
    except:
        return redirect('/error/problem')


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # If not post than just return html
        if request.method != 'POST':
            return render_template('login.html', flash_message='')
        else:
            email = request.form.get('email')
            psw = request.form.get('psw')
            # Have to do something with that ->
            remember = True if request.form.get('remember') else False

            # Check if email not in db
            cursor = connectDatabase()
            cursor.execute(
                'SELECT EXISTS(SELECT email FROM user_table WHERE email="{email}");'.format(email=email))
            email_check = cursor.fetchone()[0]
            if not email_check:
                return render_template('login.html', flash_message='wrong')
            else:
                cursor.execute(
                    'SELECT password FROM user_table WHERE email="{email}";'.format(email=email))
                psw_check = cursor.fetchone()[0]
                if not check_password_hash(psw_check, psw):
                    return render_template('login.html', flash_message='wrong')
                else:
                    # Get the user id from the logged in user
                    cursor.execute(
                        'SELECT user_id FROM user_table WHERE email="{email}";'.format(email=email))
                    userId = cursor.fetchone()[0]
                    cursor.close()
                    # Create a session cookie
                    session['userId'] = userId
                    session['psw'] = psw_check
                    return redirect('/')
    except:
        return redirect('/error/problem')


@app.route('/logout')
def logout():
    session.pop('userId', None)
    session.pop('email', None)
    session.pop('psw', None)
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        # Prevending going on this page while logged in
        if 'userId' in session:
            return redirect('/')
        # If not POST than returns static page
        if request.method != 'POST':
            return render_template('signup.html', flash_message="")
        else:
            email = request.form.get('email')
            # Check if email already exists
            cursor = connectDatabase()
            cursor.execute(
                'SELECT EXISTS(SELECT * FROM user_table WHERE email="{email}");'.format(email=email))
            emailCheck = cursor.fetchone()[0]
            if emailCheck == 1:
                return render_template('signup.html', flash_message='email')

            # hash the password for safty reasons
            psw = request.form.get('psw')
            psw_repeat = request.form.get('psw_repeat')
            # Checks if the psw's match each other
            if psw != psw_repeat:
                return render_template('signup.html', flash_message='psw')

            # Try to INSERT INTO the db
            # Email and password
            psw = generate_password_hash(psw)
            cursor.execute('INSERT INTO user_table (email, password) VALUES ("{email}","{psw}");'.format(
                email=email, psw=psw))
            # Commit changes to change the db
            cursor.execute('COMMIT;')
            # Adding the session cookies after signing up
            cursor.execute(
                'SELECT user_id FROM user_table WHERE email="{email}";'.format(email=email))
            session['userId'] = cursor.fetchone()[0]
            cursor.execute(
                'SELECT password FROM user_table WHERE email="{email}";'.format(email=email))
            session['psw'] = cursor.fetchone()[0]
            cursor.close()
            return redirect('/signup/complete-signup')
    except:
        return redirect('/error/problem')


@app.route('/signup/complete-signup', methods=['GET', 'POST'])
def complete_sign_up():
    try:
        # Check if session data is right
        if 'userId' not in session:
            return redirect('/')

        userId = session['userId']
        # check if session cookie is using the right data
        psw = session['psw']
        cursor = connectDatabase()
        cursor.execute(
            'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw != psw_check:
            cursor.close()
            return redirect('/logout')

        # prevents going back to this page
        cursor.execute(
            'SELECT firstname FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        checkUser = cursor.fetchone()[0]
        if checkUser != None:
            return redirect('/signup/complete-signup/farm-information')

        # check if method is post
        if request.method != 'POST':
            cursor.close()
            return render_template('complete_names.html')
        else:
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            # Update user
            cursor.execute('UPDATE user_table SET firstname="{firstname}", lastname="{lastname}" WHERE user_id={userId};'
                        .format(firstname=firstname, lastname=lastname, userId=userId))
            cursor.execute('COMMIT;')
            cursor.close()
            return redirect('/signup/complete-signup/farm-information')
    except:
        return redirect('/error/problem')


@app.route('/signup/complete-signup/farm-information', methods=['GET', 'POST'])
def farm_information():
    try:
        # Check if session data is right
        if 'userId' not in session:
            return redirect('/')

        userId = session['userId']
        # check if session cookie is using the right data
        psw = session['psw']
        cursor = connectDatabase()
        cursor.execute(
            'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
        psw_check = cursor.fetchone()[0]
        if psw != psw_check:
            cursor.close()
            return redirect('/logout')

        # prevents going back to this page
        cursor.execute(
            'SELECT EXISTS(SELECT * FROM farm_table WHERE user_id="{userId}");'.format(userId=userId))
        checkFarm = cursor.fetchone()[0]
        if checkFarm == 1:
            cursor.close()
            return redirect('/')

        if request.method != 'POST':
            cursor.close()
            return render_template('complete_farm.html', flash_message="")
        else:
            # Create farm for user
            farmname = request.form.get('farmname')
            cursor.execute(
                'SELECT EXISTS(SELECT * FROM farm_table WHERE farmname="{farmname}");'.format(farmname=farmname))
            nameCheck = cursor.fetchone()[0]
            if nameCheck == 1:
                return render_template('complete_farm.html', flash_message='name')
            description = request.form.get('farmDescription')
            farmImg = request.form.get('farmImg')
            cursor.execute('INSERT INTO farm_table (user_id, farmname, farm_img, description) VALUES ("{userId}", "{farmname}", "{farmImg}", "{description}");'.format(
                userId=userId, farmname=farmname, farmImg=farmImg, description=description))
            cursor.execute('COMMIT;')

            # Time
            cursor.execute(
                'SELECT farm_id FROM farm_table WHERE user_id="{userId}";'.format(userId=userId))
            farmId = cursor.fetchone()[0]

            mon_b = request.form.get('mon_b')
            mon_e = request.form.get('mon_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Monday","{b}","{e}");'.format(farmId=farmId, b=mon_b, e=mon_e))

            tue_b = request.form.get('tue_b')
            tue_e = request.form.get('tue_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Tuesday","{b}","{e}");'.format(farmId=farmId, b=tue_b, e=tue_e))

            wed_b = request.form.get('wed_b')
            wed_e = request.form.get('wed_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Wednesday","{b}","{e}");'.format(farmId=farmId, b=wed_b, e=wed_e))

            thu_b = request.form.get('thu_b')
            thu_e = request.form.get('thu_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Thursday","{b}","{e}");'.format(farmId=farmId, b=thu_b, e=thu_e))

            fri_b = request.form.get('fri_b')
            fri_e = request.form.get('fri_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Friday","{b}","{e}");'.format(farmId=farmId, b=fri_b, e=fri_e))

            sat_b = request.form.get('sat_b')
            sat_e = request.form.get('sat_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Saturday","{b}","{e}");'.format(farmId=farmId, b=sat_b, e=sat_e))

            sun_b = request.form.get('sun_b')
            sun_e = request.form.get('sun_e')

            cursor.execute(
                'INSERT INTO time_table VALUES ("{farmId}","Sunday","{b}","{e}");'.format(farmId=farmId, b=sun_b, e=sun_e))

            # Adress
            street = request.form.get('farmStreet')
            postalCode = request.form.get('farmPostalCode')
            city = request.form.get('farmCity')
            cursor.execute(
                'INSERT INTO adress_table VALUES ("{farmId}","{street}","{postalCode}","{city}");'.format(farmId=farmId, street=street, postalCode=postalCode, city=city))

            # Create farm category table
            cursor.execute('''
                INSERT INTO category_table (farm_id) 
                VALUES ("{farmId}");'''.format(
                farmId=farmId))

            # Commit inserts
            cursor.execute('COMMIT;')
            cursor.close()
            return redirect('/')
    except:
        return redirect('/error/problem')


# Error page


@app.route('/error/<error>', methods=['GET', 'POST'])
def error(error):
    if error == 'delete':
        msg = 'You can\'t delete others products or accounts!'
    if error == 'problem':
        msg = '''Something went wrong please try to logout and login again!
            If the error still appears please don't hesitate to contact us!
            Lennart.Stachowiak@gmail.com'''
    return render_template('error.html', msg=msg, notMyAccount=1)
