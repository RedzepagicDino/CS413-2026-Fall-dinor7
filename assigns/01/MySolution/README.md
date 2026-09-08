# Eight Queens Puzzle

This project translates an ATS implementation of the Eight Queens Puzzle into Python 3. The original program uses a tuple containing eight integers to represent the board, where each integer represents the column containing a queen in that row. The Python version preserves this representation and the original depth-first search approach as closely as possible.

## Files

- `queens.dats` — Original ATS source program.
- `queens.py` — Python 3 translation of the ATS program.
- `test_queens.py` — Tests for the Python translation.
- `AI-TRANSCRIPT.md` — Record of the AI-assisted development process.

## Running the Python Program

From the repository root:

```bash
python3 assigns/01/MySolution/queens.py

The program prints all solutions to the Eight Queens Puzzle and reports:

Total solutions: 92
Running the Tests

From the repository root:

python3 assigns/01/MySolution/test_queens.py

The tests check queen safety, board access, board updates, and the complete search. All tests passed successfully.

Testing and Review

The initial Python translation used direct recursion for the search function. When tested, it produced a RecursionError because Python does not perform tail-call optimization. I corrected this by implementing search with an explicit stack, which preserves the depth-first search behavior without depending on Python's recursion limit.

I attempted to compile the original ATS program locally, but the patscc compiler was not available and my attempt to build ATS-Postiats from its development source did not complete. Therefore, I did not claim a local ATS execution comparison. The Python program was tested independently and produced the expected 92 solutions documented by the original Eight Queens example.

AI Reflection

AI was useful for translating the ATS program into Python while preserving the structure and behavior of the original code. The initial translation correctly reproduced many important parts of the program, including the tuple-based board representation, board access and update functions, safety checks, and depth-first search. However, the initial translation also demonstrated why AI-generated code needs to be reviewed and tested rather than accepted automatically.

The most significant problem was the use of direct recursion in Python for the search function. Although the original ATS implementation uses tail-recursive functions, Python does not perform tail-call optimization. As a result, the first Python version failed with a RecursionError. I had to understand the difference between ATS and Python recursion and ask AI to correct the implementation. The final version uses an explicit stack to simulate the recursive search while avoiding Python's recursion limit.

Testing was important because the initial code appeared reasonable but failed when actually executed. After the correction, I tested individual functions as well as the complete search and confirmed that the program finds all 92 solutions. I also tested boundary behavior such as an invalid board index.

Overall, AI significantly reduced the amount of time needed to create the translation, but it did not eliminate the need for programming knowledge. I still needed to understand the original algorithm, interpret the error message, evaluate AI's proposed correction, and verify the result through testing. This assignment showed me that AI-generated code is most useful as a starting point that must be reviewed, tested, and corrected by the programmer.