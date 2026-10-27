# Design

## Representation and evaluation

The target language has only `Var(name)`, `Lam(name, body)`, and `App(fn,arg)`.
`target.py` prints these as `x`, `(lam x. body)`, and `(fn arg)`. Its reducer is
weak, deterministic, left-to-right call-by-value: it evaluates the function,
then the argument, and contracts only `(lam x. body) value`. It never reduces
inside a lambda. A completed lambda consequently needs zero steps, even at
budget zero. The reducer reports both completion and the number of beta-value
steps; if another contraction is necessary after the budget is spent, it reports
exhaustion. Target execution rejects open terms, although free-variable analysis,
substitution, and compilation support them.

`evaluator.py` has one public `evaluate` dispatch point. For target syntax it
uses the reducer; for supplied source AST nodes it evaluates source expressions
with lexical environments, closures, pairs, arithmetic, and short-circuiting.
The source evaluator is not imported by the compiler and compilation never calls
it. This keeps translation separate from execution.

## Encodings

Naturals are Church iterators `lam s. lam z. s^n z`; booleans are selectors;
pairs are `lam a. lam b. lam p. p a b`. All builders in `church.py` expand to
closed target ASTs. Addition and multiplication compose iterators. Truncated
subtraction iterates predecessor. The predecessor is the standard threaded-state
construction: `pred n s z = n (lam g. lam h. h (g s)) (lam u. z) (lam u. u)`.
The first state supplies zero and later states delay one additional `s`, so zero
maps to zero. Comparisons are built from subtraction and zero testing, rather
than Python arithmetic. Recursion uses the call-by-value Z combinator, not Y.

Results are decoded by pure observation contexts. Naturals receive a step and a
base that construct a finite lambda spine, which Python only counts structurally.
Booleans choose between distinct closed markers. Pairs are first evaluated then
projected with Church projections before recursively observing their components.

## Translation rules

With `I = lam w. w`, and fresh thunk names `u` and `v`:

```
C[x] = x                         C[n] = NUM(n)
C[true/false] = TRUE/FALSE       C[lam x.e] = lam x.C[e]
C[e1 e2] = C[e1] C[e2]           C[let x=e1 in e2] = (lam x.C[e2]) C[e1]
C[if c then t else f] = C[c] (lam u.C[t]) (lam v.C[f]) I
C[fix f(x).e] = Z (lam f. lam x.C[e])
C[pair(a,b)] = PAIR C[a] C[b]    C[fst e] = FST C[e]
C[snd e] = SND C[e]
C[e1 op e2] = OP C[e1] C[e2]
```

`not`, arithmetic, and comparisons use their corresponding closed Church
combinators. `and` is `C[a] (lam u.C[b]) (lam v.FALSE) I`; `or` is
`C[a] (lam u.TRUE) (lam v.C[b]) I`. Delayed branches are essential because CBV
would otherwise evaluate both branches before the boolean selected one.

The compiler is a `D0ExpVisitor`. It translates every child before assembling
the enclosing pure term, so invalid literals and unsupported operators are
rejected even in unselected branches. For every compilation a deterministic
counter produces `thunk_1`, `thunk_2`, and so on, skipping every spelling found
in the source AST. Thus generated thunks cannot capture a source free name.
Encoding binders occur within closed combinators and do not surround translated
source syntax. The resulting free-variable set is therefore the source set.

## Scope, validation, and design tradeoffs

The implementation deliberately keeps source validation separate from source
evaluation. A source program is checked while it is translated, rather than
only when a particular path happens to run. For example, a negative literal in
the unused branch of an `if` still causes a compilation error. This is useful
because the project language includes only natural-number literals, and it
prevents the compiler from silently accepting source syntax that has no stated
translation. Unsupported unary and binary operator spellings are rejected in
the same way. The implementation assumes that accepted source programs are
well typed, as permitted by the assignment; it does not try to infer types or
preserve every possible source type error.

There are two different kinds of values in this project. The source evaluator
uses ordinary host-language values such as Python integers, booleans, pairs,
and closures. The target evaluator uses only lambda terms, where a lambda
abstraction is the only value. This split is intentional. It makes it possible
to compare a simple source result with a decoded target result without letting
the target reducer cheat by recognizing a Church numeral and using Python
arithmetic. The target evaluator imports only the target representation and
substitution operation. It does not import the compiler and has no special case
for numbers, booleans, pairs, or any other encoding.

The main tradeoff is readability and correctness over runtime performance.
Church encodings are much more expensive than native numbers. A small source
expression can expand to a large target term, and multiplication, predecessor,
and recursive programs may require many beta-value steps. The project records
the step count and accepts a caller-provided budget instead of claiming that it
can efficiently run arbitrary lambda terms. This is appropriate for a compiler
demonstration because the generated program remains inspectable and every
operation follows the same target-language semantics. A production evaluator
could use sharing, closures, or graph reduction, but those optimizations would
make the central reduction behavior harder to demonstrate.

Another deliberate tradeoff is restricting target execution to closed terms.
Compilation itself supports open expressions, and the compiler verifies free
variable preservation. However, attempting to execute a target term with a
free variable produces a clear error because there is no target environment
interface in this reducer. This keeps the execution contract small while still
testing the important lexical-scope property. Similarly, the observers require
the caller to specify the expected kind. Church zero and Church false have the
same lambda shape, so an observer cannot reliably guess whether an arbitrary
term should be read as a natural or a boolean.

## Testing strategy

The automated tests are organized around properties that are easy to get wrong
in a lambda-calculus implementation. Direct substitution tests cover both
shadowing and the capture hazard where replacing `x` with `y` inside
`lam y. x` must rename the binder. Reducer tests cover zero-step lambda values,
left-to-right evaluation, the boundary between completion and exhaustion, and
the rule that lambda bodies remain unevaluated. Encoding tests independently
check Church zero, predecessor of zero, closedness of library terms, booleans,
arithmetic, and comparisons.

Compiler tests use source programs that exercise every required constructor.
They include nested lets, lambdas, pairs, projections, conditionals, both
boolean operators, open expressions, and coincident `fix` binder names.
Short-circuit tests confirm that `false and LOOP` and `true or LOOP` finish,
while strict contexts such as an ordinary function argument, a let initializer,
or either pair component use up the target budget. The demonstration collection
then provides end-to-end examples for arithmetic, pairs, higher-order
functions, recursion, and intended divergence. In each terminating case, the
source-side answer is compared with a decoded result from the compiled term.

## Correctness claim

The intended claim is the following: for a closed, well-typed program in the
required source subset that evaluates to a natural number, boolean, or finite
pair, compiling the program and observing its completed target result produces
the same data, given sufficiently large execution and observation budgets.

The claim is plausible by structural reasoning over source expressions.
Variables and lambdas preserve their binding structure directly. Application
preserves call-by-value order because the target reducer evaluates the function
and argument before substitution. A let is compiled as lambda application, so
its initializer is evaluated exactly once before its body receives the value.
Pairs preserve left-to-right strictness because their Church constructor first
receives both component values. The pair projections choose the corresponding
component through a closed selector.

For conditionals, booleans select one delayed branch and the identity function
forces only that branch. This matches source conditionals and explains why an
unselected divergent expression stays unexecuted. The same delayed-branch idea
establishes the required short-circuit behavior for `and` and `or`. Arithmetic
and comparisons follow from the behavior of the closed Church combinators;
their tests cover representative zero, equal, unequal, and comparison cases.
Finally, the Z combinator unfolds a recursive function only when it receives an
argument, which is the behavior needed for call-by-value factorial and
Fibonacci examples. These arguments explain the design, but they are not a
full formal proof. A full proof would require formal definitions of both
semantics and an induction showing that every source evaluation corresponds to
the observed target evaluation.

For closed, well-typed source programs yielding naturals, booleans, or finite
pairs, observing a completed compiled term yields the same data as source
evaluation when budgets are sufficient. Application and let preserve CBV order;
the thunk translation preserves conditional and boolean short-circuiting; Z
provides a recursive function value under CBV. Tests exercise these claims but
are evidence, not a formal proof.
