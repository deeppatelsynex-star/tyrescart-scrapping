"""
app/create_admin_user.py - CLI tool to create an administrator in the admin_users table.
"""

import getpass
import sys
import pymysql

from visionadmin.admin_auth import VALID_ADMIN_ROLES, hash_admin_password
from db import get_connection


def main():
    print("=== VisionAdmin CMS - Create Admin User ===")
    name = input('Name: ').strip()
    email = input('Email: ').strip()
    password = getpass.getpass('Password: ')
    confirm = getpass.getpass('Confirm password: ')
    role_options = '/'.join(VALID_ADMIN_ROLES)
    role = input(f"Role [{role_options}] (default super_admin): ").strip().lower() or 'super_admin'

    if not name or not email or not password:
        print('Error: Name, email and password are required.')
        sys.exit(1)

    if password != confirm:
        print('Error: Passwords do not match.')
        sys.exit(1)

    if len(password) < 8:
        print('Error: Password must be at least 8 characters long.')
        sys.exit(1)

    if role not in VALID_ADMIN_ROLES:
        print(f"Error: Role must be one of: {', '.join(VALID_ADMIN_ROLES)}.")
        sys.exit(1)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO `admin_users` (`name`, `email`, `password`, `role`, `is_active`, `created_at`, `updated_at`)
                    VALUES (%s, %s, %s, %s, 1, NOW(), NOW())
                """, (name, email.lower().strip(), hash_admin_password(password), role))
                conn.commit()
            except pymysql.err.IntegrityError:
                print(f'Error: An admin with email "{email}" already exists.')
                sys.exit(1)
        print(f'Success: Admin user "{email}" (role: {role}) created successfully in admin_users table.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
