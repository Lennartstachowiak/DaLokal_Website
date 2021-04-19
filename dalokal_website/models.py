from flask_login import UserMixin

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
