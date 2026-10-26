import unittest
from unittest.mock import patch
from security import FAILURE_PATTERN, run_security_scan


class FakeStore:
    def __init__(self): self.events=[]
    def add_alert(self,*args,**kwargs): self.events.append((args,kwargs))


class SecurityTests(unittest.TestCase):
    def test_failed_login_patterns(self):
        messages='Failed password for invalid user alice\nInvalid user someone\nauthentication failure'
        self.assertEqual(sum(bool(FAILURE_PATTERN.search(line)) for line in messages.splitlines()),3)

    @patch('security.recent_ssh_failures',return_value=(7,'readable journal'))
    @patch('security.listening_ports',return_value=([{'host':'0.0.0.0','port':22,'pid':4,'public_bind':True}],False))
    def test_scan_returns_findings_and_alert(self,_ports,_ssh):
        store=FakeStore()
        result=run_security_scan(store)
        self.assertEqual(result['all_interface_count'],1)
        self.assertEqual(result['ssh_failures_last_hour'],7)
        self.assertTrue(store.events)
        self.assertGreaterEqual(len(result['findings']),2)

    @patch('security.recent_ssh_failures',return_value=(None,'permission denied'))
    @patch('security.listening_ports',return_value=([],True))
    def test_limited_permissions_not_reported_as_safe(self,_ports,_ssh):
        result=run_security_scan(FakeStore())
        self.assertIsNone(result['ssh_failures_last_hour'])
        self.assertIn('incomplete',' '.join(result['findings']))


if __name__ == '__main__':
    unittest.main()
