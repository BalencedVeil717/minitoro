import time

import psutil
import requests
from requests import ConnectionError, Timeout


def generate_data():
    cpu = psutil.cpu_percent(1)

    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024 ** 3), 1)
    ram_used = round(ram.used / (1024 ** 3), 1)

    disk = round(psutil.disk_usage('/').percent)

    print(f"CPU : {cpu}% | RAM : {ram_used}/{ram_total}GB | Disk : {disk}% full")

    metric_data = {
        'cpu_percentage': cpu,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'disk_percentage': disk,
    }
    return metric_data


if __name__ == "__main__":
    while True:
        url = "http://127.0.0.1:8000/metrics"
        data = generate_data()

        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print(response.text)
            elif response.status_code in (422, 500):
                print("Error Occurred")
        except Timeout:
            print("Timeout Error Occurred")
        except ConnectionError:
            print("Connection Error Occurred")
        time.sleep(60)
