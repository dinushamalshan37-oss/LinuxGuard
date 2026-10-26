"""SQLite persistence. Each operation uses its own connection for thread safety."""
import sqlite3
import time
from pathlib import Path


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL, cpu REAL NOT NULL, memory REAL NOT NULL,
                disk REAL NOT NULL, rx_kbs REAL NOT NULL, tx_kbs REAL NOT NULL,
                anomaly INTEGER NOT NULL DEFAULT 0)''')
            db.execute('''CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER NOT NULL,
                severity TEXT NOT NULL, title TEXT NOT NULL, detail TEXT NOT NULL,
                source TEXT NOT NULL, dedupe_key TEXT NOT NULL)''')

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA busy_timeout=5000')
        return db

    def add_sample(self, sample):
        with self._connect() as db:
            db.execute('''INSERT INTO samples (ts,cpu,memory,disk,rx_kbs,tx_kbs,anomaly)
                          VALUES (?,?,?,?,?,?,?)''',
                       (sample['ts'], sample['cpu'], sample['memory'], sample['disk'],
                        sample['rx_kbs'], sample['tx_kbs'], int(sample['anomaly'])))
            # Keep the latest 2,000 samples to cap storage.
            db.execute('DELETE FROM samples WHERE id < (SELECT COALESCE(MAX(id),0)-2000 FROM samples)')

    def samples(self, limit=60):
        limit = max(1, min(int(limit), 2000))
        with self._connect() as db:
            data = db.execute('SELECT * FROM samples ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [dict(item) for item in reversed(data)]

    def add_alert(self, severity, title, detail, source, dedupe_key, cooldown=300):
        now = int(time.time())
        with self._connect() as db:
            latest = db.execute('SELECT ts FROM alerts WHERE dedupe_key=? ORDER BY id DESC LIMIT 1',
                                (dedupe_key,)).fetchone()
            if latest is not None and now - latest['ts'] < cooldown:
                return False
            db.execute('''INSERT INTO alerts (ts,severity,title,detail,source,dedupe_key)
                          VALUES (?,?,?,?,?,?)''', (now, severity, title, detail, source, dedupe_key))
            db.execute('DELETE FROM alerts WHERE id < (SELECT COALESCE(MAX(id),0)-1000 FROM alerts)')
        return True

    def alerts(self, limit=20):
        limit = max(1, min(int(limit), 100))
        with self._connect() as db:
            rows = db.execute('''SELECT id,ts,severity,title,detail,source FROM alerts
                                 ORDER BY id DESC LIMIT ?''', (limit,)).fetchall()
        return [dict(item) for item in rows]
