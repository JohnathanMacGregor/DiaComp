import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from data_visualization import get_time_filter
from dotenv import load_dotenv
import os
from data_visualization import generate_daily_summary, generate_daily_time_summary
from utils import filter_blood_sugar_data
DB_FILE = '../data/sample_blood_sugar_data.db'


load_dotenv(dotenv_path='../login_example.env')



def get_blood_sugar_data(db_file):
    """
    Gets blood sugar data and filters it based on a time range.
    :param db_file: Path to the database.
    :return: A pandas DataFrame containing blood sugar data.
    """
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    data_query = """SELECT * FROM blood_sugar_log ORDER BY timestamp"""
    data = pd.read_sql_query(data_query, con)


    data['timestamp'] = pd.to_datetime(data['timestamp'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    data = data.dropna(subset=['timestamp'])
    data = data.sort_values(by='timestamp')

    con.close()
    return data

def calculate_average_blood_sugar(blood_sugar_data):
    '''
    Calculates average blood sugar level.
    :param blood_sugar_data: Blood sugar data table
    :return: Average blood sugar level
    '''
    try:
        return blood_sugar_data['glucose_value'].mean()
    except KeyError as e:
        print("Error calculating average blood sugar: ", e)
        return None


def high_low_count(blood_sugar_data):
    '''
    Counts the number of high and low blood sugar events.
    :param blood_sugar_data: Blood sugar data table
    :return: Tuple containing number of high and low blood sugars.
    '''
    high_count = 0
    low_count = 0
    for index, row in blood_sugar_data.iterrows():
        if row['alert_type'] == 'High':
            high_count += 1

        if row['alert_type'] == 'Low':
            low_count += 1

    return high_count, low_count

def get_time_in_range(blood_sugar_data):
    '''
    Calculates the percentage of time the blood sugar levels are in the target range.

    :param blood_sugar_data: Blood sugar data table
    :return: Percentage of time in target range
    '''
    high_glucose = float(os.getenv('HIGH_THRESHOLD'))
    low_glucose = float(os.getenv('LOW_THRESHOLD'))


    glucose_in_range = blood_sugar_data[
        (blood_sugar_data['glucose_value'] >= low_glucose) &
        (blood_sugar_data['glucose_value'] <= high_glucose)]

    total_entries = len(blood_sugar_data)
    if total_entries == 0:
        return 0

    return round((len(glucose_in_range)/total_entries) * 100,2)

def categorize_time_of_day(timestamp):
    """
    Categorizes a timestamp into time-of-day periods (Morning, Afternoon, Evening, Night).

    :param timestamp: Timestamp to categorize
    :return: Time period as a string
    """

    hour = timestamp.hour  # Extract the hour from the timestamp
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Evening"
    else:
        return "Night"
def time_based_summary(blood_sugar_data):
    """
    Groups blood sugar data by time-of-day and calculates average glucose.

    :param blood_sugar_data: Blood sugar data table.
    :return: Data table with summary statistics.
    """
    # Add a time_period column
    blood_sugar_data = blood_sugar_data.copy()
    blood_sugar_data['time_period'] = blood_sugar_data['timestamp'].apply(categorize_time_of_day)

    summary = []
    for period, group in blood_sugar_data.groupby('time_period'):
        avg_glucose = calculate_average_blood_sugar(group)
        high_count, low_count = high_low_count(group)
        time_in_range = get_time_in_range(group)
        total_entries = len(group)
        summary.append({
            'time_period': period,
            'average_glucose': round(avg_glucose,2),
            'highs': high_count,
            'lows': low_count,
            'time_in_range': round(time_in_range,2),
            'total_entries': total_entries
        })
    return pd.DataFrame(summary)

def daily_summary(blood_sugar_data):
    blood_sugar_data = blood_sugar_data.copy()
    blood_sugar_data['date'] = blood_sugar_data['timestamp'].dt.date

    summary = []
    for date, group in blood_sugar_data.groupby('date'):
        avg_glucose = calculate_average_blood_sugar(group)
        high_count, low_count = high_low_count(group)
        time_in_range = get_time_in_range(group)
        total_entries = len(group)
        summary.append({
            'date': date,
            'average_glucose': round(avg_glucose, 2),
            'highs': high_count,
            'lows': low_count,
            'time_in_range': round(time_in_range, 2),
            'total_entries': total_entries
        })
    return pd.DataFrame(summary)

def display_main_menu():
    """Displays the main menu options."""
    print("\nAnalysis Menu\n")
    print("""
    1. Display Daily Summary (grouped by date, or time period)
    2. Display Average Glucose
    3. Display Amount of Highs 
    4. Display Amount of Lows
    5. Display Time in Range
    6. Exit
    """)


def display_daily_summary_menu(blood_sugar_data):
    '''
    Handles and displays daily summary based on user input.

    :param blood_sugar_data: Blood sugar data table.
    '''

    while True:
        print("""
        \nDaily Summary Options
        1. Group by Time Period
        2. Group by Date
        3. Back
        """)
        try:
            choice = int(input("Please enter your choice: "))
            if choice == 1:
                daily_stats = time_based_summary(blood_sugar_data)
                print("\nTime-Based Summary Statistics:")
                print(daily_stats.to_string(index=False))
                generate_daily_time_summary(daily_stats)
                exit()
            elif choice == 2:
                daily_stats = daily_summary(blood_sugar_data)
                print("\nDaily Summary Statistics (by Date):")
                print(daily_stats.to_string(index=False))
                generate_daily_summary(daily_stats)
                exit()

            elif choice == 3:
                print("Returning to main menu...")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def handle_user_choice(choice, blood_sugar_data):
    """
    Executes the appropriate action based on the user's choice.

    :param choice: User's selection.
    :param blood_sugar_data: Blood sugar data table
    :return: True if user opts to exit program, False otherwise
    """
    if choice == 1:
        display_daily_summary_menu(blood_sugar_data)
    elif choice == 2:
        avg_glucose = calculate_average_blood_sugar(blood_sugar_data)
        print(f"\nAverage Glucose Over Selected Time Period: {avg_glucose:.2f} mmol/L")
    elif choice == 3:
        high_count, _ = high_low_count(blood_sugar_data)
        print(f"\nHigh Count: {high_count}")
    elif choice == 4:
        _, low_count = high_low_count(blood_sugar_data)
        print(f"\nLow Count: {low_count}")
    elif choice == 5:
        time_in_range = get_time_in_range(blood_sugar_data)
        print(f"\nTime In Range: {time_in_range}%")
    elif choice == 6:
        print("Exiting program. Goodbye!")
        return True
    return False


def main():
    """Main function to handle the analysis menu."""
    blood_sugar_data = get_blood_sugar_data(DB_FILE)
    if blood_sugar_data is None or blood_sugar_data.empty:
        print("No blood sugar data available.")
        return

    filtered_data = filter_blood_sugar_data(blood_sugar_data)
    if filtered_data is None or filtered_data.empty:
        print("No data available for the selected time range.")
        return

    while True:
        display_main_menu()
        try:
            choice = int(input("Please enter your choice: "))
            if 1 <= choice <= 6:
                exit_program = handle_user_choice(choice, filtered_data)
                if exit_program:
                    break
            else:
                print("Invalid option. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


if __name__ == "__main__":
    main()
