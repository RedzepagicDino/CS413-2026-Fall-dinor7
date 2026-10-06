# LAMBDA MVC front-end

Requires Python 3.12+; it uses only the standard library. From this directory run:

```sh
python3 -m unittest discover -s tests -v
python3 -m app.server
```

Open <http://127.0.0.1:8000>. The server binds only to loopback. Enter/paste a single `d0exp` constructor expression, or choose a text file; the browser copies the selected file's text into the editor, which must then be applied. Nested constructors, Python comments, and multiline expressions work. This is not a Python-script input field: only the listed `D0E...` constructors, strings, integers, and booleans are accepted.

Try the factorial and Fibonacci files in `examples/`, then select **Interpret**. Enter `D0Evar("x")`, apply it, and select **Lint** to see the undeclared-variable report; replace it with `D0Eint(42)` to pass. `D0Eop2("/", D0Eint(1), D0Eint(0))` passes Lint but has an interpretation runtime error. Type-check and Compile deliberately return not-implemented messages. Execute remains disabled because no compiler creates an artifact.

Interpretation has a two-second request bound; a timeout becomes a textual failure and retry remains possible (a daemon worker may finish later). Persistence, accounts, public hosting, generated-code execution, and a concrete LAMBDA parser are intentionally absent.

## Reflection (224 words)

MVC helped most by making the important state rule visible: the model, rather than a web form, owns the applied source and its revision. The controller can therefore be tested with no browser and can reject an empty replacement without accidentally replacing the previously applied program. Results carry their own operation and revision at the backend boundary, which prevents the display from implying that an old result describes a newly edited source. The view only escapes and renders text; it has no knowledge of free variables or interpreter classes. That separation also made the security decision easier to audit: the restricted reader and the language adapter are separate from HTTP and HTML.

The most difficult separation was bounded interpretation. A standard-library thread can allow the controller to return a timeout and restore the UI, but Python cannot safely kill a running thread. A production version should move each evaluation into a supervised subprocess with resource limits, leaving the controller contract unchanged. Uploading is similarly deliberately modest: browser JavaScript reads a user-selected local text file into the visible editor; the server never receives an arbitrary executable upload.

A future compiler is easier because `LambdaBackend.compile` is already the only place expected to make that call. It can return a generated-code artifact associated with the model revision; the model invalidates that artifact whenever source changes. `execute` would then consume precisely that artifact, rather than recompiling or using interpretation as a substitute. The view would only notice that Execute becomes enabled, and controller tests could substitute a compiler adapter without requiring changes to templates.
