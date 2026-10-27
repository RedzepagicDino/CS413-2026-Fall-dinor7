# Assignment 06: Extended LAMBDA compiler

Run these commands from `assigns/06/MySolution` with Python 3.12 or newer:

```sh
python3.12 -m unittest -v
python3.12 demo.py
```

No third-party dependencies are required. `target.py` defines the pure target
AST, printing, free variables, capture-avoiding substitution, and weak CBV
reduction. `church.py` supplies closed encodings. `evaluator.py` is the shared
source/target evaluator entry point; it never imports the compiler. `compiler.py`
implements the required visitor. `observe.py` contains bounded pure observation
contexts. `demo.py` runs the required examples and `test_project.py` is the
automated regression suite.

The demo uses an execution/observation budget of 1,000,000 beta-value steps for
terminating examples and 200 for intended exhaustion demonstrations. Exhaustion
means only that the configured budget was spent; it is not a proof of divergence.
Target execution is restricted to closed terms and rejects a free variable.

`slides.pdf` and a 15–20 minute, face-visible presentation recording are still
required submission artifacts. Create them from the design and demo results;
this repository intentionally does not include a fabricated recording.
