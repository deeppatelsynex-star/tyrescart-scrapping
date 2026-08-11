from db import get_connection

CREATE_USER_TBL = """
CREATE TABLE IF NOT EXISTS userTbl (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    Status BIT(1) NOT NULL DEFAULT 1,
    IsDeleted BIT(1) NOT NULL DEFAULT 0,
    Role VARCHAR(50) NOT NULL
)
"""

CREATE_PASSWORD_RESET_TBL = """
CREATE TABLE IF NOT EXISTS password_reset_tbl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid INT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used BIT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userid) REFERENCES userTbl(userid) ON DELETE CASCADE
)
"""

# Additive columns for the profile/avatar and trash features. Existence is
# checked via information_schema before adding, so this stays safe to re-run.
NEW_COLUMNS = {
    "avatar": "ALTER TABLE userTbl ADD COLUMN avatar VARCHAR(500) NULL",
    "updated_at": (
        "ALTER TABLE userTbl ADD COLUMN updated_at TIMESTAMP NULL "
        "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    ),
    # Fixed at insert time (no ON UPDATE) so editing a user later doesn't
    # change when their account was originally created.
    "created_at": "ALTER TABLE userTbl ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    # Set when a user is soft-deleted, cleared on restore. NULL for accounts
    # that have never been deleted (and for rows soft-deleted before this
    # column existed).
    "deleted_at": "ALTER TABLE userTbl ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL",
}


def add_missing_columns(cursor):
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'userTbl'"
    )
    existing = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_COLUMNS.items():
        if column not in existing:
            cursor.execute(statement)


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_USER_TBL)
            add_missing_columns(cursor)
            cursor.execute(CREATE_PASSWORD_RESET_TBL)
        print("userTbl and password_reset_tbl are ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
