"""Read-only operating-system monitoring and explainable anomaly detection."""
from collections import deque
import math
import os
import platform
import socket
import statistics
import threading
import time

import psutil


class LinuxMonitor:
    def __init__(self, store, interval=5):
        self.store = store
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        self.latest = None
        self.baseline = deque(maxlen=60)
        self._previous_network = psutil.net_io_counters()
        self._previous_time = time.monotonic()
        self._cpu_strikes = 0
        self._memory_strikes = 0
        psutil.cpu_percent(interval=None)  # Prime the first non-blocking reading.

    @staticmethod
    def anomaly_threshold(values):
        """Use a learned ceiling without claiming the value is ML malware detection."""
        if len(values) < 8:
            return 85.0
        return min(95.0, max(70.0, statistics.mean(values) + 2 * statistics.pstdev(values)))

    @staticmethod
    def health_score(cpu, memory, disk):
        penalty = max(0, cpu - 50) * .27 + max(0, memory - 60) * .35 + max(0, disk - 65) * .45
        return max(0, min(100, round(100 - penalty)))

    def collect_once(self):
        cpu = round(psutil.cpu_percent(interval=None), 1)
        memory = round(psutil.virtual_memory().percent, 1)
        disk = round(psutil.disk_usage('/').percent, 1)
        now = time.monotonic()
        net = psutil.net_io_counters()
        elapsed = max(.1, now - self._previous_time)
        rx = max(0, net.bytes_recv - self._previous_network.bytes_recv) / elapsed / 1024
        tx = max(0, net.bytes_sent - self._previous_network.bytes_sent) / elapsed / 1024
        self._previous_time, self._previous_network = now, net
        threshold = self.anomaly_threshold(self.baseline)
        self._cpu_strikes = self._cpu_strikes + 1 if cpu >= threshold else 0
        self._memory_strikes = self._memory_strikes + 1 if memory >= 90 else 0
        anomaly = self._cpu_strikes >= 3 or self._memory_strikes >= 2 or disk >= 90
        sample = dict(ts=int(time.time()), cpu=cpu, memory=memory, disk=disk,
                      rx_kbs=round(rx, 1), tx_kbs=round(tx, 1), anomaly=anomaly)
        self.store.add_sample(sample)
        if self._cpu_strikes >= 3:
            self.store.add_alert('warning', 'Sustained CPU spike',
                                 f'CPU {cpu}% across 3 samples; baseline ceiling {threshold:.1f}%.',
                                 'performance', 'cpu-high')
        if self._memory_strikes >= 2:
            self.store.add_alert('warning', 'High memory pressure',
                                 f'RAM utilization reached {memory}%.', 'performance', 'memory-high')
        if disk >= 90:
            self.store.add_alert('critical', 'Disk almost full',
                                 f'Root filesystem usage reached {disk}%.', 'performance', 'disk-high')
        if not anomaly:
            self.baseline.append(cpu)
        with self._lock:
            self.latest = sample
        return sample

    def get_latest(self):
        with self._lock:
            return dict(self.latest) if self.latest else None

    def start(self):
        if self._thread:
            return
        def run():
            while not self._stop.is_set():
                try:
                    self.collect_once()
                except Exception as error:
                    print('Monitoring sample skipped:', error)
                self._stop.wait(self.interval)
        self._thread = threading.Thread(target=run, daemon=True, name='linuxguard-monitor')
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)


def processes(limit=8):
    rows = []
    for process in psutil.process_iter(['pid', 'name', 'memory_percent', 'username']):
        try:
            info = process.info
            rows.append({
                'pid': int(info['pid']),
                'name': str(info['name'] or 'unknown')[:100],
                'cpu': round(process.cpu_percent(interval=None), 1),
                'memory': round(float(info['memory_percent'] or 0), 1),
                # Indicators, not verdicts; never mark a process as malware.
                'indicator': 'high resource use' if float(info['memory_percent'] or 0) > 20 else '',
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            continue
    return sorted(rows, key=lambda p: (p['cpu'], p['memory']), reverse=True)[:limit]


def recommendations(sample):
    if not sample:
        return ['Collecting the first telemetry sample.']
    items = []
    if sample['cpu'] >= 85:
        items.append('Inspect top processes with top or htop; do not kill unknown services without checking them.')
    if sample['memory'] >= 90:
        items.append('Review RAM consumers and swap; check for application memory leaks.')
    if sample['disk'] >= 85:
        items.append('Use df -h and du to locate large files; verify backups before deleting anything.')
    if not items:
        items.append('Resource utilization is within the default thresholds. Continue observing trends.')
    return items


def system_info():
    boot = psutil.boot_time()
    return {
        'host': socket.gethostname(),
        'os': platform.platform(),
        'kernel': platform.release(),
        'uptime_seconds': max(0, int(time.time() - boot)),
        'cpu_cores': psutil.cpu_count(logical=True),
        'total_ram_gb': round(psutil.virtual_memory().total / 1024**3, 2),
        'is_linux': platform.system() == 'Linux',
    }
