"""One evaluator entry point for source ASTs and pure target terms."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "05"))
from lambda1_vp import D0Eint, D0Ebtf, D0Evar, D0Eop1, D0Eop2, D0Elam, D0Efix, D0Eapp, D0Eif0, D0Elet, D0Epair, D0Epfst, D0Epsnd
from target import Var, Lam, App, evaluate_target, Reduction

class SourceClosure:
    def __init__(self, name, body, env): self.name, self.body, self.env = name, body, env
class FixClosure:
    def __init__(self, f, x, body, env): self.f, self.x, self.body, self.env = f, x, body, env

def evaluate_source(e, env=None):
    env = {} if env is None else env
    if isinstance(e, D0Eint): return e.arg1
    if isinstance(e, D0Ebtf): return e.arg1
    if isinstance(e, D0Evar): return env[e.arg1]
    if isinstance(e, D0Elam): return SourceClosure(e.arg1, e.arg2, env.copy())
    if isinstance(e, D0Efix): return FixClosure(e.arg1, e.arg2, e.arg3, env.copy())
    if isinstance(e, D0Eapp):
        fun, arg = evaluate_source(e.arg1, env), evaluate_source(e.arg2, env)
        if isinstance(fun, SourceClosure):
            return evaluate_source(fun.body, fun.env | {fun.name: arg})
        if isinstance(fun, FixClosure):
            # When f == x, x shadows f, matching the assignment's binding rule.
            recursive = fun
            call_env = fun.env | ({fun.f: recursive} if fun.f != fun.x else {}) | {fun.x: arg}
            return evaluate_source(fun.body, call_env)
        raise TypeError("application of non-function")
    if isinstance(e, D0Elet): return evaluate_source(e.arg3, env | {e.arg1: evaluate_source(e.arg2, env)})
    if isinstance(e, D0Eif0): return evaluate_source(e.arg2 if evaluate_source(e.arg1, env) else e.arg3, env)
    if isinstance(e, D0Epair): return (evaluate_source(e.arg1, env), evaluate_source(e.arg2, env))
    if isinstance(e, D0Epfst): return evaluate_source(e.arg1, env)[0]
    if isinstance(e, D0Epsnd): return evaluate_source(e.arg1, env)[1]
    if isinstance(e, D0Eop1):
        if e.name != "not": raise ValueError(f"unsupported unary operator: {e.name}")
        return not evaluate_source(e.arg1, env)
    if isinstance(e, D0Eop2):
        a = evaluate_source(e.arg1, env)
        if e.name == "and": return a and evaluate_source(e.arg2, env)
        if e.name == "or": return a or evaluate_source(e.arg2, env)
        b = evaluate_source(e.arg2, env)
        return {"+":lambda:a+b, "-":lambda:max(a-b,0), "*":lambda:a*b, "<":lambda:a<b, "<=":lambda:a<=b, ">":lambda:a>b, ">=":lambda:a>=b, "==":lambda:a==b, "!=":lambda:a!=b}[e.name]()
    raise TypeError(f"unsupported expression {type(e).__name__}")

def evaluate(expression, budget=100_000):
    """Evaluate source ASTs directly; bounded pure reduction for target terms."""
    if isinstance(expression, (Var, Lam, App)): return evaluate_target(expression, budget)
    return evaluate_source(expression)
