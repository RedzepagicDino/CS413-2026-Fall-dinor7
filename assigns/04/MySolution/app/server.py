"""Loopback-only WSGI wiring (HTTP controller boundary)."""
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from .model import AppModel
from .backend import LambdaBackend
from .controller import Controller
from .view import page
model=AppModel(); controller=Controller(model, LambdaBackend())
def application(environ, start_response):
    message=""
    if environ["REQUEST_METHOD"] == "POST":
        try:
            size=int(environ.get("CONTENT_LENGTH") or 0); body=environ["wsgi.input"].read(size).decode("utf-8", "replace")
            data=parse_qs(body); source=data.get("source", [model.source])[0]; action=data.get("action", ["apply"])[0]
            controller.change_source(source)
            if action != "apply": controller.act(action)
            message="Source applied." if action == "apply" else "Operation completed."
        except Exception as exc: message=f"Change rejected; previous applied source kept: {exc}"
    html=page(model,message).encode(); start_response("200 OK", [("Content-Type","text/html; charset=utf-8"),("Content-Length",str(len(html)))]); return [html]
if __name__ == "__main__":
    print("Open http://127.0.0.1:8000")
    make_server("127.0.0.1",8000,application).serve_forever()
