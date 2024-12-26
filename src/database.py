import sqlite3
from sqlite3 import Error

DB_FILE = '../data/sample_blood_sugar_data.db'


def setup_connection(db_file):
    '''
    Create a database connection to the SQLite database specified by db_file.

    :param db_file: Path to the SQLite database.
    :return: Connection object on success, None on Failure to connect.
    '''
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print("Error: ", e)
    return None


def setup_database():
    '''
    Sets up the database by creating tables if they do not exist.

    '''
    conn = setup_connection(DB_FILE)
    if conn is None:
        print("Unable to connect to SQLite database.")
        return
    try:
        cur = conn.cursor()

        # Create the blood sugar log table
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

        # Create insulin doses table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS insulin_doses(
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

        conn.commit()  # Save changes
    except Error as e:
        print("Error during database setup: ", e)
    finally:
        conn.close()  # Close the connection



def execute_query(query, params = ()):
    '''
    Execute SQL query with optional parameters.
    :param query: SQL query string to execute.
    :param params: Tuple of parameters to pass to SQL query
    '''
    try:
        con = setup_connection(DB_FILE)
        cur = con.cursor()
        cur.execute(query, params)
        con.commit()
    except sqlite3.Error as e:
        print("Database query error: ",e)
    finally:
        con.close()


def fetch_all_data(query, params = ()):
    '''
    Retrieves all results for a given SQL query with optional parameters.

    :param query: SQL query string to execute.
    :param params: Tuple of parameters to pass to SQL query
    :return: List of tuples containing query result.
    '''
    try:
        con = setup_connection(DB_FILE)
        cur = con.cursor()
        cur.execute(query, params).fetchall()

    except sqlite3.Error as e:
        print("Error fetching data from database: ", e)
        return []
    finally:
        con.close()



def log_data(timestamp, glucose_value, alert_type=None, log_type=None,notes=None):
    '''
    Logs blood sugar measurements into the database.

    :param timestamp: Time of the log entry.
    :param glucose_value: Blood glucose in mmol/L
    :param alert_type: Type of alert (e.g., High, Low, null)
    :param log_type: Type of log (e.g., Reading, Alert)
    :param notes: Additional notes for the log entry.
    '''
    query = ("""
    INSERT INTO blood_sugar_log(timestamp, glucose_value, alert_type,log_type ,notes)
    VALUES (?,?,?,?,?)
    """)

    execute_query(query, (timestamp, glucose_value, alert_type,log_type, notes))

    print("Logged data:",timestamp,glucose_value,alert_type,log_type,notes)

def find_closest_blood_sugar_log(timestamp):
    '''
    Finds the closest blood sugar log entry to the given timestamp.

    :param timestamp: Time to find the closest log entry to.
    :return: Tuple of the closest log entry or None if no log entry exists.
    '''
    query = ("""
    SELECT id, timestamp, glucose_value
    FROM blood_sugar_log
    ORDER BY ABS(strftime('%s',timestamp) - strftime('%s',?)) ASC
    LIMIT 1;
    """)
    result = fetch_all_data(query,(timestamp,))
    if result is None:
        return result[0]


def fetch_insulin_doses():
    """
    Fetches all insulin dose records from the database.

    :return: List of tuples holding insulin dose records.
    """
    query = "SELECT * FROM insulin_doses ORDER BY timestamp"
    return fetch_all_data(query)


def fetch_blood_sugar_logs():
    """
    Fetches all blood sugar log records from the database.

    :return: List of tuples holding blood sugar log records.
    """
    query = "SELECT * FROM blood_sugar_log ORDER BY timestamp"
    return fetch_all_data(query)



if __name__ == "__main__":
    setup_database()