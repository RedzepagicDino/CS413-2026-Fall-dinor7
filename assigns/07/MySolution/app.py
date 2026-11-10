"""Local JSON-RPC 2.0 service for the course LAMBDA3 implementation."""
from __future__ import annotations

import json
import logging
import multiprocessing as mp
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

LAMBDA_DIR = Path(__file__).resolve().parents[1] / "LAMBDA3"
if str(LAMBDA_DIR) not in sys.path:
    sys.path.insert(0, str(LAMBDA_DIR))

from lambda3 import (  # noqa: E402
    LambdaSyntaxError,
    TypeCheckError,
    d0exp_compile,
    d0exp_compile_js,
    d0exp_evaluate,
    d0exp_parse_and_typecheck,
    d0val_format,
    format_type,
)

MAX_SOURCE_BYTES = 100_000
INTERPRET_TIMEOUT_SECONDS = 2.0

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
LAMBDA_SYNTAX_ERROR = -32010
LAMBDA_TYPE_ERROR = -32011
EXECUTION_TIMEOUT = -32012

LOG = logging.getLogger("lambda_rpc")


class RpcFailure(Exception):
    def __init__(self, code: int, message: str, data: dict[str, Any] | None = None):
        self.code, self.message, self.data = code, message, data


def _client_diagnostic(error: Exception) -> dict[str, str]:
    """Keep useful language diagnostics while withholding host details."""
    return {"diagnostic": str(error)[:500]}


def _interpret_worker(source: str, connection: Any) -> None:
    """Evaluate in an isolated process so a nonterminating program can end."""
    try:
        expression, _ = d0exp_parse_and_typecheck(source)
        connection.send(("ok", d0val_format(d0exp_evaluate(expression))))
    except LambdaSyntaxError as error:
        connection.send(("syntax", str(error)))
    except TypeCheckError as error:
        connection.send(("type", str(error)))
    except Exception:  # Do not transmit tracebacks or implementation internals.
        connection.send(("internal", ""))
    finally:
        connection.close()


class LambdaService:
    def _source(self, params: dict[str, Any]) -> str:
        source = params.get("source")
        if not isinstance(source, str) or not source.strip():
            raise RpcFailure(INVALID_PARAMS, "source must be a nonempty string")
        if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise RpcFailure(INVALID_PARAMS, "source exceeds the maximum size",
                             {"max_source_bytes": MAX_SOURCE_BYTES})
        return source

    @staticmethod
    def _parse_and_check(source: str) -> tuple[Any, Any]:
        try:
            return d0exp_parse_and_typecheck(source)
        except LambdaSyntaxError as error:
            raise RpcFailure(LAMBDA_SYNTAX_ERROR, "LAMBDA syntax error",
                             _client_diagnostic(error)) from error
        except TypeCheckError as error:
            raise RpcFailure(LAMBDA_TYPE_ERROR, "LAMBDA type-checking error",
                             _client_diagnostic(error)) from error

    def health(self, params: dict[str, Any]) -> dict[str, str]:
        if params:
            raise RpcFailure(INVALID_PARAMS, "service.health takes no parameters")
        return {"status": "ok", "version": "1.0"}

    def typecheck(self, params: dict[str, Any]) -> dict[str, str]:
        _, typ = self._parse_and_check(self._source(params))
        return {"type": format_type(typ)}

    def interpret(self, params: dict[str, Any]) -> dict[str, str]:
        source = self._source(params)
        _, typ = self._parse_and_check(source)
        parent, child = mp.Pipe(duplex=False)
        process = mp.Process(target=_interpret_worker, args=(source, child), daemon=True)
        process.start()
        child.close()
        process.join(INTERPRET_TIMEOUT_SECONDS)
        if process.is_alive():
            process.terminate()
            process.join()
            raise RpcFailure(EXECUTION_TIMEOUT, "LAMBDA execution timed out",
                             {"timeout_seconds": INTERPRET_TIMEOUT_SECONDS})
        if not parent.poll():
            raise RpcFailure(INTERNAL_ERROR, "Internal error")
        kind, payload = parent.recv()
        if kind == "ok":
            return {"type": format_type(typ), "value": payload}
        if kind == "syntax":
            raise RpcFailure(LAMBDA_SYNTAX_ERROR, "LAMBDA syntax error", {"diagnostic": payload[:500]})
        if kind == "type":
            raise RpcFailure(LAMBDA_TYPE_ERROR, "LAMBDA type-checking error", {"diagnostic": payload[:500]})
        raise RpcFailure(INTERNAL_ERROR, "Internal error")

    def compile(self, params: dict[str, Any]) -> dict[str, str]:
        source = self._source(params)
        target = params.get("target")
        if target not in ("python", "javascript"):
            raise RpcFailure(INVALID_PARAMS, "target must be 'python' or 'javascript'")
        expression, _ = self._parse_and_check(source)
        code = d0exp_compile(expression) if target == "python" else d0exp_compile_js(expression)
        return {"target": target, "code": code}


SERVICE = LambdaService()


def success(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str,
                   data: dict[str, Any] | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def valid_id(value: Any) -> bool:
    return value is None or (isinstance(value, (str, int, float)) and not isinstance(value, bool))


def dispatch(request: Any) -> dict[str, Any] | None:
    """Return one JSON-RPC response, or None for a valid notification."""
    if not isinstance(request, dict):
        return error_response(None, INVALID_REQUEST, "Invalid Request")
    if request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        return error_response(None, INVALID_REQUEST, "Invalid Request")
    has_id = "id" in request
    request_id = request.get("id")
    if has_id and not valid_id(request_id):
        return error_response(None, INVALID_REQUEST, "Invalid Request")
    notification = not has_id
    params = request.get("params")
    if not isinstance(params, dict):
        response = error_response(request_id, INVALID_PARAMS, "params must be an object")
        return None if notification else response
    methods = {
        "service.health": SERVICE.health,
        "lambda.typecheck": SERVICE.typecheck,
        "lambda.interpret": SERVICE.interpret,
        "lambda.compile": SERVICE.compile,
    }
    operation = methods.get(request["method"])
    if operation is None:
        response = error_response(request_id, METHOD_NOT_FOUND, "Method not found")
        return None if notification else response
    try:
        response = success(request_id, operation(params))
    except RpcFailure as failure:
        response = error_response(request_id, failure.code, failure.message, failure.data)
    except Exception:
        LOG.exception("Unexpected service failure")
        response = error_response(request_id, INTERNAL_ERROR, "Internal error")
    return None if notification else response


def handle_payload(payload: Any) -> tuple[int, Any | None]:
    if isinstance(payload, list):
        if not payload:
            return HTTPStatus.OK, error_response(None, INVALID_REQUEST, "Invalid Request")
        responses = [response for item in payload if (response := dispatch(item)) is not None]
        return (HTTPStatus.NO_CONTENT, None) if not responses else (HTTPStatus.OK, responses)
    response = dispatch(payload)
    return (HTTPStatus.NO_CONTENT, None) if response is None else (HTTPStatus.OK, response)


class RpcHandler(BaseHTTPRequestHandler):
    server_version = "LambdaRpc/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        LOG.info("%s - %s", self.address_string(), format % args)

    def _send(self, status: int, body: Any | None) -> None:
        encoded = b"" if body is None else json.dumps(body).encode("utf-8")
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if encoded:
            self.wfile.write(encoded)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/rpc":
            self._send(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().split(";", 1)[0] == "application/json":
            self._send(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Content-Type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._send(HTTPStatus.OK, error_response(None, PARSE_ERROR, "Parse error"))
            return
        status, body = handle_payload(payload)
        self._send(status, body)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RpcHandler)
    print("LAMBDA3 JSON-RPC service listening at http://127.0.0.1:8000/rpc")
    server.serve_forever()


if __name__ == "__main__":
    mp.freeze_support()
    main()
