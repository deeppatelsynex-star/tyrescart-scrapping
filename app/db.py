import os

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST', 'kodama.proxy.rlwy.net')
DB_PORT = int(os.environ.get('DB_PORT', '56470'))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'gDkJjvVBtGUqxdEjPuhYtzVeZfEPksZc')
DB_NAME = os.environ.get('DB_NAME', 'railway')


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
