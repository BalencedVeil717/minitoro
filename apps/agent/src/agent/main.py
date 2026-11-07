# Target : CPU : 40% | RAM : 2.1/4GB | DISK : 60% full
import json
import psutil


def generate_data():
    cpu = psutil.cpu_percent(1)

    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024 ** 3), 1)
    ram_used = round(ram.used / (1024 ** 3), 1)

    disk = round(psutil.disk_usage('/').percent)

    print(f"CPU : {cpu}% | RAM : {ram_used}/{ram_total}GB | Disk : {disk}% full")

    data = {
        'cpu_percentage': cpu,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'disk_percentage': disk,
    }
    return json.dumps(data)

