import queens


def test_safety_test1():
    # Same column: unsafe
    assert queens.safety_test1(0, 0, 1, 0) is False

    # Same diagonal: unsafe
    assert queens.safety_test1(0, 0, 1, 1) is False

    # Different row and column, not diagonal: safe
    assert queens.safety_test1(0, 0, 1, 2) is True


def test_board_get():
    board = (0, 1, 2, 3, 4, 5, 6, 7)

    assert queens.board_get(board, 0) == 0
    assert queens.board_get(board, 7) == 7

    # Invalid index should return -1
    assert queens.board_get(board, 8) == -1


def test_board_set():
    board = (0, 0, 0, 0, 0, 0, 0, 0)

    updated = queens.board_set(board, 3, 5)

    assert updated == (0, 0, 0, 5, 0, 0, 0, 0)

    # Original board should remain unchanged
    assert board == (0, 0, 0, 0, 0, 0, 0, 0)


def test_full_search():
    board = (0, 0, 0, 0, 0, 0, 0, 0)

    solutions = queens.search(board, 0, 0, 0)

    assert solutions == 92


if __name__ == "__main__":
    test_safety_test1()
    test_board_get()
    test_board_set()
    test_full_search()
    print("All tests passed.")