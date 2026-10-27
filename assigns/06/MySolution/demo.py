"""Run: python3.12 demo.py (from MySolution)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "05"))
from lambda1_vp import *
from compiler import compile_expr
from evaluator import evaluate
from observe import observe, ObservationError
from target import pretty

def app(f, x): return D0Eapp(f, x)
def loop(): return app(D0Efix("loop", "x", app(D0Evar("loop"), D0Evar("x"))), D0Eint(0))
def fact(n):
    body=D0Eif0(D0Eop2("==",D0Evar("n"),D0Eint(0)),D0Eint(1),D0Eop2("*",D0Evar("n"),app(D0Evar("fact"),D0Eop2("-",D0Evar("n"),D0Eint(1)))))
    return app(D0Efix("fact","n",body),D0Eint(n))
def fib(n):
    body=D0Eif0(D0Eop2("<=",D0Evar("n"),D0Eint(1)),D0Evar("n"),D0Eop2("+",app(D0Evar("fib"),D0Eop2("-",D0Evar("n"),D0Eint(1))),app(D0Evar("fib"),D0Eop2("-",D0Evar("n"),D0Eint(2)))))
    return app(D0Efix("fib","n",body),D0Eint(n))

CASES=[
 ("2 + 3 * 4",D0Eop2("+",D0Eint(2),D0Eop2("*",D0Eint(3),D0Eint(4))),"nat",14),
 ("2 - 5",D0Eop2("-",D0Eint(2),D0Eint(5)),"nat",0),
 ("conditional",D0Eif0(D0Eop2("<=",D0Eint(2),D0Eint(3)),D0Eint(7),D0Eint(9)),"nat",7),
 ("let/lambda",D0Elet("x",D0Eint(3),app(D0Elam("y",D0Eop2("+",D0Evar("x"),D0Evar("y"))),D0Eint(4))),"nat",7),
 ("fst pair",D0Epfst(D0Epair(D0Eint(2),D0Ebtf(True))),"nat",2),
 ("snd pair",D0Epsnd(D0Epair(D0Eint(2),D0Ebtf(True))),"bool",True),
 ("higher-order",app(D0Elam("f",app(D0Evar("f"),D0Eint(3))),D0Elam("x",D0Eop2("+",D0Evar("x"),D0Eint(1)))),"nat",4),
 ("true and false",D0Eop2("and",D0Ebtf(True),D0Ebtf(False)),"bool",False),
 ("false or true",D0Eop2("or",D0Ebtf(False),D0Ebtf(True)),"bool",True),
 ("unselected LOOP",D0Eif0(D0Ebtf(True),D0Eint(1),loop()),"nat",1),
 ("argument LOOP",app(D0Elam("x",D0Eint(0)),loop()),None,"exhausted"),
 ("factorial 4",fact(4),"nat",24), ("fibonacci 5",fib(5),"nat",5), ("LOOP",loop(),None,"exhausted")]

if __name__ == "__main__":
    for label, source, kind, expected in CASES:
        execution_budget = 200 if expected == "exhausted" else 1_000_000
        target=compile_expr(source); result=evaluate(target, execution_budget)
        print(f"\n{label}\n  source: {source!r}\n  target: {pretty(target)[:180]}{'...' if len(pretty(target))>180 else ''}")
        print(f"  execution: {'complete' if result.complete else 'budget exhausted'} ({result.steps} beta steps; budget {execution_budget})")
        if result.complete:
            try: print(f"  observation: {observe(result.value,kind,1_000_000)!r}; expected: {expected!r} (budget 1000000)")
            except ObservationError as exc: print(f"  observation failed: {exc}")
        else: print(f"  expected: {expected}")
