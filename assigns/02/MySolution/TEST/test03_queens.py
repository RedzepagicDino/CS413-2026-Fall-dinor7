from lambda0 import (
    T0Mint,
    T0Mbtf,
    T0Mpair,
    T0Mfix,
)

from queens_lambda0 import (
    initial_board,
    board_from_values,
    board_get_term,
    board_set_term,
    safety_test1_term,
    safety_test2_term,
    search_term,
    run_safety_test1,
    run_safety_test2,
    evaluate_board_get,
    evaluate_board_set,
    run_queens,
)


# ------------------------------------------------------------
# Board representation tests
# ------------------------------------------------------------

def test_board_get_all_positions():
    board = board_from_values([
        T0Mint(10),
        T0Mint(20),
        T0Mint(30),
        T0Mint(40),
        T0Mint(50),
        T0Mint(60),
        T0Mint(70),
        T0Mint(80),
    ])

    expected = [10, 20, 30, 40, 50, 60, 70, 80]

    for index, value in enumerate(expected):
        assert evaluate_board_get(board, index) == T0Mint(value)


def test_initial_board():
    board = initial_board()

    for index in range(8):
        assert evaluate_board_get(board, index) == T0Mint(-1)


def test_board_set_first_position():
    board = initial_board()

    new_board = evaluate_board_set(board, 0, 5)

    assert evaluate_board_get(new_board, 0) == T0Mint(5)

    for index in range(1, 8):
        assert evaluate_board_get(new_board, index) == T0Mint(-1)


def test_board_set_middle_position():
    board = initial_board()

    new_board = evaluate_board_set(board, 4, 6)

    assert evaluate_board_get(new_board, 4) == T0Mint(6)

    for index in range(8):
        if index != 4:
            assert evaluate_board_get(new_board, index) == T0Mint(-1)


def test_board_set_last_position():
    board = initial_board()

    new_board = evaluate_board_set(board, 7, 3)

    assert evaluate_board_get(new_board, 7) == T0Mint(3)

    for index in range(7):
        assert evaluate_board_get(new_board, index) == T0Mint(-1)


# ------------------------------------------------------------
# safety_test1 tests
# ------------------------------------------------------------

def test_safety_test1_safe():
    # Queens at (0, 0) and (1, 2) do not conflict.
    assert run_safety_test1(0, 0, 1, 2) == T0Mbtf(True)


def test_safety_test1_same_column():
    assert run_safety_test1(0, 3, 4, 3) == T0Mbtf(False)


def test_safety_test1_diagonal():
    assert run_safety_test1(0, 0, 1, 1) == T0Mbtf(False)


def test_safety_test1_other_diagonal():
    assert run_safety_test1(0, 4, 2, 2) == T0Mbtf(False)


# ------------------------------------------------------------
# safety_test2 tests
# ------------------------------------------------------------

def test_safety_test2_first_row():
    board = initial_board()

    # No earlier rows need to be checked.
    assert (
        run_safety_test2(0, 4, board, -1)
        == T0Mbtf(True)
    )


def test_safety_test2_safe_against_previous_rows():
    board = board_from_values([
        T0Mint(0),
        T0Mint(2),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
    ])

    assert (
        run_safety_test2(2, 5, board, 1)
        == T0Mbtf(True)
    )


def test_safety_test2_same_column_conflict():
    board = board_from_values([
        T0Mint(1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
    ])

    assert (
        run_safety_test2(1, 1, board, 0)
        == T0Mbtf(False)
    )


def test_safety_test2_diagonal_conflict():
    board = board_from_values([
        T0Mint(0),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
    ])

    assert (
        run_safety_test2(1, 1, board, 0)
        == T0Mbtf(False)
    )


def test_safety_test2_multiple_previous_rows():
    board = board_from_values([
        T0Mint(0),
        T0Mint(4),
        T0Mint(7),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
        T0Mint(-1),
    ])

    assert (
        run_safety_test2(3, 5, board, 2)
        == T0Mbtf(True)
    )


# ------------------------------------------------------------
# AST translation tests
# ------------------------------------------------------------

def test_search_is_recursive_lambda_term():
    # The translated search must use LAMBDA0 recursion,
    # rather than performing the search directly in Python.
    assert isinstance(search_term(), T0Mfix)


def test_safety_test2_is_recursive_lambda_term():
    assert isinstance(safety_test2_term(), T0Mfix)


# ------------------------------------------------------------
# Complete eight-queens search
# ------------------------------------------------------------

def test_complete_eight_queens_search():
    result = run_queens()

    assert isinstance(result, T0Mint)
    assert result.arg1 == 92