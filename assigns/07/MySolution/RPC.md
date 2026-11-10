# RPC contract

## Transport and envelopes

Send `POST /rpc` with `Content-Type: application/json`. Requests and normal
responses use JSON-RPC 2.0. JSON-RPC outcomes (including errors) use HTTP
200. A valid notification, or a batch containing only notifications, returns
HTTP 204 with an empty body. Unsupported media types return HTTP 415; an
unknown URL returns HTTP 404.

Every call has `"jsonrpc":"2.0"`, a string `method`, an object `params`, and
an optional `id` (string, number, or null). Omitting `id` creates a
notification. Responses have exactly one of `result` or `error` and preserve
the request ID. A client must match batch responses by ID, not position.

The maximum UTF-8 source size is 100,000 bytes. Interpretation has a 2.0
second process deadline. A timeout is reported as an error; it does not prove
the program cannot terminate.

## Methods

| Method | Params | Result |
|---|---|---|
| `service.health` | `{}` | `{"status":"ok","version":"1.0"}` |
| `lambda.typecheck` | `{"source": string}` | `{"type": string}` |
| `lambda.interpret` | `{"source": string}` | `{"type": string,"value": string}` |
| `lambda.compile` | `{"source": string,"target":"python"|"javascript"}` | `{"target": string,"code": string}` |

Source must be a nonblank string. All source operations parse and type-check
before interpreting or compiling. Types are from `format_type`; values are
from `d0val_format`, so closures are represented safely as `<lam>` or `<fix>`.

## Examples

Health:

```json
{"jsonrpc":"2.0","method":"service.health","params":{},"id":"h1"}
{"jsonrpc":"2.0","id":"h1","result":{"status":"ok","version":"1.0"}}
```

Type-checking and interpretation:

```json
{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + 2"},"id":2}
{"jsonrpc":"2.0","id":2,"result":{"type":"sint"}}
{"jsonrpc":"2.0","method":"lambda.interpret","params":{"source":"20 + 22"},"id":3}
{"jsonrpc":"2.0","id":3,"result":{"type":"sint","value":"42"}}
```

Compilation:

```json
{"jsonrpc":"2.0","method":"lambda.compile","params":{"source":"1 + 2","target":"python"},"id":"c"}
{"jsonrpc":"2.0","id":"c","result":{"target":"python","code":"...generated source..."}}
```

Syntax and type errors:

```json
{"jsonrpc":"2.0","id":"s","error":{"code":-32010,"message":"LAMBDA syntax error","data":{"diagnostic":"..."}}}
{"jsonrpc":"2.0","id":"t","error":{"code":-32011,"message":"LAMBDA type-checking error","data":{"diagnostic":"..."}}}
```

A mixed batch returns only the call response:

```json
[{"jsonrpc":"2.0","method":"service.health","params":{},"id":"a"},{"jsonrpc":"2.0","method":"service.health","params":{}}]
[{"jsonrpc":"2.0","id":"a","result":{"status":"ok","version":"1.0"}}]
```

A notification-only batch returns HTTP 204 and no body:

```json
[{"jsonrpc":"2.0","method":"service.health","params":{}}]
```

## Errors

| Code | Category | `data` |
|---:|---|---|
| -32700 | Parse error (invalid JSON) | none |
| -32600 | Invalid Request envelope or empty batch | none |
| -32601 | Unknown method | none |
| -32602 | Invalid parameters, including size limit | max size when relevant |
| -32603 | Internal error | none |
| -32010 | LAMBDA syntax error | client-safe diagnostic |
| -32011 | LAMBDA type-checking error | client-safe diagnostic |
| -32012 | Execution deadline expired | timeout seconds |

Tracebacks and filesystem paths are never returned.

## JSON Schema (envelopes)

```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","$defs":{"request":{"type":"object","required":["jsonrpc","method","params"],"properties":{"jsonrpc":{"const":"2.0"},"method":{"type":"string"},"params":{"type":"object"},"id":{"type":["string","number","null"]}}},"response":{"type":"object","required":["jsonrpc","id"],"properties":{"jsonrpc":{"const":"2.0"},"id":{"type":["string","number","null"]},"result":{},"error":{"type":"object","required":["code","message"],"properties":{"code":{"type":"integer"},"message":{"type":"string"},"data":{}}}},"oneOf":[{"required":["result"]},{"required":["error"]}]}}}
```
