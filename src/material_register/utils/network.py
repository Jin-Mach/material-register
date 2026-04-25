import requests

def is_internet_available(timeout: int = 3) -> bool:
    try:
        return requests.head("https://www.google.com", timeout=timeout).ok
    except requests.RequestException as e:
        print(e)
        return False