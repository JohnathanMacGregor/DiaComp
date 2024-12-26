from api import login, get_patient_id, get_cgm_data
from dotenv import load_dotenv
from analysis import is_low_blood_sugar, is_high_blood_sugar, is_extremely_low, is_extremely_high, is_normal_level
from send_sms import send_sms
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
import time
from datetime import datetime, timedelta
import os
from database import log_data


# Global variables for tracking alert timing
last_low_alert_time= None
last_high_alert_time = None
last_extreme_low_alert_time = None
last_extreme_high_alert_time = None


def send_alert(condition, user_name, timestamp, blood_sugar, suggested_action):
    """
    Send an SMS alert for a specific condition.

    :param condition: Description of the blood sugar (e.g., "low or high")
    :param user_name: Name of the user being monitored
    :param timestamp: Time of blood sugar reading.
    :param blood_sugar: Blood sugar reading value.
    :param suggested_action: Recommended action to be taken.
    """
    try:
        msg = (
            f"Time: {timestamp}\n"
            f"Alert! {user_name}'s blood glucose is {condition}! Glucose Reading: {blood_sugar}\n"
            f"Suggested Action: {suggested_action}"
        )
        send_sms(msg)
    except Exception as e:
        print("Failed to send SMS alert: ", e)


def monitor_blood_sugar():
    """
    Monitor blood sugar levels and send alerts based on conditions.
    """
    global last_low_alert_time, last_high_alert_time, last_extreme_low_alert_time, \
        last_extreme_high_alert_time, last_extreme_low_alert_time

    # Load environment variables
    load_dotenv(dotenv_path='../login.env')
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    user_name = os.getenv('USER_NAME')

    try:
        # Login and get token
        token = login(email, password)

        # Get connections and retrieve patient ID
        patient_id = get_patient_id(token)


        # Get CGM data
        cgm_data = get_cgm_data(token, patient_id)
        latest_measurement = cgm_data["connection"]["glucoseMeasurement"]

        timestamp = latest_measurement["Timestamp"]
        blood_sugar = latest_measurement["Value"]

        # Handling extreme lows
        if is_extremely_low(latest_measurement):
            if last_extreme_low_alert_time is None or datetime.now() > last_extreme_low_alert_time + timedelta(minutes= 7):
                send_alert(
                    "EXTREMELY low",
                    user_name,
                    timestamp,
                    blood_sugar,
                    "Take immediate action! Drink juice and check again in 15 minutes.",
                )
                log_data(timestamp, blood_sugar, alert_type="EXTREMELY low", log_type="alert")
                last_extreme_low_alert_time = datetime.now()


        # Handling extreme highs
        if is_extremely_high(latest_measurement):
            if last_extreme_high_alert_time is None or datetime.now() > last_extreme_high_alert_time + timedelta(minutes= 30):
                send_alert(
                    "EXTREMELY high",
                    user_name,
                    timestamp,
                    blood_sugar,
                    "Take immediate corrective dosage and monitor closely.",
                )
                log_data(timestamp, blood_sugar, alert_type="EXTREMELY high", log_type="alert")
                last_extreme_high_alert_time = datetime.now()

        # Handle lows
        if is_low_blood_sugar(latest_measurement):
            if last_low_alert_time is None or datetime.now() > last_low_alert_time + timedelta(minutes=15):
                send_alert(
                    "low",
                    user_name,
                    timestamp,
                    blood_sugar,
                    "Drink juice and check blood sugar again in 15 minutes.",
                )
                log_data(timestamp, blood_sugar, alert_type="Low", log_type="alert")
                last_low_alert_time = datetime.now()

        # Handle highs
        if is_high_blood_sugar(latest_measurement):
            if last_high_alert_time is None or datetime.now() > last_high_alert_time + timedelta(minutes=30):
                send_alert(
                    "high",
                    user_name,
                    timestamp,
                    blood_sugar,
                    "Take a corrective dosage and monitor closely.",
                )
                log_data(timestamp, blood_sugar, alert_type="High", log_type="alert")
                last_high_alert_time = datetime.now()

        if is_normal_level(latest_measurement):
            last_low_alert_time = None
            last_high_alert_time = None
            last_extreme_low_alert_time = None
            last_extreme_high_alert_time = None
            log_data(timestamp, blood_sugar, log_type="Reading")

    except Exception as e:
        print("Error monitoring blood sugar: ", e)

def main():
    """
    Function to start the blood sugar monitoring scheduler.
    """

    scheduler = BackgroundScheduler()
    #Monitor_blood_sugar every 5 minutes
    scheduler.add_job(monitor_blood_sugar, 'interval',
                      minutes = int(os.getenv("MONITOR_INTERVAL",5))
                      )

    print("Scheduler started. Monitoring blood sugar levels...")
    scheduler.start()

    try:
        while True:
            time.sleep(1) # Keeps program running continously
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    main()
