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
        cursor.execute(
            'SELECT EXISTS(SELECT * FROM user_basic_table WHERE email="{email}");'.format(email=email))
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
        psw = generate_password_hash(psw)
        cursor.execute('INSERT INTO user_basic_table (email, password) VALUES ("{email}","{psw}");'.format(
            email=email, psw=psw))
        # Commit changes to change the db
        cursor.execute('COMMIT;')
        # Adding the session cookies after signing up
        cursor.execute(
            'SELECT user_id FROM user_basic_table WHERE email="{email}";'.format(email=email))
        session['userId'] = cursor.fetchone()[0]
        cursor.execute(
            'SELECT password FROM user_basic_table WHERE email="{email}";'.format(email=email))
        session['psw'] = cursor.fetchone()[0]
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

        cursor.execute(
            'SELECT email FROM user_basic_table WHERE email="{email}";'.format(email=email))
        email_check = cursor.fetchone()
        if not email_check:
            print('Wrong')
            return render_template('login.html', flash_message='wrong')
        else:
            cursor.execute(
                'SELECT password FROM user_basic_table WHERE email="{email}";'.format(email=email))
            psw_check = cursor.fetchone()[0]
            if not check_password_hash(psw_check, psw):
                return render_template('login.html', flash_message='wrong')
            else:
                """ Work with session and go back to homepage """
                # Get the user id from the logged in user
                cursor.execute(
                    'SELECT user_id FROM user_basic_table WHERE email="{email}";'.format(email=email))
                userId = cursor.fetchone()[0]
                session['userId'] = userId
                session['psw'] = psw_check
                return redirect('/')
    return render_template('login.html', flash_message='')


@auth.route('/logout')
def logout():
    session.pop('userId', None)
    session.pop('email', None)
    session.pop('psw', None)
    return redirect('/')


@auth.route('/sign-up/complete-sign-up', methods=['GET', 'POST'])
def complete_sign_up():
    if request.method == 'POST':
        # Check if session data is right
        if 'userId' in session:
            userId = session['userId']
            # check if session cookie is using the right data
            psw = session['psw']
            cursor.execute(
                'SELECT password FROM user_basic_table WHERE user_id="{userId}";'.format(userId=userId))
            psw_check = cursor.fetchone()[0]
            if psw == psw_check:

                # check if method is post
                if request.method == 'POST':
                    farmname = request.form.get('farmname')
                    firstname = request.form.get('firstname')
                    lastname = request.form.get('lastname')
                    # Insert data into database for the user
                    cursor.execute('INSERT INTO user_info_table VALUES ("{userId}", "{farmname}", "{firstname}", "{lastname}");'
                                   .format(userId=userId, farmname=farmname, firstname=firstname, lastname=lastname)
                                   )
                    cursor.execute('COMMIT;')
                    return redirect('/sign-up/complete-sign-up/farm-information')
            else:
                return redirect('/login')

    return render_template('complete_names.html')


@auth.route('/sign-up/complete-sign-up/farm-information', methods=['GET', 'POST'])
def farm_information():
    if request.method == 'POST':
        # Check if session data is right
        if 'userId' in session:
            userId = session['userId']
            # check if session cookie is using the right data
            psw = session['psw']
            cursor.execute(
                'SELECT password FROM user_basic_table WHERE user_id="{userId}";'.format(userId=userId))
            psw_check = cursor.fetchone()[0]
            if psw == psw_check:
                # Time
                timeDic = {'Monday':'','Tuesday':'','Wednesday':'','Thursday':'','Friday':'','Saturday':'','Sunday':''}

                mon_b = request.form.get('mon_b')
                mon_e = request.form.get('mon_e')
                monday = [mon_b,mon_e]
                timeDic['Monday'] = monday

                tue_b = request.form.get('tue_b')
                tue_e = request.form.get('tue_e')
                tuesday = [tue_b,tue_e]
                timeDic['Tuesday'] = tuesday

                wed_b = request.form.get('wed_b')
                wed_e = request.form.get('wed_e')
                wednesday = [wed_b,wed_e]
                timeDic['Wednesday'] = wednesday

                thu_b = request.form.get('thu_b')
                thu_e = request.form.get('thu_e')
                thursday = [thu_b,thu_e]
                timeDic['Thursday'] = thursday

                fri_b = request.form.get('fri_b')
                fri_e = request.form.get('fri_e')
                friday = [fri_b,fri_e]
                timeDic['Friday'] = friday

                sat_b = request.form.get('sat_b')
                sat_e = request.form.get('sat_e')
                saturday = [sat_b,sat_e]
                timeDic['Saturday'] = saturday
                
                sun_b = request.form.get('sun_b')
                sun_e = request.form.get('sun_e')
                sunday = [sun_b,sun_e]
                timeDic['Sunday'] = sunday

                # Adress
                adressDic = {'Street':'','StreetNumber':'','PostalCode':'','City':''}

                street = request.form.get('farmStreet')
                adressDic['Street'] = street

                streetNumber = request.form.get('farmStreetNumber')
                adressDic['StreetNumber'] = streetNumber

                postalCode = request.form.get('farmPostalCode')
                adressDic['PostalCode'] = postalCode

                city = request.form.get('farmCity')
                adressDic['City'] = city

                # Description
                description = request.form.get('farmDescription')

                # Insert data into database for the user
                cursor.execute('INSERT INTO farm_basic_table VALUES ("{userId}", "{timeDic}", "{adressDic}", "{description}");'
                                .format(userId=userId, timeDic=timeDic, adressDic = adressDic, description = description)
                                )
                cursor.execute('COMMIT;')
                return redirect('/')
            
            else:
                return redirect('/login')


    return render_template('complete_farm.html')
