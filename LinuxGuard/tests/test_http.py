import json
import threading
import unittest
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from app import Handler


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=2)

    def test_dashboard_is_served(self):
        with urlopen(self.url,timeout=5) as response:
            self.assertIn(b'LinuxGuard',response.read())
            self.assertEqual(response.status,200)

    def test_history_endpoint(self):
        with urlopen(self.url+'/api/history?limit=10',timeout=5) as response:
            payload=json.loads(response.read())
            self.assertIn('samples',payload)

    def test_unknown_route_returns_404(self):
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as cm:
            urlopen(self.url+'/not-a-real-route',timeout=5)
        self.assertEqual(cm.exception.code,404)


if __name__ == '__main__':
    unittest.main()
