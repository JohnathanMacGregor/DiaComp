import sqlite3
from datetime import datetime
from database import find_closest_blood_sugar_log, execute_query

DB_FILE = 'blood_sugar_data.db'

def log_insulin_dose():
    '''
    Logs insulin does entry into the database. User provides details such as timestampe, dosage amount,
    dosage type, and optionally links it to a related blood sugar log.
    '''


    timestamp = input("Enter the time (YYYY-MM-DD HH:SS) or leave blank for current dosage: ")
    if not timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        try:
            datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')  # Validate format
        except ValueError:
            print("Invalid timestamp format. Please use 'YYYY-MM-DD HH:MM:SS'.")
            return

    try:
        dosage_amount = float(input("Enter the insulin dosage amount in units: "))
    except ValueError:
        print("Invalid input for dosage amount. Please enter a valid number.")
        return


    dosage_type = input("Enter the insulin dosage type\n(e.g., rapid-acting or long-acting insulin): ")
    entry_type = input("Enter the type of entry (e.g., Correction, Meal, Snack, or Other): ")

    try:
        carbs = input("Enter the amount of carbs or leave blank if not applicable: ")
        if carbs:
            carbs = float(carbs)
        else:
            carbs = None
    except ValueError:
        print("Invalid input for carbs. Please enter a valid number.")
        return

    # Finds the closest blood sugar log
    closest_log = find_closest_blood_sugar_log(timestamp)
    if closest_log:
        related_log_id, related_log_time, related_glucose = closest_log
        print(f"Linking to the closest blood sugar log: ID {related_log_id}, "
              f"Time: {related_log_time}, Glucose: {related_glucose} mmol/L.")
    else:
        print("No blood sugar logs found. Proceeding without linking.")
        related_log_id = None



    query = ("""
    INSERT INTO insulin_doses (timestamp, dosage_amount, dosage_type,entry_type,carbs, related_log_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """)

    execute_query(query, (timestamp, dosage_amount, dosage_type, entry_type, carbs, related_log_id))
    print(f"Insulin dosage logged: {dosage_amount} units ({dosage_type}) at {timestamp}.")


if __name__ == "__main__":
    log_insulin_dose()