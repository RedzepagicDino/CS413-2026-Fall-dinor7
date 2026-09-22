import sys

sys.setrecursionlimit(20000)

from lambda0 import *


# ============================================================
# Helpers for constructing LAMBDA0 terms
# ============================================================

def mint(n):
    return T0Mint(n)


def mbool(b):
    return T0Mbtf(b)


def var(x):
    return T0Mvar(x)


def op1(op, t):
    return T0Mop1(op, t)


def op2(op, t1, t2):
    return T0Mop2(op, t1, t2)


def if0(cond, then_term, else_term):
    return T0Mif0(cond, then_term, else_term)


def lam(x, body):
    return T0Mlam(x, body)


def app(t1, t2):
    return T0Mapp(t1, t2)


def pair(t1, t2):
    return T0Mpair(t1, t2)


def fst(t):
    return T0Mpfst(t)


def snd(t):
    return T0Mpsnd(t)


# ============================================================
# Board representation
# ============================================================
#
# ATS2:
#
# (x0, x1, x2, x3, x4, x5, x6, x7)
#
# LAMBDA0:
#
# (x0, (x1, (x2, (x3, (x4, (x5, (x6, x7)))))))
#
# ============================================================

def board_from_values(values):
    assert len(values) == 8

    result = pair(values[6], values[7])

    for index in range(5, -1, -1):
        result = pair(values[index], result)

    return result


def initial_board():
    return board_from_values([
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
    ])


# ============================================================
# Board element helper
# ============================================================

def board_element_term(board_term, index):
    result = board_term

    for _ in range(index):
        result = snd(result)

    if index < 7:
        return fst(result)

    return result


# ============================================================
# board_get
# ============================================================

def board_get_term():
    bd = "bd"
    i = "i"

    result = mint(-1)

    for index in range(7, -1, -1):
        result = if0(
            op2(
                "==",
                var(i),
                mint(index)
            ),
            board_element_term(
                var(bd),
                index
            ),
            result
        )

    return lam(
        bd,
        lam(
            i,
            result
        )
    )


# ============================================================
# board_set
# ============================================================

def board_set_term():
    bd = "bd"
    i = "i"
    j = "j"

    def set_element(index_to_replace):
        values = []

        for index in range(8):
            if index == index_to_replace:
                values.append(var(j))
            else:
                values.append(
                    board_element_term(
                        var(bd),
                        index
                    )
                )

        return board_from_values(values)

    result = var(bd)

    for index in range(7, -1, -1):
        result = if0(
            op2(
                "==",
                var(i),
                mint(index)
            ),
            set_element(index),
            result
        )

    return lam(
        bd,
        lam(
            i,
            lam(
                j,
                result
            )
        )
    )


# ============================================================
# Absolute value
# ============================================================

def abs_term(t):
    return if0(
        op2(
            "<",
            t,
            mint(0)
        ),
        op1("-", t),
        t
    )


# ============================================================
# safety_test1
# ============================================================

def safety_test1_term():
    i0 = "i0"
    j0 = "j0"
    i1 = "i1"
    j1 = "j1"

    different_columns = op2(
        "!=",
        var(j0),
        var(j1)
    )

    row_difference = abs_term(
        op2(
            "-",
            var(i0),
            var(i1)
        )
    )

    column_difference = abs_term(
        op2(
            "-",
            var(j0),
            var(j1)
        )
    )

    different_diagonal = op2(
        "!=",
        row_difference,
        column_difference
    )

    result = if0(
        different_columns,
        different_diagonal,
        mbool(False)
    )

    return lam(
        i0,
        lam(
            j0,
            lam(
                i1,
                lam(
                    j1,
                    result
                )
            )
        )
    )


# ============================================================
# Four-argument representation
# ============================================================
#
# (a,b,c,d) is represented as:
#
# (a, (b, (c, d)))
#
# ============================================================

def args4(a, b, c, d):
    return pair(
        a,
        pair(
            b,
            pair(
                c,
                d
            )
        )
    )


def arg4_0(t):
    return fst(t)


def arg4_1(t):
    return fst(snd(t))


def arg4_2(t):
    return fst(snd(snd(t)))


def arg4_3(t):
    return snd(snd(snd(t)))


# ============================================================
# safety_test2
# ============================================================
#
# Recursive conflict checker.
#
# ============================================================

def safety_test2_term():
    fname = "safety2"
    args = "args"

    i0 = arg4_0(var(args))
    j0 = arg4_1(var(args))
    bd = arg4_2(var(args))
    i = arg4_3(var(args))

    previous_column = app(
        app(
            board_get_term(),
            bd
        ),
        i
    )

    safe_with_current = app(
        app(
            app(
                app(
                    safety_test1_term(),
                    i0
                ),
                j0
            ),
            i
        ),
        previous_column
    )

    recursive_call = app(
        var(fname),
        args4(
            i0,
            j0,
            bd,
            op2(
                "-",
                i,
                mint(1)
            )
        )
    )

    check_previous = if0(
        safe_with_current,
        recursive_call,
        mbool(False)
    )

    body = if0(
        op2(
            ">=",
            i,
            mint(0)
        ),
        check_previous,
        mbool(True)
    )

    return T0Mfix(
        fname,
        args,
        body
    )


# ============================================================
# search
# ============================================================
#
# This is the main recursive eight-queens search.
#
# Arguments:
#
# bd   = current board
# i    = current row
# j    = candidate column
# nsol = number of solutions found
#
# The recursion itself executes inside LAMBDA0 using T0Mfix.
#
# ============================================================

def search_term():
    fname = "search"
    args = "search_args"

    bd = arg4_0(var(args))
    i = arg4_1(var(args))
    j = arg4_2(var(args))
    nsol = arg4_3(var(args))

    # --------------------------------------------------------
    # safety_test2(i, j, bd, i - 1)
    # --------------------------------------------------------

    safe = app(
        safety_test2_term(),
        args4(
            i,
            j,
            bd,
            op2(
                "-",
                i,
                mint(1)
            )
        )
    )

    # --------------------------------------------------------
    # board_set(bd, i, j)
    # --------------------------------------------------------

    bd1 = app(
        app(
            app(
                board_set_term(),
                bd
            ),
            i
        ),
        j
    )

    # --------------------------------------------------------
    # A solution has been completed.
    #
    # ATS2:
    #
    # search(bd, i, j+1, nsol+1)
    #
    # Notice that the original bd is used here because we
    # continue trying columns in the current row.
    # --------------------------------------------------------

    found_solution = app(
        var(fname),
        args4(
            bd,
            i,
            op2(
                "+",
                j,
                mint(1)
            ),
            op2(
                "+",
                nsol,
                mint(1)
            )
        )
    )

    # --------------------------------------------------------
    # Move to next row.
    #
    # search(bd1, i+1, 0, nsol)
    # --------------------------------------------------------

    move_next_row = app(
        var(fname),
        args4(
            bd1,
            op2(
                "+",
                i,
                mint(1)
            ),
            mint(0),
            nsol
        )
    )

    # --------------------------------------------------------
    # If safe:
    #
    #     if i+1 == 8:
    #         solution found
    #     else:
    #         move to next row
    # --------------------------------------------------------

    safe_branch = if0(
        op2(
            "==",
            op2(
                "+",
                i,
                mint(1)
            ),
            mint(8)
        ),
        found_solution,
        move_next_row
    )

    # --------------------------------------------------------
    # Candidate is unsafe:
    #
    # search(bd, i, j+1, nsol)
    # --------------------------------------------------------

    unsafe_branch = app(
        var(fname),
        args4(
            bd,
            i,
            op2(
                "+",
                j,
                mint(1)
            ),
            nsol
        )
    )

    try_column = if0(
        safe,
        safe_branch,
        unsafe_branch
    )

    # --------------------------------------------------------
    # Backtracking:
    #
    # board_get(bd, i-1)
    # --------------------------------------------------------

    previous_row_column = app(
        app(
            board_get_term(),
            bd
        ),
        op2(
            "-",
            i,
            mint(1)
        )
    )

    # --------------------------------------------------------
    # search(
    #     bd,
    #     i-1,
    #     board_get(bd, i-1)+1,
    #     nsol
    # )
    # --------------------------------------------------------

    backtrack = app(
        var(fname),
        args4(
            bd,
            op2(
                "-",
                i,
                mint(1)
            ),
            op2(
                "+",
                previous_row_column,
                mint(1)
            ),
            nsol
        )
    )

    # --------------------------------------------------------
    # If i > 0, backtrack.
    # Otherwise the entire search is finished.
    # --------------------------------------------------------

    exhausted_columns = if0(
        op2(
            ">",
            i,
            mint(0)
        ),
        backtrack,
        nsol
    )

    # --------------------------------------------------------
    # Main:
    #
    # if j < 8:
    #     try current column
    # else:
    #     backtrack / finish
    # --------------------------------------------------------

    body = if0(
        op2(
            "<",
            j,
            mint(8)
        ),
        try_column,
        exhausted_columns
    )

    return T0Mfix(
        fname,
        args,
        body
    )


# ============================================================
# Run the complete eight-queens search
# ============================================================

def queens_program_term():
    return app(
        search_term(),
        args4(
            initial_board(),
            mint(0),
            mint(0),
            mint(0)
        )
    )


def run_queens():
    return t0erm_cbv_evaluate0(
        queens_program_term()
    )


# ============================================================
# Temporary development helpers
# ============================================================

def make_test_board():
    return board_from_values([
        mint(10),
        mint(20),
        mint(30),
        mint(40),
        mint(50),
        mint(60),
        mint(70),
        mint(80),
    ])


def evaluate_board_get(board, index):
    return t0erm_cbv_evaluate0(
        app(
            app(
                board_get_term(),
                board
            ),
            mint(index)
        )
    )


def evaluate_board_set(board, index, value):
    return t0erm_cbv_evaluate0(
        app(
            app(
                app(
                    board_set_term(),
                    board
                ),
                mint(index)
            ),
            mint(value)
        )
    )


def run_safety_test1(i0, j0, i1, j1):
    return t0erm_cbv_evaluate0(
        app(
            app(
                app(
                    app(
                        safety_test1_term(),
                        mint(i0)
                    ),
                    mint(j0)
                ),
                mint(i1)
            ),
            mint(j1)
        )
    )


def run_safety_test2(i0, j0, board, i):
    return t0erm_cbv_evaluate0(
        app(
            safety_test2_term(),
            args4(
                mint(i0),
                mint(j0),
                board,
                mint(i)
            )
        )
    )


# ============================================================
# Tests: board_get
# ============================================================

def test_board_get():
    board = make_test_board()

    assert evaluate_board_get(board, 0) == T0Mint(10)
    assert evaluate_board_get(board, 1) == T0Mint(20)
    assert evaluate_board_get(board, 2) == T0Mint(30)
    assert evaluate_board_get(board, 3) == T0Mint(40)
    assert evaluate_board_get(board, 4) == T0Mint(50)
    assert evaluate_board_get(board, 5) == T0Mint(60)
    assert evaluate_board_get(board, 6) == T0Mint(70)
    assert evaluate_board_get(board, 7) == T0Mint(80)

    assert evaluate_board_get(board, 8) == T0Mint(-1)
    assert evaluate_board_get(board, -1) == T0Mint(-1)


# ============================================================
# Tests: board_set
# ============================================================

def test_board_set_index_zero():
    board = make_test_board()

    result = evaluate_board_set(
        board,
        0,
        99
    )

    expected = board_from_values([
        mint(99),
        mint(20),
        mint(30),
        mint(40),
        mint(50),
        mint(60),
        mint(70),
        mint(80),
    ])

    assert result == expected


def test_board_set_index_seven():
    board = make_test_board()

    result = evaluate_board_set(
        board,
        7,
        99
    )

    expected = board_from_values([
        mint(10),
        mint(20),
        mint(30),
        mint(40),
        mint(50),
        mint(60),
        mint(70),
        mint(99),
    ])

    assert result == expected


def test_board_set_middle():
    board = make_test_board()

    result = evaluate_board_set(
        board,
        4,
        999
    )

    expected = board_from_values([
        mint(10),
        mint(20),
        mint(30),
        mint(40),
        mint(999),
        mint(60),
        mint(70),
        mint(80),
    ])

    assert result == expected


def test_board_set_invalid_index():
    board = make_test_board()

    result = evaluate_board_set(
        board,
        8,
        999
    )

    assert result == board


# ============================================================
# Tests: safety_test1
# ============================================================

def test_safety_test1_safe():
    assert run_safety_test1(
        0, 0,
        1, 2
    ) == T0Mbtf(True)


def test_safety_test1_same_column():
    assert run_safety_test1(
        0, 3,
        5, 3
    ) == T0Mbtf(False)


def test_safety_test1_diagonal():
    assert run_safety_test1(
        0, 1,
        2, 3
    ) == T0Mbtf(False)


def test_safety_test1_other_diagonal():
    assert run_safety_test1(
        1, 4,
        4, 1
    ) == T0Mbtf(False)


# ============================================================
# Tests: safety_test2
# ============================================================

def test_safety_test2_no_previous_queens():
    assert run_safety_test2(
        0,
        4,
        initial_board(),
        -1
    ) == T0Mbtf(True)


def test_safety_test2_safe_against_previous():
    board = board_from_values([
        mint(0),
        mint(2),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
    ])

    assert run_safety_test2(
        2,
        5,
        board,
        1
    ) == T0Mbtf(True)


def test_safety_test2_same_column_conflict():
    board = board_from_values([
        mint(1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
    ])

    assert run_safety_test2(
        1,
        1,
        board,
        0
    ) == T0Mbtf(False)


def test_safety_test2_diagonal_conflict():
    board = board_from_values([
        mint(0),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
    ])

    assert run_safety_test2(
        1,
        1,
        board,
        0
    ) == T0Mbtf(False)


def test_safety_test2_checks_multiple_rows():
    board = board_from_values([
        mint(0),
        mint(4),
        mint(7),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
        mint(-1),
    ])

    assert run_safety_test2(
        3,
        5,
        board,
        2
    ) == T0Mbtf(True)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    test_board_get()
    print("board_get tests passed!")

    test_board_set_index_zero()
    test_board_set_index_seven()
    test_board_set_middle()
    test_board_set_invalid_index()
    print("board_set tests passed!")

    test_safety_test1_safe()
    test_safety_test1_same_column()
    test_safety_test1_diagonal()
    test_safety_test1_other_diagonal()
    print("safety_test1 tests passed!")

    test_safety_test2_no_previous_queens()
    test_safety_test2_safe_against_previous()
    test_safety_test2_same_column_conflict()
    test_safety_test2_diagonal_conflict()
    test_safety_test2_checks_multiple_rows()
    print("safety_test2 tests passed!")

    print("Running complete 8-queens search...")
    result = run_queens()
    print("Number of solutions:", result.arg1)