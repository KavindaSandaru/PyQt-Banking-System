import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "atm.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts(
            account_number TEXT PRIMARY KEY,
            pin TEXT NOT NULL,
            balance REAL DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked INTEGER DEFAULT 0,
            name TEXT,
            birthday TEXT,
            profile_picture TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT,
            type TEXT,
            amount REAL,
            created_at TEXT,
            description TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            category TEXT DEFAULT 'Info',
            created_at TEXT,
            read INTEGER DEFAULT 0
        )
        """
    )

    _ensure_column(cursor, "accounts", "name", "TEXT")
    _ensure_column(cursor, "accounts", "birthday", "TEXT")
    _ensure_column(cursor, "accounts", "profile_picture", "TEXT")
    _ensure_column(cursor, "transactions", "created_at", "TEXT")
    _ensure_column(cursor, "transactions", "description", "TEXT")

    conn.commit()
    conn.close()


def _ensure_column(cursor, table_name, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


def create_admin():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO accounts
        (account_number, pin, balance, name)
        VALUES (?, ?, ?, ?)
        """,
        ("admin", "admin123", 0, "Admin"),
    )

    conn.commit()
    conn.close()


def seed_demo_data():
    create_tables()
    create_admin()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO accounts
        (account_number, pin, balance, name, birthday)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("1999", "1234", 514000, "Ishan", "2000-01-01"),
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO accounts
        (account_number, pin, balance, name, birthday)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("1998", "1234", 495000, "John Doe", "1999-05-15"),
    )

    cursor.execute(
        """
        UPDATE accounts
        SET name = COALESCE(name, ?),
            birthday = COALESCE(birthday, ?)
        WHERE account_number = ?
        """,
        ("Ishan", "2000-01-01", "1999"),
    )

    cursor.execute(
        """
        UPDATE accounts
        SET name = COALESCE(name, ?),
            birthday = COALESCE(birthday, ?)
        WHERE account_number = ?
        """,
        ("John Doe", "1999-05-15", "1998"),
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        WHERE account_number = ?
        """,
        ("1999",),
    )
    has_history = cursor.fetchone()[0] > 0

    if not has_history:
        demo_transactions = [
            ("1999", "Deposit", 10000, "Cash deposit", "2024-05-18 10:30:00"),
            ("1999", "Withdraw", 2000, "ATM withdrawal", "2024-05-17 16:15:00"),
            ("1999", "Transfer Out", 5000, "Transfer to 1998", "2024-05-16 11:20:00"),
            ("1999", "Deposit", 20000, "Cash deposit", "2024-05-15 09:45:00"),
        ]

        cursor.executemany(
            """
            INSERT INTO transactions
            (account_number, type, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            demo_transactions,
        )

    conn.commit()
    conn.close()


def create_account(account_number, pin, initial_balance=0, name="", birthday=""):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO accounts
        (account_number, pin, balance, name, birthday)
        VALUES (?, ?, ?, ?, ?)
        """,
        (account_number, pin, initial_balance, name, birthday),
    )

    conn.commit()
    conn.close()

    add_alert(
        account_number,
        "Account created",
        "Your new bank account registration was completed.",
        "Account",
    )


def get_account(account_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT account_number, pin, balance, failed_attempts, locked, name, birthday, profile_picture
        FROM accounts
        WHERE account_number = ?
        """,
        (account_number,),
    )

    account = cursor.fetchone()

    conn.close()

    return account


def get_account_profile(account_number):
    account = get_account(account_number)

    if not account:
        return {
            "account_number": account_number,
            "name": f"Account {account_number}",
            "birthday": "",
            "profile_picture": "",
        }

    return {
        "account_number": account[0],
        "balance": account[2],
        "failed_attempts": account[3],
        "locked": bool(account[4]),
        "name": account[5] or f"Account {account_number}",
        "birthday": account[6] or "",
        "profile_picture": account[7] or "",
    }


def update_account_profile(account_number, name, birthday):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET name = ?, birthday = ?
        WHERE account_number = ?
        """,
        (name, birthday, account_number),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if changed:
        add_alert(
            account_number,
            "Account settings updated",
            "Your profile details were changed.",
            "Account",
        )

    return changed


def update_profile_picture(account_number, profile_picture):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET profile_picture = ?
        WHERE account_number = ?
        """,
        (profile_picture, account_number),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if changed:
        add_alert(
            account_number,
            "Profile picture changed",
            "A new profile picture was added to your account.",
            "Account",
        )

    return changed


def record_login_failure(account_number):
    account = get_account(account_number)

    if account is None:
        add_alert(
            "admin",
            "Unknown login attempt",
            f"Failed login for unknown account {account_number}.",
            "Security",
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET failed_attempts = failed_attempts + 1
        WHERE account_number = ?
        """,
        (account_number,),
    )

    conn.commit()
    conn.close()

    add_alert(
        account_number,
        "Failed login attempt",
        "Someone entered an incorrect PIN for this account.",
        "Security",
    )


def record_login_success(account_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET failed_attempts = 0
        WHERE account_number = ?
        """,
        (account_number,),
    )

    conn.commit()
    conn.close()


def view_accounts():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT account_number, balance
        FROM accounts
        ORDER BY account_number
        """
    )

    accounts = cursor.fetchall()

    conn.close()

    return accounts


def get_balance(account_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT balance
        FROM accounts
        WHERE account_number = ?
        """,
        (account_number,),
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0


def deposit(account_number, amount):
    amount = float(amount)

    if amount <= 0:
        return False

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance + ?
        WHERE account_number = ?
        """,
        (amount, account_number),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if changed:
        add_transaction(account_number, "Deposit", amount, "Cash deposit")
        add_alert(
            account_number,
            "Deposit completed",
            f"{amount:,.2f} was added to your account.",
            "Transaction",
        )

    return changed


def withdraw(account_number, amount):
    amount = float(amount)

    if amount <= 0:
        return False

    balance = get_balance(account_number)

    if amount > balance:
        return False

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance - ?
        WHERE account_number = ?
        """,
        (amount, account_number),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if changed:
        add_transaction(account_number, "Withdraw", amount, "ATM withdrawal")
        add_alert(
            account_number,
            "Withdrawal completed",
            f"{amount:,.2f} was withdrawn from your account.",
            "Transaction",
        )

    return changed


def add_transaction(account_number, transaction_type, amount, description=""):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transactions
        (account_number, type, amount, created_at, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account_number,
            transaction_type,
            float(amount),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description,
        ),
    )

    conn.commit()
    conn.close()


def get_transactions(account_number, limit=None):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT id, account_number, type, amount, created_at, description
        FROM transactions
        WHERE account_number = ?
        ORDER BY id DESC
    """
    params = [account_number]

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    transactions = cursor.fetchall()

    conn.close()

    return transactions


def transfer(sender_account, receiver_account, amount):
    amount = float(amount)

    if amount <= 0:
        return False

    sender_balance = get_balance(sender_account)

    if sender_balance < amount:
        return False

    receiver = get_account(receiver_account)

    if receiver is None or receiver_account == sender_account:
        return False

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance - ?
        WHERE account_number = ?
        """,
        (amount, sender_account),
    )

    cursor.execute(
        """
        UPDATE accounts
        SET balance = balance + ?
        WHERE account_number = ?
        """,
        (amount, receiver_account),
    )

    conn.commit()
    conn.close()

    add_transaction(
        sender_account,
        "Transfer Out",
        amount,
        f"Transfer to {receiver_account}",
    )
    add_transaction(
        receiver_account,
        "Transfer In",
        amount,
        f"Transfer from {sender_account}",
    )

    add_alert(
        sender_account,
        "Transfer sent",
        f"{amount:,.2f} was sent to account {receiver_account}.",
        "Transaction",
    )
    add_alert(
        receiver_account,
        "Transfer received",
        f"{amount:,.2f} was received from account {sender_account}.",
        "Transaction",
    )

    return True


def add_alert(account_number, title, message, category="Info"):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO alerts
        (account_number, title, message, category, created_at, read)
        VALUES (?, ?, ?, ?, ?, 0)
        """,
        (
            account_number,
            title,
            message,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()


def get_alerts(account_number, limit=None):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT id, title, message, category, created_at, read
        FROM alerts
        WHERE account_number = ?
        ORDER BY id DESC
    """
    params = [account_number]

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    alerts = cursor.fetchall()

    conn.close()

    return alerts


def get_unread_alert_count(account_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM alerts
        WHERE account_number = ? AND read = 0
        """,
        (account_number,),
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count


def mark_alerts_read(account_number):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE alerts
        SET read = 1
        WHERE account_number = ?
        """,
        (account_number,),
    )

    conn.commit()
    conn.close()


def get_all_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT account_number, type, amount, created_at, description
        FROM transactions
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


def get_total_money():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SUM(balance)
        FROM accounts
        """
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total or 0
