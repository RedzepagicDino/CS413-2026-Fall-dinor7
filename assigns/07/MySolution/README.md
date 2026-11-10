# LAMBDA3 JSON-RPC service

This project implements Assign07 using Python 3.12+ and only the Python
standard library. It exposes a local JSON-RPC 2.0 endpoint at
`http://127.0.0.1:8000/rpc`.

## Setup, startup, and tests

Use Python 3.12 or later; the provided `LAMBDA3/lambda3.py` uses Python 3.12
syntax. No packages need to be installed.

```sh
cd assigns/07/MySolution
python3.12 app.py
```

In another terminal, run the project tests:

```sh
cd assigns/07/MySolution
python3.12 -m unittest discover -s tests -v
```

Run the supplied black-box tests while the service is running:

```sh
cd assigns/07
python3.12 -m unittest discover -s TEST -v
```

## Examples

Health request:

```sh
curl -X POST http://127.0.0.1:8000/rpc -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"service.health","params":{},"id":1}'
```

Factorial interpretation:

```sh
curl -X POST http://127.0.0.1:8000/rpc -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.interpret","params":{"source":"let fact : sint -> sint = fix fact(n: sint): sint => if n <= 1 then 1 else n * fact(n - 1) in fact(6) end"},"id":"fact"}'
```

Type-error demonstration:

```sh
curl -X POST http://127.0.0.1:8000/rpc -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + true"},"id":"bad-type"}'
```

Compilation demonstration:

```sh
curl -X POST http://127.0.0.1:8000/rpc -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.compile","params":{"source":"1 + 2","target":"javascript"},"id":"compile"}'
```

Compilation returns generated source text. The service never executes
generated Python or JavaScript.
