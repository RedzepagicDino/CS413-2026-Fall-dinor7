# AI assistance transcript

## Tools and assistance used

Codex was used to inspect `Assign07.md`, the supplied black-box tests, and
the public LAMBDA3 API. It helped draft the JSON-RPC service, documentation,
and automated tests.

## Important prompts/suggestions

- Requested: identify the assignment instructions and grading system.
- Requested: build the assignment step by step and make GitHub pushes.
- The implementation suggestion was to use Python's standard-library HTTP
  server, separate JSON-RPC envelope handling from a LAMBDA3 service adapter,
  and evaluate in a child process to enforce a deadline.

## Review and testing

The generated work was reviewed against `Assign07.md` and
`TEST/test_rpc_api.py`. With Python 3.12.14, all 7 project HTTP-level tests
and all 15 supplied black-box contract tests passed. The project supplies the
exact reproducible commands in `README.md` and `TESTING.md`.
