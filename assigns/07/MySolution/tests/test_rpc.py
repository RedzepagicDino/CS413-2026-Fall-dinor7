"""HTTP-level regression tests for the LAMBDA3 JSON-RPC service."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import SERVICE, RpcHandler, error_response, handle_payload


class RpcHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), RpcHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/rpc"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post(self, payload, content_type="application/json"):
        request = Request(self.url, data=json.dumps(payload).encode(), method="POST",
                          headers={"Content-Type": content_type})
        try:
            response = urlopen(request)
        except HTTPError as error:
            response = error
        with response:
            body = response.read()
            return response.status, json.loads(body) if body else None

    def call(self, method, params, request_id=1):
        return self.post({"jsonrpc": "2.0", "method": method, "params": params, "id": request_id})

    def test_health_and_typecheck(self):
        status, body = self.call("service.health", {}, "health")
        self.assertEqual((status, body["result"]), (200, {"status": "ok", "version": "1.0"}))
        status, body = self.call("lambda.typecheck", {"source": "1 + 2"}, 2)
        self.assertEqual((status, body["result"]), (200, {"type": "sint"}))

    def test_interpretation_values_and_function_formatting(self):
        cases = [("20 + 22", {"type": "sint", "value": "42"}),
                 ("(1, true)", {"type": "(sint, bool)", "value": "(1, true)"}),
                 ("list_cons(1, list_cons(2, list_nil()))", {"type": "List[sint]", "value": "[1, 2]"}),
                 ("let f : sint -> sint = lam (x: sint) => x in f end",
                  {"type": "sint -> sint", "value": "<lam>"})]
        for source, expected in cases:
            with self.subTest(source=source):
                status, body = self.call("lambda.interpret", {"source": source})
                self.assertEqual(status, 200)
                self.assertEqual(body["result"], expected)

    def test_factorial_and_compilers(self):
        factorial = "let fact : sint -> sint = fix fact(n: sint): sint => if n <= 1 then 1 else n * fact(n - 1) in fact(6) end"
        self.assertEqual(self.call("lambda.interpret", {"source": factorial})[1]["result"]["value"], "720")
        for target in ("python", "javascript"):
            status, body = self.call("lambda.compile", {"source": "1 + 2", "target": target})
            self.assertEqual(status, 200)
            self.assertEqual(body["result"]["target"], target)
            self.assertTrue(body["result"]["code"].strip())

    def test_language_and_parameter_errors(self):
        for source, code in (("if then", -32010), ("1 + true", -32011)):
            body = self.call("lambda.typecheck", {"source": source})[1]
            self.assertEqual(body["error"]["code"], code)
        for method, params in (("lambda.interpret", {}), ("lambda.interpret", {"source": " "}),
                               ("lambda.compile", {"source": "1", "target": "ruby"})):
            self.assertEqual(self.call(method, params)[1]["error"]["code"], -32602)
        self.assertEqual(self.call("not.a.method", {})[1]["error"]["code"], -32601)

    def test_batches_notifications_and_transport(self):
        status, body = self.post([{"jsonrpc": "2.0", "method": "service.health", "params": {}, "id": "a"},
                                  {"jsonrpc": "2.0", "method": "service.health", "params": {}}])
        self.assertEqual((status, len(body), body[0]["id"]), (200, 1, "a"))
        status, body = self.post({"jsonrpc": "2.0", "method": "service.health", "params": {}})
        self.assertEqual((status, body), (204, None))
        self.assertEqual(self.post([])[1], error_response(None, -32600, "Invalid Request"))
        self.assertEqual(self.post({"jsonrpc": "2.0", "method": "service.health", "params": {}}, "text/plain")[0], 415)

    def test_invalid_batch_item_and_internal_helper_contract(self):
        status, body = self.post([{"jsonrpc": "2.0", "method": "service.health", "params": {}, "id": "ok"}, "bad"])
        self.assertEqual(status, 200)
        self.assertEqual({item["id"] for item in body}, {"ok", None})
        status, body = handle_payload({"jsonrpc": "1.0", "method": "service.health", "id": 1})
        self.assertEqual((status, body["error"]["code"]), (200, -32600))

    def test_injected_backend_failure_is_sanitized(self):
        with patch.object(SERVICE, "health", side_effect=RuntimeError("secret traceback detail")):
            status, body = self.call("service.health", {}, "failure")
        self.assertEqual(status, 200)
        self.assertEqual(body["id"], "failure")
        self.assertEqual(body["error"]["code"], -32603)
        self.assertNotIn("secret", json.dumps(body))


if __name__ == "__main__":
    unittest.main()
