import time
import psutil
import platform

from psutil import AccessDenied, NoSuchProcess


class Metrics:
    def __init__(self):
        super().__init__()
        psutil.cpu_percent()

    def get_sysinfo(self):
        uptime = int(time.time() - psutil.boot_time())
        sysinfo = {
            'uptime': uptime,
            'os': platform.platform(),
            'cpu_count': psutil.cpu_count(),
        }

        return sysinfo

    def get_memory(self):
        return psutil.virtual_memory()._asdict()

    def get_swap_memory(self):
        return psutil.swap_memory()._asdict()

    def get_cpu(self):
        return psutil.cpu_times_percent(0.1)._asdict()

    def get_cpu_cores(self):
        return [c._asdict() for c in psutil.cpu_times_percent(0.1, percpu=True)]

    def get_disks(self, all_partitions: bool = False):
        disks = []
        for dp in psutil.disk_partitions(all_partitions):
            usage = psutil.disk_usage(dp.mountpoint)
            disk = {
                'device': dp.device,
                'mount_point': dp.mountpoint,
                'type': dp.fstype,
                'options': dp.opts,
                'space_total': usage.total,
                'space_used': usage.used,
                'space_used_percent': usage.percent,
                'space_free': usage.free
            }
            disks.append(disk)
        return disks

    def get_disk_counters(self, perdisk: bool = True):
        return dict((dev, c._asdict()) for dev, c in psutil.disk_io_counters(perdisk).items())

    def get_users(self):
        return [u._asdict() for u in psutil.users()]

    def get_process_list(self):
        process_list = []
        for p in psutil.process_iter():
            if p.is_running():
                p.cpu_percent(interval=None)
                mem = p.memory_info()

                try:
                    username = p.username()
                except AccessDenied:
                    username = None

                proc = {
                    'pid': p.pid,
                    'name': p.name(),
                    'user': username,
                    'status': p.status(),
                    'created': p.create_time(),
                    'mem_rss': mem.rss,
                    'mem_vms': mem.vms,
                    'mem_percent': p.memory_percent(),
                    'cpu_percent': p.cpu_percent()
                }
                process_list.append(proc)
        return process_list