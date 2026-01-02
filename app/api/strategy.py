import requests

BASE_URL = "http://127.0.0.1:8000/strategy"


def register_strategy(strategy_id: str, name: str, cash: float):
    payload = {
        "strategyID": strategy_id,
        "name": name,
        "cash": cash
    }
    url = f"{BASE_URL}/register"
    r = requests.post(url, json=payload)
    return (r.status_code, r.json())


def unregister_strategy(strategy_id: str):
    url = f"{BASE_URL}/{strategy_id}"
    r = requests.delete(url, timeout=5)

    return (r.status_code, r.json())


def get_strategy_info(strategy_id: str):
    url = f"{BASE_URL}/{strategy_id}"
    r = requests.get(url)

    return (r.status_code, r.json())