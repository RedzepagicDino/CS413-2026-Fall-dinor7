# Testing and architecture

Run `python3.12 -m unittest discover -s tests -v` in this directory, with the
course-provided LAMBDA3 folder in its original sibling location. Run the
instructor black-box suite from `assigns/07` as documented in `README.md`.

| Required behavior | Project test |
|---|---|
| Health and ID preservation | `test_health_and_typecheck` |
| Type checking | `test_health_and_typecheck` |
| Arithmetic, tuple, collection, closure values | `test_interpretation_values_and_function_formatting` |
| Factorial and both compiler targets | `test_factorial_and_compilers` |
| Syntax/type errors, validation, unknown method | `test_language_and_parameter_errors` |
| Batch, notifications, 204 and media type | `test_batches_notifications_and_transport` |
| Invalid request and invalid batch member | `test_invalid_batch_item_and_internal_helper_contract` |
| Injected backend failure is safe and preserves its ID | `test_injected_backend_failure_is_sanitized` |

## Observed results

On 2026-11-10 with Python 3.12.14, `python3.12 -B -m unittest discover -s
tests -v` passed all 7 project tests. With the server running, the supplied
`python3.12 -B -m unittest discover -s TEST -v` passed all 15 black-box tests.

```text
HTTP POST /rpc
     |
JSON-RPC envelope validator and batch dispatcher
     |
LambdaService adapter -----> LAMBDA3 parser/type checker/compiler
     |                              |
isolated interpreter worker <--------+
     |
JSON-RPC response serializer
```
