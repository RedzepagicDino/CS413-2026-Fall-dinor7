# Testing and smoke-test record

Run automated checks with `python3 -m unittest discover -s tests -v`.

| ID | Check and expected outcome | Evidence |
|---|---|---|
| F1 | Constructor/binding free variables, duplicates, fix and let scope return `frozenset`. | `test_all_key_binding_rules_and_frozenset` (model/tool test; no server). |
| F2 | Closed lint succeeds; sorted open names fail; divide by zero is not evaluated by lint. | `test_lint_closed_open_and_no_evaluation`. |
| F3 | Arithmetic/factorial plus malformed and runtime failures. | `test_arithmetic_factorial_fibonacci_and_failures`. |
| F4 | Manual source replacement and invalid blank replacement preserves source. | `test_replace_invalid_and_dispatch`. |
| F5 | Test backend dispatch; placeholders are not success and Execute has no artifact. | `test_replace_invalid_and_dispatch`. |
| F6 | Timeout produces retryable failure. | `test_timeout_retry_with_substitute_backend`. |
| F7 | Source menu/upload/editor actions display literal text safely. | Manual smoke test below. |
| F8 | Five controls, including disabled Execute, are reachable and textual. | Manual smoke test below. |
| F9 | Error recovery after bad input leaves prior applied source. | Manual smoke test below. |
| F10 | Lint, interpretation and placeholder outcomes show operation/revision/kind. | Automated backend tests + manual smoke test. |

## Browser smoke-test steps (record after local run)

1. Start server and open the documented URL. Expected: editor and all labeled controls appear; Execute is disabled.
2. Upload `examples/factorial.txt`; expected: its literal source enters the editor. Apply and Interpret; expected: textual `D0Vint(arg1=120)`.
3. Enter `D0Evar("x")`, Apply, Lint; expected: `Undeclared variable(s): x`. Edit to `D0Eint(1)` and lint again; expected pass.
4. Enter `<b>not HTML</b>` and Apply; expected: literal text/invalid-input diagnostic, never rendered markup. Enter division-by-zero source; expected Lint success then interpretation error. Select Type-check and Compile; expected not-implemented text.

Observed result: automated tests were run during submission preparation; perform these browser steps on the target machine before final submission and record browser/version/date here.
