import pytest

from lambda0 import (
    T0Mvar,
    T0Mint,
    T0Mbtf,
    T0Mlam,
    T0Mfix,
    T0Mapp,
    T0Mop1,
    T0Mop2,
    T0Mif0,
    T0Mpair,
    T0Mpfst,
    T0Mpsnd,
    t0erm_size,
    t0erm_fvset,
    t0erm_subst0,
    t0erm_cbv_evaluate0,
)


# ----------------------------------------------------------------------
# t0erm_size
# ----------------------------------------------------------------------

def test_size_pair():
    term = T0Mpair(T0Mint(1), T0Mint(2))
    assert t0erm_size(term) == 3


def test_size_projections():
    pair = T0Mpair(T0Mint(1), T0Mint(2))

    assert t0erm_size(T0Mpfst(pair)) == 4
    assert t0erm_size(T0Mpsnd(pair)) == 4


def test_size_nested_pairs_and_projections():
    term = T0Mpfst(
        T0Mpair(
            T0Mpair(T0Mint(1), T0Mint(2)),
            T0Mpsnd(T0Mpair(T0Mint(3), T0Mint(4)))
        )
    )

    assert t0erm_size(term) == 9


# ----------------------------------------------------------------------
# t0erm_fvset
# ----------------------------------------------------------------------

def test_fvset_pair():
    term = T0Mpair(T0Mvar("x"), T0Mvar("y"))

    assert t0erm_fvset(term) == frozenset({"x", "y"})


def test_fvset_projection():
    term = T0Mpfst(
        T0Mpair(T0Mvar("x"), T0Mvar("y"))
    )

    assert t0erm_fvset(term) == frozenset({"x", "y"})


def test_fvset_nested_pair():
    term = T0Mpair(
        T0Mvar("x"),
        T0Mpair(T0Mvar("y"), T0Mvar("z"))
    )

    assert t0erm_fvset(term) == frozenset({"x", "y", "z"})


def test_fvset_under_lambda():
    term = T0Mlam(
        "x",
        T0Mpair(T0Mvar("x"), T0Mvar("y"))
    )

    assert t0erm_fvset(term) == frozenset({"y"})


def test_fvset_under_fix():
    term = T0Mfix(
        "f",
        "x",
        T0Mpair(T0Mvar("f"), T0Mvar("y"))
    )

    assert t0erm_fvset(term) == frozenset({"y"})


# ----------------------------------------------------------------------
# t0erm_subst0
# ----------------------------------------------------------------------

def test_substitution_in_both_pair_components():
    term = T0Mpair(T0Mvar("x"), T0Mvar("x"))

    result = t0erm_subst0(term, "x", T0Mint(42))

    assert result == T0Mpair(T0Mint(42), T0Mint(42))


def test_substitution_in_projection():
    term = T0Mpfst(T0Mvar("x"))

    result = t0erm_subst0(term, "x", T0Mpair(T0Mint(1), T0Mint(2)))

    assert result == T0Mpfst(
        T0Mpair(T0Mint(1), T0Mint(2))
    )


def test_substitution_nested_pair():
    term = T0Mpair(
        T0Mvar("x"),
        T0Mpfst(T0Mpair(T0Mvar("x"), T0Mint(5)))
    )

    result = t0erm_subst0(term, "x", T0Mint(10))

    assert result == T0Mpair(
        T0Mint(10),
        T0Mpfst(T0Mpair(T0Mint(10), T0Mint(5)))
    )


def test_substitution_respects_lambda_binder():
    term = T0Mlam(
        "x",
        T0Mpair(T0Mvar("x"), T0Mvar("y"))
    )

    result = t0erm_subst0(term, "x", T0Mint(42))

    assert result == term


def test_substitution_under_lambda():
    term = T0Mlam(
        "y",
        T0Mpair(T0Mvar("x"), T0Mvar("y"))
    )

    result = t0erm_subst0(term, "x", T0Mint(42))

    assert result == T0Mlam(
        "y",
        T0Mpair(T0Mint(42), T0Mvar("y"))
    )


def test_substitution_respects_fix_binders():
    term = T0Mfix(
        "f",
        "x",
        T0Mpair(T0Mvar("f"), T0Mvar("x"))
    )

    assert t0erm_subst0(term, "f", T0Mint(1)) == term
    assert t0erm_subst0(term, "x", T0Mint(2)) == term


# ----------------------------------------------------------------------
# t0erm_cbv_evaluate0 -- pairs and projections
# ----------------------------------------------------------------------

def test_pair_evaluation():
    term = T0Mpair(
        T0Mop2("+", T0Mint(1), T0Mint(2)),
        T0Mop2("*", T0Mint(3), T0Mint(4))
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mpair(T0Mint(3), T0Mint(12))


def test_first_projection():
    term = T0Mpfst(
        T0Mpair(
            T0Mop2("+", T0Mint(1), T0Mint(2)),
            T0Mop2("*", T0Mint(3), T0Mint(4))
        )
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mint(3)


def test_second_projection():
    term = T0Mpsnd(
        T0Mpair(
            T0Mop2("+", T0Mint(1), T0Mint(2)),
            T0Mop2("+", T0Mint(2), T0Mint(3))
        )
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mint(5)


def test_nested_pairs():
    term = T0Mpsnd(
        T0Mpair(
            T0Mint(1),
            T0Mpair(T0Mint(2), T0Mint(3))
        )
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mpair(T0Mint(2), T0Mint(3))


def test_pair_with_different_value_kinds():
    term = T0Mpair(
        T0Mint(42),
        T0Mlam("x", T0Mvar("x"))
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mpair(
        T0Mint(42),
        T0Mlam("x", T0Mvar("x"))
    )


def test_pair_components_evaluate_left_to_right():
    term = T0Mpair(
        T0Mop2("+", T0Mint(1), T0Mint(2)),
        T0Mop2("*", T0Mint(3), T0Mint(4))
    )

    result = t0erm_cbv_evaluate0(term)

    assert result == T0Mpair(T0Mint(3), T0Mint(12))


def test_unselected_pair_component_is_still_evaluated():
    term = T0Mpfst(
        T0Mpair(
            T0Mint(1),
            T0Mop2("/", T0Mint(1), T0Mint(0))
        )
    )

    with pytest.raises(ZeroDivisionError):
        t0erm_cbv_evaluate0(term)


def test_projection_of_non_pair_raises_type_error():
    with pytest.raises(TypeError):
        t0erm_cbv_evaluate0(T0Mpfst(T0Mint(42)))

    with pytest.raises(TypeError):
        t0erm_cbv_evaluate0(T0Mpsnd(T0Mbtf(True)))


# ----------------------------------------------------------------------
# Functions accepting and returning pairs
# ----------------------------------------------------------------------

def test_function_accepting_pair():
    identity = T0Mlam("p", T0Mpfst(T0Mvar("p")))

    application = T0Mapp(
        identity,
        T0Mpair(T0Mint(10), T0Mint(20))
    )

    result = t0erm_cbv_evaluate0(application)

    assert result == T0Mint(10)


def test_function_returning_pair():
    make_pair = T0Mlam(
        "x",
        T0Mpair(T0Mvar("x"), T0Mint(99))
    )

    application = T0Mapp(
        make_pair,
        T0Mint(42)
    )

    result = t0erm_cbv_evaluate0(application)

    assert result == T0Mpair(T0Mint(42), T0Mint(99))


def test_function_composing_pair_operations():
    get_second = T0Mlam(
        "p",
        T0Mpsnd(T0Mvar("p"))
    )

    application = T0Mapp(
        get_second,
        T0Mpair(
            T0Mint(100),
            T0Mop2("+", T0Mint(20), T0Mint(22))
        )
    )

    result = t0erm_cbv_evaluate0(application)

    assert result == T0Mint(42)
