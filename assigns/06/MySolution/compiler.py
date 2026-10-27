"""Compositional visitor translating Assignment 5 ASTs to pure terms."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "05"))
from lambda1_vp import D0ExpVisitor, D0Eint, D0Ebtf, D0Evar, D0Eop1, D0Eop2, D0Elam, D0Efix, D0Eapp, D0Eif0, D0Elet, D0Epair, D0Epfst, D0Epsnd
from target import Var, Lam, App, Term, apps, free_vars
import church

class CompileError(ValueError): pass

class _Names(D0ExpVisitor[set[str]]):
    def visit_int(self,e): return set()
    def visit_btf(self,e): return set()
    def visit_var(self,e): return {e.arg1}
    def visit_op1(self,e): return e.arg1.accept(self)
    def visit_op2(self,e): return e.arg1.accept(self)|e.arg2.accept(self)
    def visit_lam(self,e): return {e.arg1}|e.arg2.accept(self)
    def visit_fix(self,e): return {e.arg1,e.arg2}|e.arg3.accept(self)
    def visit_app(self,e): return e.arg1.accept(self)|e.arg2.accept(self)
    def visit_if0(self,e): return e.arg1.accept(self)|e.arg2.accept(self)|e.arg3.accept(self)
    def visit_let(self,e): return {e.arg1}|e.arg2.accept(self)|e.arg3.accept(self)
    def visit_pair(self,e): return e.arg1.accept(self)|e.arg2.accept(self)
    def visit_pfst(self,e): return e.arg1.accept(self)
    def visit_psnd(self,e): return e.arg1.accept(self)

class Compiler(D0ExpVisitor[Term]):
    def __init__(self, source): self.used, self.counter = source.accept(_Names()), 0
    def fresh(self, base="thunk"):
        while True:
            self.counter += 1; n = f"{base}_{self.counter}"
            if n not in self.used: self.used.add(n); return n
    def delay(self, body): return Lam(self.fresh(), body)
    def force_choice(self, condition, yes, no): return apps(condition, self.delay(yes), self.delay(no), church.identity())
    def visit_int(self,e):
        if e.arg1 < 0: raise CompileError(f"negative literal unsupported: {e.arg1}")
        return church.num(e.arg1)
    def visit_btf(self,e): return church.true() if e.arg1 else church.false()
    def visit_var(self,e): return Var(e.arg1)
    def visit_lam(self,e): return Lam(e.arg1, e.arg2.accept(self))
    def visit_app(self,e): return App(e.arg1.accept(self), e.arg2.accept(self))
    def visit_let(self,e): return App(Lam(e.arg1, e.arg3.accept(self)), e.arg2.accept(self))
    def visit_fix(self,e): return App(church.z_combinator(), Lam(e.arg1, Lam(e.arg2, e.arg3.accept(self))))
    def visit_if0(self,e): return self.force_choice(e.arg1.accept(self), e.arg2.accept(self), e.arg3.accept(self))
    def visit_pair(self,e): return apps(church.pair(), e.arg1.accept(self), e.arg2.accept(self))
    def visit_pfst(self,e): return App(church.fst(), e.arg1.accept(self))
    def visit_psnd(self,e): return App(church.snd(), e.arg1.accept(self))
    def visit_op1(self,e):
        value=e.arg1.accept(self)
        if e.name == "not": return App(church.not_(), value)
        raise CompileError(f"unsupported unary operator: {e.name}")
    def visit_op2(self,e):
        left, right = e.arg1.accept(self), e.arg2.accept(self)
        if e.name == "and": return self.force_choice(left, right, church.false())
        if e.name == "or": return self.force_choice(left, church.true(), right)
        ops={"+":church.add, "-":church.sub, "*":church.mul, "<":church.lt, "<=":church.leq, ">":church.gt, ">=":church.geq, "==":church.eq, "!=":church.ne}
        if e.name not in ops: raise CompileError(f"unsupported binary operator: {e.name}")
        return apps(ops[e.name](), left, right)

def compile_expr(source) -> Term:
    term = source.accept(Compiler(source))
    return term
