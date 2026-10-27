"""Closed Church encodings, represented solely with target AST nodes."""
from target import Var, Lam, App, Term, apps, lams

def num(n: int) -> Term:
    if n < 0: raise ValueError("Church naturals are nonnegative")
    body: Term = Var("z")
    for _ in range(n): body = App(Var("s"), body)
    return lams(["s", "z"], body)

def true() -> Term: return lams(["t", "f"], Var("t"))
def false() -> Term: return lams(["t", "f"], Var("f"))
def identity() -> Term: return Lam("w", Var("w"))
def pair() -> Term: return lams(["a", "b", "p"], apps(Var("p"), Var("a"), Var("b")))
def fst() -> Term: return Lam("p", App(Var("p"), lams(["a", "b"], Var("a"))))
def snd() -> Term: return Lam("p", App(Var("p"), lams(["a", "b"], Var("b"))))
def succ() -> Term: return lams(["n", "s", "z"], App(Var("s"), apps(Var("n"), Var("s"), Var("z"))))

# pred n s z = n (lam g. lam h. h (g s)) (lam u. z) (lam u. u)
def pred() -> Term:
    return lams(["n", "s", "z"], apps(Var("n"), lams(["g", "h"], App(Var("h"), App(Var("g"), Var("s")))), Lam("u", Var("z")), Lam("u", Var("u"))))
def iszero() -> Term: return Lam("n", apps(Var("n"), Lam("x", false()), true()))
def add() -> Term: return lams(["m", "n", "s", "z"], apps(Var("m"), Var("s"), apps(Var("n"), Var("s"), Var("z"))))
def mul() -> Term: return lams(["m", "n", "s"], App(Var("m"), App(Var("n"), Var("s"))))
def sub() -> Term: return lams(["m", "n"], apps(Var("n"), pred(), Var("m")))
def not_() -> Term: return Lam("b", apps(Var("b"), false(), true()))
def and_() -> Term: return lams(["p", "q"], apps(Var("p"), Var("q"), false()))
def or_() -> Term: return lams(["p", "q"], apps(Var("p"), true(), Var("q")))
def leq() -> Term: return lams(["m", "n"], App(iszero(), apps(sub(), Var("m"), Var("n"))))
def geq() -> Term: return lams(["m", "n"], App(iszero(), apps(sub(), Var("n"), Var("m"))))
def eq() -> Term: return lams(["m", "n"], apps(and_(), apps(leq(), Var("m"), Var("n")), apps(leq(), Var("n"), Var("m"))))
def lt() -> Term: return lams(["m", "n"], apps(not_(), apps(leq(), Var("n"), Var("m"))))
def gt() -> Term: return lams(["m", "n"], apps(not_(), apps(leq(), Var("m"), Var("n"))))
def ne() -> Term: return lams(["m", "n"], App(not_(), apps(eq(), Var("m"), Var("n"))))

def z_combinator() -> Term:
    # Z = lam g. (lam x. g (lam v. x x v)) (lam x. g (lam v. x x v))
    inner = Lam("x", App(Var("g"), Lam("v", apps(Var("x"), Var("x"), Var("v")))))
    return Lam("g", App(inner, inner))
