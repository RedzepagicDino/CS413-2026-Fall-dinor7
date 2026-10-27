"""Bounded pure observation contexts for Church values."""
from target import Var, Lam, App, Term, apps, evaluate_target, Reduction
import church

class ObservationError(ValueError): pass

def _require(result: Reduction) -> Term:
    if not result.complete: raise ObservationError(f"observation budget exhausted after {result.steps} beta steps")
    return result.value

def observe_nat(value: Term, budget=100_000) -> tuple[int, int]:
    step = Lam("tail", Lam("c", Lam("z", App(Var("c"), Var("tail")))))
    base = Lam("c", Lam("z", Var("z")))
    result = evaluate_target(apps(value, step, base), budget)
    term = _require(result)
    def count(t):
        if isinstance(t, Lam) and isinstance(t.body, Lam):
            c, inner = t.name, t.body
            if isinstance(inner.body, Var) and inner.body.name == inner.name: return 0
            if isinstance(inner.body, App) and isinstance(inner.body.fn, Var) and inner.body.fn.name == c:
                return 1 + count(inner.body.arg)
        raise ObservationError("malformed Church-natural observation output")
    return count(term), result.steps

def observe_bool(value: Term, budget=100_000) -> tuple[bool, int]:
    yes, no = church.identity(), Lam("a", Lam("b", Var("a")))
    result = evaluate_target(apps(value, yes, no), budget)
    term = _require(result)
    if term == yes: return True, result.steps
    if term == no: return False, result.steps
    raise ObservationError("malformed Church-boolean observation output")

def observe(value: Term, kind, budget=100_000):
    if kind == "nat": return observe_nat(value, budget)[0]
    if kind == "bool": return observe_bool(value, budget)[0]
    if isinstance(kind, tuple) and len(kind) == 3 and kind[0] == "pair":
        left = _require(evaluate_target(App(church.fst(), value), budget))
        right = _require(evaluate_target(App(church.snd(), value), budget))
        return (observe(left, kind[1], budget), observe(right, kind[2], budget))
    raise ObservationError(f"unknown expected kind: {kind!r}")
