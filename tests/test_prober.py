import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import unittest
from health_prober import HealthProber, EndpointConfig


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        elif self.path == "/error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server Error")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress server log messages during test


class TestHealthProber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), SimpleHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_probe_endpoints(self):
        async def run_test():
            prober = HealthProber(concurrency=2)
            endpoints = [
                EndpointConfig(
                    name="Health Check",
                    url=f"http://127.0.0.1:{self.port}/health",
                    expected_status=200,
                    keyword_assertion="status",
                    check_ssl=False,
                ),
                EndpointConfig(
                    name="Error Route",
                    url=f"http://127.0.0.1:{self.port}/error",
                    expected_status=200,
                    check_ssl=False,
                ),
            ]

            summary = await prober.probe_all(endpoints)
            self.assertEqual(summary.total_endpoints, 2)
            self.assertEqual(summary.healthy_count, 1)
            self.assertEqual(summary.unhealthy_count, 1)
            self.assertFalse(summary.is_all_healthy)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
