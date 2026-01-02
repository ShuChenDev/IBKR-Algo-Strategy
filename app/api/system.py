import requests


BASE_URL = "http://127.0.0.1:8000/system"
DEFAULT_TIMEOUT = (3.05, 10)


def get_system_health() -> bool:
    url = f"{BASE_URL}/status"
    r = requests.get(url, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())
