N = 8


def print_dots(i):
    if i > 0:
        print(". ", end="")
        print_dots(i - 1)


def print_row(i):
    print_dots(i)
    print("Q ", end="")
    print_dots(N - i - 1)
    print()


def print_board(bd):
    print_row(bd[0])
    print_row(bd[1])
    print_row(bd[2])
    print_row(bd[3])
    print_row(bd[4])
    print_row(bd[5])
    print_row(bd[6])
    print_row(bd[7])
    print()


def board_get(bd, i):
    if i == 0:
        return bd[0]
    elif i == 1:
        return bd[1]
    elif i == 2:
        return bd[2]
    elif i == 3:
        return bd[3]
    elif i == 4:
        return bd[4]
    elif i == 5:
        return bd[5]
    elif i == 6:
        return bd[6]
    elif i == 7:
        return bd[7]
    else:
        return -1


def board_set(bd, i, j):
    board = list(bd)

    if i == 0:
        board[0] = j
    elif i == 1:
        board[1] = j
    elif i == 2:
        board[2] = j
    elif i == 3:
        board[3] = j
    elif i == 4:
        board[4] = j
    elif i == 5:
        board[5] = j
    elif i == 6:
        board[6] = j
    elif i == 7:
        board[7] = j
    else:
        return bd

    return tuple(board)


def safety_test1(i0, j0, i1, j1):
    return j0 != j1 and abs(i0 - i1) != abs(j0 - j1)


def safety_test2(i0, j0, bd, i):
    if i >= 0:
        if safety_test1(i0, j0, i, board_get(bd, i)):
            return safety_test2(i0, j0, bd, i - 1)
        else:
            return False
    else:
        return True


def search(bd, i, j, nsol):
    stack = [(bd, i, j, nsol)]

    while stack:
        bd, i, j, nsol = stack.pop()

        if j < N:
            test = safety_test2(i, j, bd, i - 1)

            if test:
                bd1 = board_set(bd, i, j)

                if i + 1 == N:
                    print(f"Solution #{nsol + 1}:\n")
                    print_board(bd1)

                    # Equivalent to:
                    # search(bd, i, j + 1, nsol + 1)
                    stack.append((bd, i, j + 1, nsol + 1))
                else:
                    # Equivalent to:
                    # search(bd1, i + 1, 0, nsol)
                    stack.append((bd1, i + 1, 0, nsol))
            else:
                # Equivalent to:
                # search(bd, i, j + 1, nsol)
                stack.append((bd, i, j + 1, nsol))

        else:
            if i > 0:
                # Equivalent to:
                # search(bd, i - 1, board_get(bd, i - 1) + 1, nsol)
                stack.append(
                    (bd, i - 1, board_get(bd, i - 1) + 1, nsol)
                )
            else:
                return nsol

    return nsol


if __name__ == "__main__":
    board = (0, 0, 0, 0, 0, 0, 0, 0)
    solutions = search(board, 0, 0, 0)
    print(f"Total solutions: {solutions}")