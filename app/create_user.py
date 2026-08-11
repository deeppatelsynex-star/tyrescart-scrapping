import getpass
import sys

import pymysql

from auth import VALID_ROLES, hash_password
from db import get_connection


def main():
    name = input('Name: ').strip()
    email = input('Email: ').strip()
    password = getpass.getpass('Password: ')
    confirm = getpass.getpass('Confirm password: ')
    role = input(f"Role [{'/'.join(VALID_ROLES)}] (default User): ").strip() or 'User'

    if not name or not email or not password:
        print('Name, email and password are required.')
        sys.exit(1)

    if password != confirm:
        print('Passwords do not match.')
        sys.exit(1)

    if role not in VALID_ROLES:
        print(f"Role must be one of: {', '.join(VALID_ROLES)}.")
        sys.exit(1)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO userTbl (Name, Email, password, Status, IsDeleted, Role) '
                    'VALUES (%s, %s, %s, 1, 0, %s)',
                    (name, email, hash_password(password), role),
                )
            except pymysql.err.IntegrityError:
                print(f'A user with email "{email}" already exists.')
                sys.exit(1)
        print(f'User "{email}" created successfully.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
