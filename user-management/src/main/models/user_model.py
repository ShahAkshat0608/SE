import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Determine DB path based on environment
_IS_TESTING = os.environ.get("TESTING") == "true"

if _IS_TESTING:
    # Use a dedicated test database file in the test directory
    # Assume tests run from the root of the project or tests are structured accordingly
    DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test', 'data'))
    DB_PATH = os.path.join(DB_DIR, 'test_users.db')
    logging.warning(f"--- RUNNING IN TEST MODE: Using test database at {DB_PATH} ---")
else:
    # Production/Development DB path
    DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    DB_PATH = os.path.join(DB_DIR, 'users.db')

def get_db_connection():
    """Establishes a connection to the SQLite database (test or dev)."""
    os.makedirs(DB_DIR, exist_ok=True) # Ensure data directory exists
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database (test or dev) by creating tables if they don't exist."""
    conn = None # Ensure conn is defined
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                contact TEXT,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        logging.info(f"Database checked/initialized successfully at {DB_PATH}.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization failed for {DB_PATH}: {e}")
        raise # Reraise after logging
    finally:
        if conn:
            conn.close()

def clear_test_database():
    """Drops the users table, specifically for cleaning up the test database."""
    if not _IS_TESTING:
        logging.error("Attempted to clear non-test database. Aborting.")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.warning(f"Clearing test database table 'users' at {DB_PATH}")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        logging.info("Test database table 'users' cleared.")
    except sqlite3.Error as e:
        logging.error(f"Failed to clear test database table 'users': {e}")
    finally:
        if conn:
            conn.close()

def create_user(name: str, email: str, password_hash: str, contact: str | None = None) -> dict | None:
    """Creates a new user in the database. Returns user details on success."""
    sql = '''INSERT INTO users(name, email, password_hash, contact)
             VALUES(?,?,?,?)'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (name, email, password_hash, contact))
        user_id = cursor.lastrowid
        conn.commit()
        logging.info(f"User '{email}' created successfully with ID: {user_id} in {DB_PATH}.")
        # Fetch the created user to return details
        cursor.execute("SELECT id, name, email, contact FROM users WHERE id = ?", (user_id,))
        new_user = cursor.fetchone()
        return dict(new_user) if new_user else None
    except sqlite3.IntegrityError:
        logging.warning(f"Attempted to create user with existing email: {email} in {DB_PATH}")
        return None # Email already exists
    except sqlite3.Error as e:
        logging.error(f"Failed to create user '{email}' in {DB_PATH}: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def find_user_by_email(email: str) -> dict | None:
    """Finds a user by their email address. Returns dict or None."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        logging.error(f"Error finding user by email '{email}' in {DB_PATH}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def find_user_by_id(user_id: int) -> dict | None:
    """Finds a user by their ID. Returns dict or None."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Select specific columns needed, excluding password hash
        cursor.execute("SELECT id, name, email, contact FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        logging.error(f"Error finding user by ID '{user_id}' in {DB_PATH}: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Initialize the database (test or dev) when the module is loaded
initialize_database() 