import sqlite3

# Create the database and table if it doesn't exist
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

# Call setup_database() when the bot starts
setup_database()
