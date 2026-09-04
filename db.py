import sqlite3
import json
import os

DB_FILE = "campusos.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ১. Schedules টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
        id TEXT PRIMARY KEY, course TEXT, title TEXT, day TEXT,
        start_time TEXT, end_time TEXT, room TEXT, instructor TEXT, section TEXT
    )''')

    # ২. Rooms টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
        id TEXT PRIMARY KEY, room_number TEXT, type TEXT, capacity INTEGER,
        equipment TEXT, floor INTEGER, status TEXT, bookings TEXT
    )''')

    # ৩. Events টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY, name TEXT, description TEXT, date TEXT,
        start_time TEXT, end_time TEXT, end_date TEXT, venue TEXT,
        organizer TEXT, capacity INTEGER, registered INTEGER, registrations TEXT, status TEXT
    )''')

    # ৪. Announcements টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id TEXT PRIMARY KEY, title TEXT, body TEXT, date TEXT,
        priority TEXT, posted_by TEXT, expires TEXT
    )''')

    # ৫. Assignments টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id TEXT PRIMARY KEY, course TEXT, course_title TEXT, title TEXT,
        description TEXT, assigned_date TEXT, deadline TEXT,
        submission_platform TEXT, status TEXT, marks INTEGER
    )''')
    conn.commit()

    # সিড ডাটা লোড করা (JSON থেকে SQLite-এ)
    cursor.execute("SELECT COUNT(*) FROM schedules")
    if cursor.fetchone()[0] == 0 and os.path.exists("data/schedules.json"):
        with open("data/schedules.json") as f:
            for r in json.load(f):
                cursor.execute("INSERT OR IGNORE INTO schedules VALUES (?,?,?,?,?,?,?,?,?)",
                               (r["id"], r["course"], r["title"], r["day"], r["start_time"], r["end_time"], r["room"], r["instructor"], r.get("section", "")))

    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0 and os.path.exists("data/rooms.json"):
        with open("data/rooms.json") as f:
            for r in json.load(f):
                cursor.execute("INSERT OR IGNORE INTO rooms VALUES (?,?,?,?,?,?,?,?)",
                               (r["id"], r["room_number"], r["type"], r["capacity"], json.dumps(r.get("equipment", [])), r["floor"], r["status"], json.dumps(r.get("bookings", []))))

    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0 and os.path.exists("data/events.json"):
        with open("data/events.json") as f:
            for r in json.load(f):
                cursor.execute("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               (r["id"], r["name"], r["description"], r["date"], r["start_time"], r["end_time"], r.get("end_date", ""), r["venue"], r["organizer"], r["capacity"], r["registered"], json.dumps(r.get("registrations", [])), r["status"]))

    cursor.execute("SELECT COUNT(*) FROM announcements")
    if cursor.fetchone()[0] == 0 and os.path.exists("data/announcements.json"):
        with open("data/announcements.json") as f:
            for r in json.load(f):
                cursor.execute("INSERT OR IGNORE INTO announcements VALUES (?,?,?,?,?,?,?)",
                               (r["id"], r["title"], r["body"], r["date"], r["priority"], r["posted_by"], r["expires"]))

    cursor.execute("SELECT COUNT(*) FROM assignments")
    if cursor.fetchone()[0] == 0 and os.path.exists("data/assignments.json"):
        with open("data/assignments.json") as f:
            for r in json.load(f):
                cursor.execute("INSERT OR IGNORE INTO assignments VALUES (?,?,?,?,?,?,?,?,?,?)",
                               (r["id"], r["course"], r["course_title"], r["title"], r["description"], r["assigned_date"], r["deadline"], r["submission_platform"], r["status"], r["marks"]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")