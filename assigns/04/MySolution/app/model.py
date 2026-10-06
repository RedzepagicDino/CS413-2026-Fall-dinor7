"""Browser-independent MVC model and state rules."""
from dataclasses import dataclass, field
from .backend import Result
@dataclass
class AppModel:
    source: str = "D0Eint(42)"; revision: int = 1; result: Result | None = None; artifact: object | None = None; busy: bool = False
    def apply_source(self, source):
        if not source.strip(): raise ValueError("Source cannot be empty; previous applied source was kept.")
        self.source=source; self.revision += 1; self.artifact=None; self.result=None
    def record(self, result):
        if result.revision == self.revision: self.result=result
