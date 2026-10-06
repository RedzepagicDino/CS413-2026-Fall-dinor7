"""Restricted reader for the d0exp constructor notation; never uses eval()."""
import ast
from . import lambda1 as L

CLASSES = {name: getattr(L, name) for name in (
    "D0Eint", "D0Ebtf", "D0Eop1", "D0Eop2", "D0Evar", "D0Elam", "D0Efix",
    "D0Eapp", "D0Eif0", "D0Elet", "D0Epair", "D0Epfst", "D0Epsnd")}

def read_source(source: str) -> L.d0exp:
    """Parse one constructor expression, with literal arguments only."""
    try:
        node = ast.parse(source, mode="eval").body
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"Invalid constructor input: {exc.msg if hasattr(exc, 'msg') else exc}") from exc
    value = _read(node)
    if not isinstance(value, L.D0E000):
        raise ValueError("Input must construct a d0exp expression")
    return value

def _read(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, bool, str)):
        return node.value
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.keywords:
        raise ValueError("Only positional calls to approved constructors and literal arguments are allowed")
    cls = CLASSES.get(node.func.id)
    if cls is None:
        raise ValueError(f"Constructor {node.func.id!r} is not allowed")
    try:
        return cls(*[_read(arg) for arg in node.args])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {node.func.id} arguments: {exc}") from exc
