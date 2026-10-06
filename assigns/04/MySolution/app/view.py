"""View renders text safely and forwards form values only."""
from html import escape
def page(model, message=""):
    r=model.result; output = "No operation has run." if r is None else f"[{r.operation}, revision {r.revision}, {r.kind.value}]\n{r.text}"
    disabled = "disabled" if model.artifact is None else ""
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>LAMBDA MVC</title></head><body>
<h1>LAMBDA MVC front-end</h1><p>{escape(message)}</p><form method="post" enctype="multipart/form-data">
<label>Upload source <input type="file" id="file" accept=".txt,.lambda"></label>
<label>Source editor <textarea name="source" rows="14" cols="88">{escape(model.source)}</textarea></label>
<button name="action" value="apply">Apply source</button><button name="action" value="lint">Lint</button><button name="action" value="interpret">Interpret</button><button name="action" value="type-check">Type-check</button><button name="action" value="compile">Compile</button><button name="action" value="execute" {disabled}>Execute</button></form>
<h2>Status and textual output</h2><pre>{escape(output)}</pre><p>Execute is disabled until a future compiler provides an artifact.</p><script>document.querySelector('#file').addEventListener('change',e=>{{let f=e.target.files[0];if(f){{let r=new FileReader();r.onload=()=>document.querySelector('textarea').value=r.result;r.readAsText(f)}}}})</script></body></html>'''
