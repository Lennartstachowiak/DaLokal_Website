# import os
# from flask import Blueprint, render_template, request, session, jsonify, redirect
# """ For hashing the password """
# import pymysql
# from werkzeug.security import generate_password_hash, check_password_hash

# auth = Blueprint('auth', __name__)

# """ That connection is for GCloud """
# # Connection to database set up
# # db_user = os.environ.get('CLOUD_SQL_USERNAME')
# # db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# # db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# # db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
# # unix_socket = '/cloudsql/{}'.format(db_connection_name)
# # conn = pymysql.connect(
# #     user=db_user,
# #     password=db_password,
# #     unix_socket=unix_socket,
# #     db=db_name
# # )
# # cursor = conn.cursor()

# # Database connection for local connection


# def connectDatabase():
#     cursor = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='My2418SQL5765',
#         database='dalokalschema'
#     ).cursor()
#     # cursor = conn.cursor()
#     return cursor


# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     try:
#         # If not post than just return html
#         if request.method != 'POST':
#             return render_template('login.html', flash_message='')
#         else:
#             email = request.form.get('email')
#             psw = request.form.get('psw')
#             # Have to do something with that ->
#             remember = True if request.form.get('remember') else False

#             # Check if email not in db
#             cursor = connectDatabase()
#             cursor.execute(
#                 'SELECT EXISTS(SELECT email FROM user_table WHERE email="{email}");'.format(email=email))
#             email_check = cursor.fetchone()[0]
#             if not email_check:
#                 return render_template('login.html', flash_message='wrong')
#             else:
#                 cursor.execute(
#                     'SELECT password FROM user_table WHERE email="{email}";'.format(email=email))
#                 psw_check = cursor.fetchone()[0]
#                 if not check_password_hash(psw_check, psw):
#                     return render_template('login.html', flash_message='wrong')
#                 else:
#                     # Get the user id from the logged in user
#                     cursor.execute(
#                         'SELECT user_id FROM user_table WHERE email="{email}";'.format(email=email))
#                     userId = cursor.fetchone()[0]
#                     cursor.close()
#                     # Create a session cookie
#                     session['userId'] = userId
#                     session['psw'] = psw_check
#                     return redirect('/')
#     except:
#         return redirect('/error/problem')


# @auth.route('/logout')
# def logout():
#     session.pop('userId', None)
#     session.pop('email', None)
#     session.pop('psw', None)
#     return redirect('/')


# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     try:
#         # Prevending going on this page while logged in
#         if 'userId' in session:
#             return redirect('/')
#         # If not POST than returns static page
#         if request.method != 'POST':
#             return render_template('signup.html', flash_message="")
#         else:
#             email = request.form.get('email')
#             # Check if email already exists
#             cursor = connectDatabase()
#             cursor.execute(
#                 'SELECT EXISTS(SELECT * FROM user_table WHERE email="{email}");'.format(email=email))
#             emailCheck = cursor.fetchone()[0]
#             if emailCheck == 1:
#                 return render_template('signup.html', flash_message='email')

#             # hash the password for safty reasons
#             psw = request.form.get('psw')
#             psw_repeat = request.form.get('psw_repeat')
#             # Checks if the psw's match each other
#             if psw != psw_repeat:
#                 return render_template('signup.html', flash_message='psw')

#             # Try to INSERT INTO the db
#             # Email and password
#             psw = generate_password_hash(psw)
#             cursor.execute('INSERT INTO user_table (email, password) VALUES ("{email}","{psw}");'.format(
#                 email=email, psw=psw))
#             # Commit changes to change the db
#             cursor.execute('COMMIT;')
#             # Adding the session cookies after signing up
#             cursor.execute(
#                 'SELECT user_id FROM user_table WHERE email="{email}";'.format(email=email))
#             session['userId'] = cursor.fetchone()[0]
#             cursor.execute(
#                 'SELECT password FROM user_table WHERE email="{email}";'.format(email=email))
#             session['psw'] = cursor.fetchone()[0]
#             cursor.close()
#             return redirect('/signup/complete-signup')
#     except:
#         return redirect('/error/problem')


# @auth.route('/signup/complete-signup', methods=['GET', 'POST'])
# def complete_sign_up():
#     try:
#         # Check if session data is right
#         if 'userId' not in session:
#             return redirect('/')

#         userId = session['userId']
#         # check if session cookie is using the right data
#         psw = session['psw']
#         cursor = connectDatabase()
#         cursor.execute(
#             'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
#         psw_check = cursor.fetchone()[0]
#         if psw != psw_check:
#             cursor.close()
#             return redirect('/logout')

#         # prevents going back to this page
#         cursor.execute(
#             'SELECT firstname FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
#         checkUser = cursor.fetchone()[0]
#         if checkUser != None:
#             return redirect('/signup/complete-signup/farm-information')

#         # check if method is post
#         if request.method != 'POST':
#             cursor.close()
#             return render_template('complete_names.html')
#         else:
#             firstname = request.form.get('firstname')
#             lastname = request.form.get('lastname')
#             # Update user
#             cursor.execute('UPDATE user_table SET firstname="{firstname}", lastname="{lastname}" WHERE user_id={userId};'
#                         .format(firstname=firstname, lastname=lastname, userId=userId))
#             cursor.execute('COMMIT;')
#             cursor.close()
#             return redirect('/signup/complete-signup/farm-information')
#     except:
#         return redirect('/error/problem')


# @auth.route('/signup/complete-signup/farm-information', methods=['GET', 'POST'])
# def farm_information():
#     try:
#         # Check if session data is right
#         if 'userId' not in session:
#             return redirect('/')

#         userId = session['userId']
#         # check if session cookie is using the right data
#         psw = session['psw']
#         cursor = connectDatabase()
#         cursor.execute(
#             'SELECT password FROM user_table WHERE user_id="{userId}";'.format(userId=userId))
#         psw_check = cursor.fetchone()[0]
#         if psw != psw_check:
#             cursor.close()
#             return redirect('/logout')

#         # prevents going back to this page
#         cursor.execute(
#             'SELECT EXISTS(SELECT * FROM farm_table WHERE user_id="{userId}");'.format(userId=userId))
#         checkFarm = cursor.fetchone()[0]
#         if checkFarm == 1:
#             cursor.close()
#             return redirect('/')

#         if request.method != 'POST':
#             cursor.close()
#             return render_template('complete_farm.html', flash_message="")
#         else:
#             # Create farm for user
#             farmname = request.form.get('farmname')
#             cursor.execute(
#                 'SELECT EXISTS(SELECT * FROM farm_table WHERE farmname="{farmname}");'.format(farmname=farmname))
#             nameCheck = cursor.fetchone()[0]
#             if nameCheck == 1:
#                 return render_template('complete_farm.html', flash_message='name')
#             description = request.form.get('farmDescription')
#             farmImg = request.form.get('farmImg')
#             cursor.execute('INSERT INTO farm_table (user_id, farmname, farm_img, description) VALUES ("{userId}", "{farmname}", "{farmImg}", "{description}");'.format(
#                 userId=userId, farmname=farmname, farmImg=farmImg, description=description))
#             cursor.execute('COMMIT;')

#             # Time
#             cursor.execute(
#                 'SELECT farm_id FROM farm_table WHERE user_id="{userId}";'.format(userId=userId))
#             farmId = cursor.fetchone()[0]

#             mon_b = request.form.get('mon_b')
#             mon_e = request.form.get('mon_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Monday","{b}","{e}");'.format(farmId=farmId, b=mon_b, e=mon_e))

#             tue_b = request.form.get('tue_b')
#             tue_e = request.form.get('tue_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Tuesday","{b}","{e}");'.format(farmId=farmId, b=tue_b, e=tue_e))

#             wed_b = request.form.get('wed_b')
#             wed_e = request.form.get('wed_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Wednesday","{b}","{e}");'.format(farmId=farmId, b=wed_b, e=wed_e))

#             thu_b = request.form.get('thu_b')
#             thu_e = request.form.get('thu_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Thursday","{b}","{e}");'.format(farmId=farmId, b=thu_b, e=thu_e))

#             fri_b = request.form.get('fri_b')
#             fri_e = request.form.get('fri_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Friday","{b}","{e}");'.format(farmId=farmId, b=fri_b, e=fri_e))

#             sat_b = request.form.get('sat_b')
#             sat_e = request.form.get('sat_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Saturday","{b}","{e}");'.format(farmId=farmId, b=sat_b, e=sat_e))

#             sun_b = request.form.get('sun_b')
#             sun_e = request.form.get('sun_e')

#             cursor.execute(
#                 'INSERT INTO time_table VALUES ("{farmId}","Sunday","{b}","{e}");'.format(farmId=farmId, b=sun_b, e=sun_e))

#             # Adress
#             street = request.form.get('farmStreet')
#             postalCode = request.form.get('farmPostalCode')
#             city = request.form.get('farmCity')
#             cursor.execute(
#                 'INSERT INTO adress_table VALUES ("{farmId}","{street}","{postalCode}","{city}");'.format(farmId=farmId, street=street, postalCode=postalCode, city=city))

#             # Create farm category table
#             cursor.execute('''
#                 INSERT INTO category_table (farm_id) 
#                 VALUES ("{farmId}");'''.format(
#                 farmId=farmId))

#             # Commit inserts
#             cursor.execute('COMMIT;')
#             cursor.close()
#             return redirect('/')
#     except:
#         return redirect('/error/problem')
