import getpass
import sys

import pymysql

from auth import VALID_ROLES, hash_password
from db import get_connection


def main():
    name = input('Name: ').strip()
    email = input('Email: ').strip().lower()
    password = getpass.getpass('Password: ')
    confirm = getpass.getpass('Confirm password: ')
    role_in = input("Role [super_admin/manager/support] (default manager): ").strip().lower() or 'manager'

    if not name or not email or not password:
        print('Name, email and password are required.')
        sys.exit(1)

    if password != confirm:
        print('Passwords do not match.')
        sys.exit(1)

    valid_admin_roles = ('super_admin', 'manager', 'support')
    role = role_in if role_in in valid_admin_roles else ('super_admin' if role_in in ('superadmin', 'super-admin', 'super_admin') else 'manager')

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO `admin_users` (name, email, password, role, is_active, created_at, updated_at) '
                    'VALUES (%s, %s, %s, %s, 1, NOW(), NOW())',
                    (name, email, hash_password(password), role),
                )
                conn.commit()
            except pymysql.err.IntegrityError:
                print(f'An administrator with email "{email}" already exists.')
                sys.exit(1)
        print(f'Administrator "{email}" ({role}) created successfully in admin_users.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
