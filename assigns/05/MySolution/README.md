# Assignment 5

Requires Python 3.12+ and pytest. From this directory, run `python3.12 -m unittest -v test_unittest.py` for the standard-library suite, or install pytest in a virtual environment with `python3.12 -m venv .venv`, activate it, run `.venv/bin/pip install pytest`, and run `.venv/bin/python -m pytest -q test_pytest.py` for the independent pytest suite. Do not commit `.venv/`.

`d0exp_pretty` sends an expression to `PrettyPrintVisitor`, whose result type is `str`. It reconstructs every constructor's required concrete notation without evaluating child expressions. `d0exp_substitute` sends the input to `SubstitutionVisitor`, whose result type is an AST. The substitution target, replacement free-variable set, and fresh-name generator are visitor context; each recursive edge uses `accept`.

At a lambda, fix, or let body, substitution stops when that binder shadows the target. Otherwise, a binder that appears free in the replacement is alpha-renamed only if the target occurs free in its scope. `RenameVisitor` is another visitor: it changes occurrences bound by the current binder while stopping at nested binders that shadow the old name. Let initializers are traversed separately because the let name does not bind there. A fix treats equal function and parameter names as parameter-shadowing, matching the supplied evaluator. This makes insertion of a replacement capture-avoiding while neither evaluating nor mutating input trees.

Fresh names use deterministic `base_1`, `base_2`, ... spelling. The generator avoids every variable/binder name in both inputs, the target name, and all previously generated names. Adding these operations only adds visitors; adding a new AST constructor would instead require adding an `accept` method and a method to every existing visitor.

Example: `d0exp_pretty(d0exp_substitute(D0Elam('y', D0Evar('x')), 'x', D0Evar('y')))` returns `(lam y_1. y)`.
