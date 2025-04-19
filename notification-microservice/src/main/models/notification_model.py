import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Determine DB path
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
DB_PATH = os.path.join(DB_DIR, 'notifications.db')

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)  # Ensure data directory exists
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the notification database by creating tables if they don't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                sent_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                event_id TEXT,
                summary TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        logging.info(f"Notification database initialized successfully at {DB_PATH}.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization failed for {DB_PATH}: {e}")
        raise
    finally:
        if conn:
            conn.close()

def create_email_notification(user_id, email, subject, body):
    """Creates a new email notification record."""
    sql = '''INSERT INTO email_notifications(user_id, email, subject, body, created_at)
             VALUES(?, ?, ?, ?, ?)'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(sql, (user_id, email, subject, body, now))
        notification_id = cursor.lastrowid
        conn.commit()
        logging.info(f"Email notification created for user {user_id} with ID: {notification_id}")
        
        # Fetch the created notification to return
        cursor.execute("SELECT * FROM email_notifications WHERE id = ?", (notification_id,))
        notification = cursor.fetchone()
        return dict(notification) if notification else None
    except sqlite3.Error as e:
        logging.error(f"Failed to create email notification for user {user_id}: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_email_notification_status(notification_id, status, sent_at=None):
    """Updates the status of an email notification."""
    sql = '''UPDATE email_notifications SET status = ?, sent_at = ? WHERE id = ?'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sent_time = sent_at or (datetime.now().isoformat() if status == 'sent' else None)
        cursor.execute(sql, (status, sent_time, notification_id))
        conn.commit()
        logging.info(f"Email notification {notification_id} updated to status: {status}")
        return True
    except sqlite3.Error as e:
        logging.error(f"Failed to update email notification {notification_id}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def create_calendar_event(user_id, email, summary, description, start_time, end_time):
    """Creates a new calendar event record."""
    sql = '''INSERT INTO calendar_events(user_id, email, summary, description, start_time, end_time, created_at)
             VALUES(?, ?, ?, ?, ?, ?, ?)'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(sql, (user_id, email, summary, description, start_time, end_time, now))
        event_id = cursor.lastrowid
        conn.commit()
        logging.info(f"Calendar event created for user {user_id} with ID: {event_id}")
        
        # Fetch the created event to return
        cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        return dict(event) if event else None
    except sqlite3.Error as e:
        logging.error(f"Failed to create calendar event for user {user_id}: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_calendar_event_status(event_id, status, google_event_id=None):
    """Updates the status and Google event ID of a calendar event."""
    sql = '''UPDATE calendar_events SET status = ?, event_id = ? WHERE id = ?'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (status, google_event_id, event_id))
        conn.commit()
        logging.info(f"Calendar event {event_id} updated to status: {status}")
        return True
    except sqlite3.Error as e:
        logging.error(f"Failed to update calendar event {event_id}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_pending_email_notifications(limit=10):
    """Retrieves pending email notifications."""
    sql = '''SELECT * FROM email_notifications WHERE status = 'pending' LIMIT ?'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        notifications = cursor.fetchall()
        return [dict(n) for n in notifications]
    except sqlite3.Error as e:
        logging.error(f"Failed to retrieve pending email notifications: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_pending_calendar_events(limit=10):
    """Retrieves pending calendar events."""
    sql = '''SELECT * FROM calendar_events WHERE status = 'pending' LIMIT ?'''
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        events = cursor.fetchall()
        return [dict(e) for e in events]
    except sqlite3.Error as e:
        logging.error(f"Failed to retrieve pending calendar events: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Initialize the database when the module is loaded
initialize_database() 