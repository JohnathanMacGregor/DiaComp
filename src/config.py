# config.py

# Base API URL
BASE_URL = "https://api.libreview.io"

# Endpoints
LOGIN_ENDPOINT = f"{BASE_URL}/llu/auth/login"
CONNECTIONS_ENDPOINT = f"{BASE_URL}/llu/connections"
CGM_DATA_ENDPOINT = f"{BASE_URL}/llu/connections/{{patientId}}/graph"

# Headers
HEADERS = {
    'accept-encoding': 'gzip',
    'cache-control': 'no-cache',
    'connection': 'Keep-Alive',
    'content-type': 'application/json',
    'product': 'llu.android',
    'version': '4.7.0',
}
