import sqlite3

def setup_database():
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id TEXT PRIMARY KEY,
            birthday TEXT
        )
    ''')
    conn.commit()
    conn.close()

def set_birthday(user_id, date):
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO birthdays (user_id, birthday)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET birthday = excluded.birthday
    ''', (user_id, date))
    conn.commit()
    conn.close()

def get_birthday(user_id):
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('SELECT birthday FROM birthdays WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def list_birthdays():
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('SELECT user_id, birthday FROM birthdays')
    results = c.fetchall()
    conn.close()
    return results
