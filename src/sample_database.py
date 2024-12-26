import sqlite3
import os
from datetime import datetime, timedelta
import random
# Specify the SQLite database file
DB_FILE = "../data/sample_blood_sugar_data.db"

def create_sample_database():
    # Delete the old database if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Deleted old database: {DB_FILE}")

    # Create a new database connection
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_sugar_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        glucose_value REAL NOT NULL,
        alert_type TEXT,
        log_type TEXT,
        notes TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS insulin_doses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        dosage_amount REAL NOT NULL,
        dosage_type TEXT,
        entry_type TEXT,
        carbs REAL,
        related_log_id INTEGER,
        FOREIGN KEY(related_log_id) REFERENCES blood_sugar_log(id)
    )
    """)

    # Insert sample data into blood_sugar_log
    start_time = datetime.now() - timedelta(days=7)  # Start from 7 days ago
    # Insert sample data into blood_sugar_log
    for i in range(50):  # Add 50 entries
        # Generate a random glucose value with some variability
        base_value = random.uniform(4.0, 7.0)  # Normal range as the base
        fluctuation = random.uniform(-2.0, 3.0)  # Possible fluctuations
        glucose_value = round(base_value + fluctuation, 1)

        # Ensure values stay within a realistic range
        glucose_value = max(2.0, min(glucose_value, 15.0))

        timestamp = (start_time + timedelta(minutes=i * 120)).strftime('%m/%d/%Y %I:%M:%S %p')
        alert_type = "High" if glucose_value > 9.0 else "Low" if glucose_value < 3.9 else None
        log_type = "Manual" if i % 2 == 0 else "Automatic"
        notes = "Sample note" if i % 5 == 0 else None

        cur.execute("""
        INSERT INTO blood_sugar_log (timestamp, glucose_value, alert_type, log_type, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (timestamp, glucose_value, alert_type, log_type, notes))

    # Insert sample data into insulin_doses
    for i in range(20):  # Add 20 entries
        timestamp = (start_time + timedelta(minutes=i * 360)).strftime('%m/%d/%Y %I:%M:%S %p')
        dosage_amount = round(5 + (i % 5) * 2, 1)
        dosage_type = "Bolus" if i % 2 == 0 else "Basal"
        entry_type = "Manual"
        carbs = round(15 + i * 2, 1)
        cur.execute("""
        INSERT INTO insulin_doses (timestamp, dosage_amount, dosage_type, entry_type, carbs)
        VALUES (?, ?, ?, ?, ?)
        """, (timestamp, dosage_amount, dosage_type, entry_type, carbs))

    # Commit changes and close the connection
    con.commit()
    con.close()
    print(f"Sample database '{DB_FILE}' created successfully with updated timestamps.")

if __name__ == "__main__":
    create_sample_database()
