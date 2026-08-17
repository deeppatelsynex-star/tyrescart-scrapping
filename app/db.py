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

try:
    from dbutils.pooled_db import PooledDB

    _pool = PooledDB(
        creator=pymysql,
        mincached=2,
        maxcached=10,
        maxshared=0,
        maxconnections=30,
        blocking=True,
        maxusage=None,
        setsession=[],
        reset=True,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
except ImportError:
    _pool = None


def get_connection():
    """Fetches a pre-warmed connection from the connection pool instantly."""
    if _pool is not None:
        return _pool.connection()

    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
