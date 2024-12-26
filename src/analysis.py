from dotenv import load_dotenv
import os




load_dotenv(dotenv_path='../login_example.env')

def retrieve_value(data,key):
    """
    Retrieve a value from a dictionary.

    :param data: Dictionary containing the data to retrieve
    :param key: Key to retrieve from the dictionary
    :return: Value corresponding to the provided key.
    """
    try:
        return data[key]
    except KeyError:
        raise KeyError(f"Key '{key}' not found in the provided data.")

def is_low_blood_sugar(glucose_data):
    '''
    Checks if the blood sugar level is below the low threshold.

    :param glucose_data: Dictionary containing glucose information.
    :return: Boolean indicating if the blood sugar level is low.
    '''
    try:

        blood_sugar = retrieve_value(glucose_data,'Value')
        low_threshold = float(os.getenv('LOW_THRESHOLD'))
        return blood_sugar < low_threshold
    except (TypeError, ValueError) as e:
        raise ValueError("Error determining low blood sugar: ", e)

def is_high_blood_sugar(glucose_data):
    '''
    Checks if the blood sugar level is above the high threshold.

    :param glucose_data: Dictionary containing glucose information.
    :return: Boolean indicating if the blood sugar level is high.
    '''

    try:
        blood_sugar = retrieve_value(glucose_data, 'Value')
        high_threshold = float(os.getenv('HIGH_THRESHOLD'))
        return blood_sugar > high_threshold
    except (TypeError, ValueError) as e:
        raise ValueError("Error determining high blood sugar: ", e)



def is_extremely_low(glucose_data):
    '''
    Checks if the blood sugar level is below the extremely low threshold.

    :param glucose_data: Dictionary containing glucose information.
    :return: Boolean indicating if the blood sugar level is extremely low.
    '''

    try:
        blood_sugar = retrieve_value(glucose_data, 'Value')
        extremely_low_threshold = float(os.getenv('EXTREMELY_LOW_THRESHOLD'))
        return blood_sugar < extremely_low_threshold
    except (TypeError, ValueError) as e :
        raise ValueError("Error determining extremely low blood sugar: ",e)

def is_extremely_high(glucose_data):
    '''
    Checks if the blood sugar level is below the extremely low threshold.

    :param glucose_data: Dictionary containing glucose information.
    :return: Boolean indicating if the blood sugar level is extremely high.
    '''

    try:
        blood_sugar = retrieve_value(glucose_data,'Value')
        extremely_high_threshold = float(os.getenv('EXTREMELY_HIGH_THRESHOLD'))
        return blood_sugar > extremely_high_threshold
    except (TypeError, ValueError) as e:
        raise ValueError("Error determining extremely high blood sugar: ", e)

def is_normal_level(glucose_data):
    """
    Determines if the blood sugar level is within normal range.

    :param glucose_data: Dictionary containing glucose information.
    :return: Boolen indicating if blood sugar level is normal
    """
    try:
        blood_sugar = retrieve_value(glucose_data,'Value')
        low_threshold = float(os.getenv('LOW_THRESHOLD'))
        high_threshold = float(os.getenv('HIGH_THRESHOLD'))
        return low_threshold <= blood_sugar <= high_threshold
    except (TypeError, ValueError) as e:
        raise ValueError("Error determining normal blood sugar level: ", e)
