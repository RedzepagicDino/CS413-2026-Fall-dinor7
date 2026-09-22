# CS413 Assignment 2

## Overview

This submission extends the provided LAMBDA0 interpreter with support for pairs and projections and translates an ATS2 eight-queens program into a LAMBDA0 abstract syntax tree.

The original ATS2 program used for the translation is included as:

`queens_copy.dats`

The translated program is implemented in:

`queens_lambda0.py`

The search algorithm and queen-conflict checking are represented as LAMBDA0 terms and are evaluated by `t0erm_cbv_evaluate0`. Python helper functions are used to construct the AST, run tests, and inspect results, but they do not perform the eight-queens search themselves.

## Pair and Projection Extensions

I extended `lambda0.py` to support the following constructors:

* `T0Mpair(t1, t2)`
* `T0Mpfst(t1)`
* `T0Mpsnd(t1)`

Support for these constructors was added to:

* `t0erm_size`
* `t0erm_fvset`
* `t0erm_subst0`
* `t0erm_cbv_evaluate0`

For `t0erm_size`, a pair or projection counts as one AST node in addition to the sizes of its subterms.

For `t0erm_fvset`, both components of a pair are checked for free variables. A projection has the same free variables as its operand.

For `t0erm_subst0`, substitution recursively enters both components of a pair and the operand of a projection. The existing binding behavior for lambda expressions and recursive functions is preserved.

## Call-by-Value Pair Evaluation

Pairs use strict call-by-value evaluation. For:

`T0Mpair(t1, t2)`

`t1` is evaluated first, followed by `t2`. The resulting pair contains both evaluated values.

This also means that both components are evaluated even when a projection only uses one component. For example, projecting the first component of a pair does not prevent an error in the second component from occurring.

`T0Mpfst` and `T0Mpsnd` first evaluate their operand. If the resulting value is not a pair, the evaluator raises `TypeError`.

## Additional Primitive Operations

The eight-queens translation requires integer comparisons. The interpreter supports the following comparison operators:

* `<`
* `>`
* `<=`
* `>=`
* `==`
* `!=`

Comparisons between integers return `T0Mbtf` values so that their results can be used as conditions in `T0Mif0`.

## ATS2 to LAMBDA0 Translation

The original ATS2 program represents a board as a tuple of eight integers. Each position represents a row, and the integer stored at that position represents the column containing the queen.

In LAMBDA0, I represent the eight-element board using nested pairs. Conceptually, a board containing:

`x0, x1, x2, x3, x4, x5, x6, x7`

is represented as:

`(x0, (x1, (x2, (x3, (x4, (x5, (x6, x7)))))))`

This representation allows the program to access board positions using `T0Mpfst` and `T0Mpsnd`.

### board_get

The ATS2 `board_get` function is translated into a LAMBDA0 function constructed with `T0Mlam`.

It checks the requested index and uses first and second projections to obtain the corresponding element from the nested-pair board representation.

### board_set

The ATS2 `board_set` function is also translated using `T0Mlam`.

Because LAMBDA0 pairs are immutable, updating a position constructs a new nested-pair board. The selected position contains the new value while all other positions are taken from the original board.

### safety_test1

`safety_test1` determines whether two queens conflict.

Two queens are safe when:

1. They are in different columns.
2. The absolute difference between their row positions is different from the absolute difference between their column positions.

The translated function uses LAMBDA0 arithmetic, comparisons, conditionals, lambdas, and applications.

### safety_test2

`safety_test2` recursively checks a proposed queen against the queens already placed in previous rows.

This function is represented with `T0Mfix`, allowing the recursion to execute inside the LAMBDA0 interpreter.

If the proposed queen conflicts with an earlier queen, the function returns `T0Mbtf(False)`. If all previous queens are checked without a conflict, it returns `T0Mbtf(True)`.

### search

The main `search` function implements the ATS2 backtracking algorithm.

It is represented using `T0Mfix` and receives the current board, row, column, and number of solutions as its state.

The search attempts columns in the current row. When a safe position is found, it constructs an updated board and continues to the next row. If all columns in a row have been exhausted, the search backtracks to the previous row and continues with the next available column.

When a queen is successf
