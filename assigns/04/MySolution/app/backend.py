"""Replaceable language-tool adapter."""
from dataclasses import dataclass
from enum import Enum
from .reader import read_source
from . import lambda1 as L

class Kind(str, Enum): SUCCESS="success"; INVALID="invalid-input-or-language-error"; FAILURE="backend-failure"; UNIMPLEMENTED="not-implemented"
@dataclass(frozen=True)
class Result:
    operation: str; revision: int; kind: Kind; text: str; artifact: object | None = None

class LambdaBackend:
    def lint(self, source, revision):
        try:
            free = L.d0exp_fvset(read_source(source))
            if free: return Result("lint", revision, Kind.INVALID, "Undeclared variable(s): " + ", ".join(sorted(free)))
            return Result("lint", revision, Kind.SUCCESS, "Lint passed: no undeclared variables.")
        except (ValueError, TypeError) as exc: return Result("lint", revision, Kind.INVALID, str(exc))
        except Exception as exc: return Result("lint", revision, Kind.FAILURE, f"Lint backend failure: {exc}")
    def interpret(self, source, revision):
        try:
            value = L.d0exp_evaluate(read_source(source), L.ENVnil())
            if _has_error(value): return Result("interpret", revision, Kind.INVALID, "Runtime error: interpreter returned D0V000")
            return Result("interpret", revision, Kind.SUCCESS, repr(value))
        except (ValueError, TypeError, ZeroDivisionError, RecursionError) as exc: return Result("interpret", revision, Kind.INVALID, f"Runtime/input error: {exc}")
        except Exception as exc: return Result("interpret", revision, Kind.FAILURE, f"Interpret backend failure: {exc}")
    def typecheck(self, source, revision): return Result("type-check", revision, Kind.UNIMPLEMENTED, "Type checking is not yet implemented.")
    def compile(self, source, revision): return Result("compile", revision, Kind.UNIMPLEMENTED, "Compilation is not yet implemented.")
    def execute(self, artifact, revision): return Result("execute", revision, Kind.UNIMPLEMENTED, "Execute is unavailable: no generated-code artifact exists.")
def _has_error(value):
    return isinstance(value, L.D0V000) and not isinstance(value, (L.D0Vint,L.D0Vbtf,L.D0Vpair,L.D0Vlam,L.D0Vfix)) or (isinstance(value, L.D0Vpair) and (_has_error(value.arg1) or _has_error(value.arg2)))
