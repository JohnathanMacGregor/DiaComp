
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # Use this before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, num2date
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os
from utils import get_time_filter
import mplcursors


load_dotenv(dotenv_path='../login_example.env')

DB_FILE = '../data/sample_blood_sugar_data.db'

#Constants for threshold values
LOW_THRESHOLD = float(os.getenv('LOW_THRESHOLD'))
HIGH_THRESHOLD = float(os.getenv('HIGH_THRESHOLD'))
def get_blood_sugar_data():
    '''
    Gets blood sugar and timestamp based on a time range given by the user.

    :return: A pandas dataframe with blood sugar data.
    '''
    try:
        con = sqlite3.connect(DB_FILE)
        blood_sugar_query = "SELECT timestamp, glucose_value FROM blood_sugar_log ORDER BY timestamp;"
        blood_sugar_data = pd.read_sql_query(blood_sugar_query, con)
        con.close()

        # Parse timestamps with a specific format
        blood_sugar_data['timestamp'] = pd.to_datetime(
            blood_sugar_data['timestamp'],
            format='%m/%d/%Y %I:%M:%S %p',  # Replace with your actual timestamp format
            errors='coerce'
        )
        blood_sugar_data.dropna(subset=['timestamp'], inplace=True)



        start_date = get_time_filter()
        end_date = datetime.now()
        filtered_data = blood_sugar_data[
            (blood_sugar_data['timestamp'] >= start_date) &
            (blood_sugar_data['timestamp'] <= end_date)
            ]
        return filtered_data

    except Exception as e:
        print(f"Error fetching or filtering blood sugar data: {e}")
        return pd.DataFrame(columns=['timestamp', 'glucose_value'])  # Return an empty DataFrame on error




def set_textbox_color(sel):
    """
    Changes the colour of the text box based on glucose level.

    :param sel: The mplcursors selection object containing target data points.
    """
    try:
        # Retrieve thresholds
        LOW_THRESHOLD = 3.9
        HIGH_THRESHOLD = 9.0

        glucose_value = sel.target[1]  # Glucose level

        # Determine the annotation color
        if glucose_value < LOW_THRESHOLD:
            colour = 'red'  # Low glucose
        elif glucose_value > HIGH_THRESHOLD:
            colour = 'orange'  # High glucose
        else:
            colour = 'green'  # Normal range

        # Set the annotation text
        sel.annotation.set_text(
            f"Time: {num2date(sel.target[0]).strftime('%m/%d %H:%M')}\nGlucose: {glucose_value:.1f} mmol/L"
        )

        # Customize the annotation background
        bbox = sel.annotation.get_bbox_patch()
        bbox.set_facecolor(colour)
        bbox.set_alpha(0.8)

    except AttributeError as e:
        print(f"Annotation error: {e}")

def plot_blood_sugar_data(blood_sugar_data):
    '''
    Plots blood sugar data with a green shaded region for the target range and markers for highs and lows.

    :param blood_sugar_data: Blood sugar data table.
    '''
    global LOW_THRESHOLD, HIGH_THRESHOLD

    if blood_sugar_data.empty:
        print("No data available.")
        return

    try:
        # Parse timestamps
        blood_sugar_data['timestamp'] = pd.to_datetime(blood_sugar_data['timestamp'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

        # Drops invalid timestamps
        blood_sugar_data = blood_sugar_data.dropna(subset=['timestamp'])
        blood_sugar_data = blood_sugar_data.sort_values(by='timestamp')

    except Exception as e:
        print("Error parsing timestamps: ", e)
        return



    # Initializing plot
    plt.figure(figsize=(12, 8))

    # Adding target range
    plt.axhspan(LOW_THRESHOLD, HIGH_THRESHOLD, color='green', alpha=0.1, label='Target Range')


    plt.plot(
        blood_sugar_data['timestamp'],
        blood_sugar_data['glucose_value'],
        label='Blood Sugar Level',
        color= 'black',
        linestyle= '-',
        )

    # Highlights highs and lows
    plt.scatter(blood_sugar_data['timestamp'][blood_sugar_data['glucose_value'] < LOW_THRESHOLD],
                blood_sugar_data['glucose_value'][blood_sugar_data['glucose_value'] < LOW_THRESHOLD],
                color='red',
                label='Low Blood Sugar',
                zorder=3)

    plt.scatter(blood_sugar_data['timestamp'][blood_sugar_data['glucose_value'] > HIGH_THRESHOLD],
                blood_sugar_data['glucose_value'][blood_sugar_data['glucose_value'] > HIGH_THRESHOLD],
                color='orange',
                label='High Blood Sugar',
                zorder = 3)

    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: set_textbox_color(sel))



    # Threshold lines
    plt.axhline(y=LOW_THRESHOLD, color='red', linestyle='--', label='Low Threshold (3.9 mmol/L)')
    plt.axhline(y=HIGH_THRESHOLD, color='orange', linestyle='--', label='High Threshold (9.0 mmol/L)')

    # Formats x-axis
    plt.gca().xaxis.set_major_formatter(DateFormatter('%m/%d %H:%M'))
    plt.xticks(rotation=45)

    plt.title("Blood Sugar Over Time")
    plt.xlabel("Time")
    plt.ylabel("Glucose Level (mmol/L)")
    plt.legend()
    plt.grid(True)


    plt.tight_layout()
    plt.show()



def generate_daily_summary(daily_summary_data):
    '''
    Generate a line graph of daily average glucose levels.

    :param daily_summary_data: Pandas datagrame containing date and average_glucose.
    '''
    if daily_summary_data.empty:
       print("No data available for daily summary plot.")
       return

    plt.figure(figsize=(12, 8))

    plt.plot(
       daily_summary_data['date'],
       daily_summary_data['average_glucose'],
       label='Average Blood Sugar', color='black',
       marker='o', linewidth=2)

    plt.gca().xaxis.set_major_formatter(DateFormatter('%m/%d'))
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)

    # Adds shaded green region for target range
    plt.axhspan(4.0, 9.0, color='green', alpha=0.1, label='Target Range')

    plt.axhline(y=3.9, color='red', linestyle='--', label='Low Threshold (3.9 mmol/L)')
    plt.axhline(y=9.0, color='orange', linestyle='--', label='High Threshold (9.0 mmol/L)')


    plt.title("Daily Average Glucose Levels", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Average Glucose Level (mmol/L)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)


    plt.tight_layout()
    plt.show()

def generate_daily_time_summary(daily_time_summary_data):
    '''
    Generate a bar graph of average glucose levels at different periods of the day.

    :param daily_time_summary_data: Pandas datagrame containing time_period and average_glucose.
    '''

    global LOW_THRESHOLD, HIGH_THRESHOLD
    if daily_time_summary_data.empty:
       print("No data available for daily time summary plot.")
       return


    plt.figure(figsize=(12, 8))

    plt.bar(
       daily_time_summary_data['time_period'],
       daily_time_summary_data['average_glucose'],
       label='Average Blood Sugar',
       color='blue'
    )

    plt.axhspan(4.0, 9.0, color='green', alpha=0.1, label='Target Range')

    plt.axhline(y=LOW_THRESHOLD, color='red', linestyle='--', label='Low Threshold (3.9 mmol/L)')
    plt.axhline(y=HIGH_THRESHOLD, color='orange', linestyle='--', label='High Threshold (9.0 mmol/L)')


    plt.title("Daily Average Glucose Levels", fontsize=16)
    plt.xlabel("Time Period", fontsize=12)
    plt.ylabel("Average Glucose Level (mmol/L)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    blood_sugar_data = get_blood_sugar_data()

    if blood_sugar_data.empty:
        print("No data available to plot after filtering.")
    else:
        plot_blood_sugar_data(blood_sugar_data)





