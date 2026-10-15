"""Visitor-based pretty printing and capture-avoiding substitution."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lambda1_vp import (D0ExpVisitor, D0Eint, D0Ebtf, D0Evar, D0Eop1,
    D0Eop2, D0Elam, D0Efix, D0Eapp, D0Eif0, D0Elet, D0Epair, D0Epfst,
    D0Epsnd, d0exp, d0exp_fvset)


class PrettyPrintVisitor(D0ExpVisitor[str]):
    def visit_int(self, e): return str(e.arg1)
    def visit_btf(self, e): return "true" if e.arg1 else "false"
    def visit_var(self, e): return e.arg1
    def visit_op1(self, e): return f"({e.name} {e.arg1.accept(self)})"
    def visit_op2(self, e): return f"({e.arg1.accept(self)} {e.name} {e.arg2.accept(self)})"
    def visit_lam(self, e): return f"(lam {e.arg1}. {e.arg2.accept(self)})"
    def visit_fix(self, e): return f"(fix {e.arg1}({e.arg2}). {e.arg3.accept(self)})"
    def visit_app(self, e): return f"({e.arg1.accept(self)} {e.arg2.accept(self)})"
    def visit_if0(self, e): return f"(if {e.arg1.accept(self)} then {e.arg2.accept(self)} else {e.arg3.accept(self)})"
    def visit_let(self, e): return f"(let {e.arg1} = {e.arg2.accept(self)} in {e.arg3.accept(self)})"
    def visit_pair(self, e): return f"(pair {e.arg1.accept(self)} {e.arg2.accept(self)})"
    def visit_pfst(self, e): return f"(fst {e.arg1.accept(self)})"
    def visit_psnd(self, e): return f"(snd {e.arg1.accept(self)})"


def d0exp_pretty(expression: d0exp) -> str:
    return expression.accept(PrettyPrintVisitor())


class NameVisitor(D0ExpVisitor[set[str]]):
    """Collect all spelling occurrences, including binders, via accept."""
    def visit_int(self, e): return set()
    def visit_btf(self, e): return set()
    def visit_var(self, e): return {e.arg1}
    def visit_op1(self, e): return e.arg1.accept(self)
    def visit_op2(self, e): return e.arg1.accept(self) | e.arg2.accept(self)
    def visit_lam(self, e): return {e.arg1} | e.arg2.accept(self)
    def visit_fix(self, e): return {e.arg1, e.arg2} | e.arg3.accept(self)
    def visit_app(self, e): return e.arg1.accept(self) | e.arg2.accept(self)
    def visit_if0(self, e): return e.arg1.accept(self) | e.arg2.accept(self) | e.arg3.accept(self)
    def visit_let(self, e): return {e.arg1} | e.arg2.accept(self) | e.arg3.accept(self)
    def visit_pair(self, e): return e.arg1.accept(self) | e.arg2.accept(self)
    def visit_pfst(self, e): return e.arg1.accept(self)
    def visit_psnd(self, e): return e.arg1.accept(self)


class FreshNames:
    """Generate base_1, base_2, ... avoiding every name seen so far."""
    def __init__(self, used: set[str]): self.used, self.next = set(used), 1
    def get(self, base: str) -> str:
        while f"{base}_{self.next}" in self.used: self.next += 1
        name = f"{base}_{self.next}"; self.used.add(name); self.next += 1
        return name


class RenameVisitor(D0ExpVisitor[d0exp]):
    """Rename free occurrences of old in this subtree, respecting shadows."""
    def __init__(self, old, new): self.old, self.new = old, new
    def visit_int(self,e): return D0Eint(e.arg1)
    def visit_btf(self,e): return D0Ebtf(e.arg1)
    def visit_var(self,e): return D0Evar(self.new if e.arg1 == self.old else e.arg1)
    def visit_op1(self,e): return D0Eop1(e.name,e.arg1.accept(self))
    def visit_op2(self,e): return D0Eop2(e.name,e.arg1.accept(self),e.arg2.accept(self))
    def visit_app(self,e): return D0Eapp(e.arg1.accept(self),e.arg2.accept(self))
    def visit_if0(self,e): return D0Eif0(e.arg1.accept(self),e.arg2.accept(self),e.arg3.accept(self))
    def visit_pair(self,e): return D0Epair(e.arg1.accept(self),e.arg2.accept(self))
    def visit_pfst(self,e): return D0Epfst(e.arg1.accept(self))
    def visit_psnd(self,e): return D0Epsnd(e.arg1.accept(self))
    def visit_lam(self,e):
        return D0Elam(e.arg1, e.arg2 if e.arg1 == self.old else e.arg2.accept(self))
    def visit_let(self,e):
        return D0Elet(e.arg1, e.arg2.accept(self), e.arg3 if e.arg1 == self.old else e.arg3.accept(self))
    def visit_fix(self,e):
        # A parameter with the same name shadows the function binder.
        bound = {e.arg2} | ({e.arg1} if e.arg1 != e.arg2 else set())
        return D0Efix(e.arg1,e.arg2,e.arg3 if self.old in bound else e.arg3.accept(self))


class SubstitutionVisitor(D0ExpVisitor[d0exp]):
    def __init__(self, variable: str, replacement: d0exp, fresh: FreshNames):
        self.variable, self.replacement, self.replacement_fv, self.fresh = variable, replacement, d0exp_fvset(replacement), fresh
    def visit_int(self,e): return D0Eint(e.arg1)
    def visit_btf(self,e): return D0Ebtf(e.arg1)
    def visit_var(self,e): return self.replacement if e.arg1 == self.variable else D0Evar(e.arg1)
    def visit_op1(self,e): return D0Eop1(e.name,e.arg1.accept(self))
    def visit_op2(self,e): return D0Eop2(e.name,e.arg1.accept(self),e.arg2.accept(self))
    def visit_app(self,e): return D0Eapp(e.arg1.accept(self),e.arg2.accept(self))
    def visit_if0(self,e): return D0Eif0(e.arg1.accept(self),e.arg2.accept(self),e.arg3.accept(self))
    def visit_pair(self,e): return D0Epair(e.arg1.accept(self),e.arg2.accept(self))
    def visit_pfst(self,e): return D0Epfst(e.arg1.accept(self))
    def visit_psnd(self,e): return D0Epsnd(e.arg1.accept(self))
    def visit_lam(self,e):
        if e.arg1 == self.variable: return D0Elam(e.arg1,e.arg2)
        body = e.arg2
        if self.variable in d0exp_fvset(body) and e.arg1 in self.replacement_fv:
            name = self.fresh.get(e.arg1); body = body.accept(RenameVisitor(e.arg1,name)); return D0Elam(name,body.accept(self))
        return D0Elam(e.arg1,body.accept(self))
    def visit_let(self,e):
        init = e.arg2.accept(self)
        if e.arg1 == self.variable: return D0Elet(e.arg1,init,e.arg3)
        body = e.arg3
        if self.variable in d0exp_fvset(body) and e.arg1 in self.replacement_fv:
            name = self.fresh.get(e.arg1); body = body.accept(RenameVisitor(e.arg1,name)); return D0Elet(name,init,body.accept(self))
        return D0Elet(e.arg1,init,body.accept(self))
    def visit_fix(self,e):
        # With equal names, arg2 is the effective binder (as in EvaluateVisitor).
        bound = {e.arg2} | ({e.arg1} if e.arg1 != e.arg2 else set())
        if self.variable in bound: return D0Efix(e.arg1,e.arg2,e.arg3)
        f, x, body = e.arg1, e.arg2, e.arg3
        if self.variable in d0exp_fvset(body):
            if f != x and f in self.replacement_fv:
                nf=self.fresh.get(f); body=body.accept(RenameVisitor(f,nf)); f=nf
            if x in self.replacement_fv:
                nx=self.fresh.get(x); body=body.accept(RenameVisitor(x,nx)); x=nx
        return D0Efix(f,x,body.accept(self))


def d0exp_substitute(expression: d0exp, variable: str, replacement: d0exp) -> d0exp:
    """Return expression[variable := replacement] without evaluation or mutation."""
    names = expression.accept(NameVisitor()) | replacement.accept(NameVisitor()) | {variable}
    return expression.accept(SubstitutionVisitor(variable, replacement, FreshNames(names)))
