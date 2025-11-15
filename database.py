import sqlite3
def init_db():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT,
                 role TEXT)""")
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  ("admin", "admin123", "admin"))
    conn.commit()
    conn.close()
