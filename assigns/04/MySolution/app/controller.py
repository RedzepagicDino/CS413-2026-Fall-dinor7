"""Controller coordinates model/backend; it has no HTML dependency."""
from .backend import Result, Kind
import threading
class Controller:
    def __init__(self, model, backend, timeout_seconds=2): self.model, self.backend, self.timeout_seconds = model, backend, timeout_seconds
    def change_source(self, text): self.model.apply_source(text)
    def act(self, operation):
        if self.model.busy: return Result(operation, self.model.revision, Kind.FAILURE, "Application is busy; retry shortly.")
        self.model.busy=True
        try:
            method = getattr(self.backend, operation.replace("-", "_"))
            box=[]
            def work():
                try: box.append(method(self.model.source, self.model.revision) if operation != "execute" else method(self.model.artifact, self.model.revision))
                except Exception as exc: box.append(Result(operation, self.model.revision, Kind.FAILURE, f"Backend failure: {exc}"))
            thread=threading.Thread(target=work, daemon=True); thread.start(); thread.join(self.timeout_seconds)
            result = box[0] if box else Result(operation, self.model.revision, Kind.FAILURE, f"Timed out after {self.timeout_seconds} seconds; retry is available.")
            self.model.record(result); return result
        finally: self.model.busy=False
