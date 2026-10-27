"""Pure, untyped lambda-calculus terms and a weak CBV reducer."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Var: name: str
@dataclass(frozen=True)
class Lam: name: str; body: object
@dataclass(frozen=True)
class App: fn: object; arg: object
Term = Var | Lam | App

def pretty(t: Term) -> str:
    if isinstance(t, Var): return t.name
    if isinstance(t, Lam): return f"(lam {t.name}. {pretty(t.body)})"
    return f"({pretty(t.fn)} {pretty(t.arg)})"

def free_vars(t: Term) -> frozenset[str]:
    if isinstance(t, Var): return frozenset({t.name})
    if isinstance(t, Lam): return free_vars(t.body) - {t.name}
    return free_vars(t.fn) | free_vars(t.arg)

def all_names(t: Term) -> set[str]:
    if isinstance(t, Var): return {t.name}
    if isinstance(t, Lam): return {t.name} | all_names(t.body)
    return all_names(t.fn) | all_names(t.arg)

def fresh(base: str, used: set[str]) -> str:
    i = 1
    while f"{base}_{i}" in used: i += 1
    return f"{base}_{i}"

def rename_bound(t: Term, old: str, new: str) -> Term:
    """Rename free occurrences of old in a binder's body."""
    if isinstance(t, Var): return Var(new if t.name == old else t.name)
    if isinstance(t, App): return App(rename_bound(t.fn, old, new), rename_bound(t.arg, old, new))
    return t if t.name == old else Lam(t.name, rename_bound(t.body, old, new))

def substitute(t: Term, name: str, replacement: Term) -> Term:
    """Capture-avoiding substitution; neither argument is mutated."""
    if isinstance(t, Var): return replacement if t.name == name else t
    if isinstance(t, App): return App(substitute(t.fn, name, replacement), substitute(t.arg, name, replacement))
    if t.name == name: return t
    body = t.body
    if name in free_vars(body) and t.name in free_vars(replacement):
        n = fresh(t.name, all_names(body) | all_names(replacement) | {name, t.name})
        body = rename_bound(body, t.name, n)
        return Lam(n, substitute(body, name, replacement))
    return Lam(t.name, substitute(body, name, replacement))

@dataclass(frozen=True)
class Reduction:
    complete: bool
    value: Term | None
    steps: int

def evaluate_target(t: Term, budget: int = 100_000) -> Reduction:
    """Weak, deterministic, left-to-right call-by-value evaluation."""
    if budget < 0: raise ValueError("budget must be nonnegative")
    steps = 0
    def go(e: Term) -> Term | None:
        nonlocal steps
        if isinstance(e, Lam): return e
        if isinstance(e, Var): raise ValueError(f"open target term: {e.name}")
        f = go(e.fn)
        if f is None: return None
        a = go(e.arg)
        if a is None: return None
        if not isinstance(f, Lam): raise TypeError("attempted to apply a non-lambda")
        if steps >= budget: return None
        steps += 1
        return go(substitute(f.body, f.name, a))
    value = go(t)
    return Reduction(value is not None, value, steps)

def apps(*terms: Term) -> Term:
    result = terms[0]
    for t in terms[1:]: result = App(result, t)
    return result

def lams(names: list[str], body: Term) -> Term:
    for n in reversed(names): body = Lam(n, body)
    return body
