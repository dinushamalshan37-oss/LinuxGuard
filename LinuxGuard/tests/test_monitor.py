import tempfile
import unittest
from pathlib import Path 

from monitor import LinuxMonitor, recommendations
from storage import Store 


class MonitoringTests(unittest.TestCase):
    def test_initial_threshold(self):
        self.assertEqual(LinuxMonitor.anomaly_threshold([]), 85.0)
        self.assertEqual(LinuxMonitor.anomaly_threshold([22] * 7), 85.0)

    def test_baseline_bounds(self):
        self.assertEqual(LinuxMonitor.anomaly_threshold([10] * 12), 70.0)
        self.assertEqual(LinuxMonitor.anomaly_threshold([100] * 12), 95.0)

    def test_health_score_bounds(self):
        self.assertEqual(LinuxMonitor.health_score(10, 10, 10), 100)
        self.assertGreaterEqual(LinuxMonitor.health_score(100, 100, 100), 0)
        self.assertLess(LinuxMonitor.health_score(100, 100, 100), 100)

    def test_recommendations(self):
        self.assertIn('top', recommendations(dict(cpu=92, memory=50, disk=40))[0])
        self.assertEqual(len(recommendations(dict(cpu=20, memory=30, disk=50))), 1)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.folder.name) / 'history.db')

    def tearDown(self):
        self.folder.cleanup()

    def test_samples_are_ordered(self):
        for ts in [10, 20, 30]:
            self.store.add_sample(dict(ts=ts, cpu=10, memory=20, disk=30,
                                       rx_kbs=1, tx_kbs=2, anomaly=False))
        self.assertEqual([item['ts'] for item in self.store.samples(2)], [20, 30])

    def test_alert_deduplication(self):
        args=('warning', 'CPU spike', 'High CPU', 'performance', 'cpu-high')
        self.assertTrue(self.store.add_alert(*args))
        self.assertFalse(self.store.add_alert(*args))
        self.assertEqual(len(self.store.alerts()), 1)

    def test_sample_limit_clamped(self):
        self.assertEqual(self.store.samples(99999), [])


if __name__ == '__main__':
    unittest.main()
