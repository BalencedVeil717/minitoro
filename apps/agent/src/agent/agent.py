# Target : CPU : 40% | RAM : 2.1/4GB | DISK : 60% full
import time

while True:
    import psutil

    cpu = psutil.cpu_percent(0.1)

    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024 ** 3), 1)
    ram_used = round(ram.used / (1024 ** 3), 1)

    disk = round(psutil.disk_usage('/').percent)

    print(f"CPU : {cpu}% | RAM : {ram_used}/{ram_total}GB | Disk : {disk}% full")

    time.sleep(60)
