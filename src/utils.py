
from datetime import datetime, timedelta

def get_time_filter():

    while True:
        try:
            time_filter = int(input("Enter the time period of the data you would like to view:\n1. Day"
            "\n2. 7 days\n3. 14 days\n4. 30 days\n5. 60 days\nEnter your choice: "))
            if 5 >= time_filter >= 1:
                break
            else:
                print("Invalid option. Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")

    curr_time = datetime.now()
    if time_filter == 1:
        return curr_time - timedelta(days=1)
    elif time_filter == 2:
        return curr_time - timedelta(days=7)
    elif time_filter == 3:
        return curr_time - timedelta(days=14)
    elif time_filter == 4:
        return curr_time - timedelta(days=30)
    elif time_filter == 5:
        return curr_time - timedelta(days=60)


def filter_blood_sugar_data(data):
    '''
    Filters blood sugar data based on a time range given by the user.
    :param data: Blood sugar data table
    :return: Filtered data table
    '''

    try:
        start_date = get_time_filter()
        end_date = datetime.now()

        filtered_data = data[
            (data['timestamp'] >= start_date) &
            (data['timestamp'] <= end_date)
            ]


        if filtered_data.empty:
            print("No blood sugar data available for the selected time range.")
            return None
        return filtered_data
    except Exception as e:
        print("Error filtering blood sugar data: ", e)
        return None
