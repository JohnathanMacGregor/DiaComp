# api.py
import requests
from config import LOGIN_ENDPOINT, HEADERS,CONNECTIONS_ENDPOINT,CGM_DATA_ENDPOINT


def login(email, password):
    """
    Logs into the API and retrieves a JWT token.

    :param email: User's LibreLinkUp email.
    :param password: User's LibreLinkUp password.
    :returns: JWT token
    """
    payload = {"email": email, "password": password}


    try:
        # Sending login request
        response = requests.post(LOGIN_ENDPOINT, json=payload, headers=HEADERS)
        response.raise_for_status()
        token = response.json()["data"]["authTicket"]["token"]
        return token
    except requests.exceptions.RequestException as e:
        raise Exception(f"Login failed. Error: {str(e)}") from e
    except KeyError:
        raise Exception("Missing token in response.")

def get_patient_id(token):
    """
    Get the patient ID associated with the user.

    :param token: JWT token.
    :returns: Patient ID.
    """
    headers = {**HEADERS, 'authorization': f'Bearer {token}'}

    try:

        response = requests.get(CONNECTIONS_ENDPOINT, headers=headers)
        response.raise_for_status()
        connections = response.json()["data"]
        if not connections:
            raise Exception("No connections found!")

        patient_id = connections[0]["patientId"]
        return patient_id

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch connections. Error: {str(e)}") from e
    except KeyError:
        raise Exception("Missing patient ID.")


def get_cgm_data(token, patient_id):
    """
    Fetches CGM data for the specified patient ID.

    :param token: JWT token.
    :param patient_id: Patient ID.
    :returns: a dictionary containing CGM data.
    """
    url = CGM_DATA_ENDPOINT.format(patientId=patient_id)
    headers = {**HEADERS, 'authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get CGM data. Error: {str(e)}") from e
    except KeyError:
        raise Exception("Missing CGM data.")