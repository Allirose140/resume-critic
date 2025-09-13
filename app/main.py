# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse

# Import from the app package (matches app/services/)
from app.services.pdf_parser import ResumeParser, PARSER_VERSION
# Note: we intentionally DO NOT import AICritic here (diagnostic mode)

# Debug: prove which parser is loaded at startup
import logging, inspect, traceback
import app.services.pdf_parser as parser_mod
logging.warning(
    "USING PARSER: file=%s version=%s",
    inspect.getsourcefile(parser_mod),
    getattr(parser_mod, "PARSER_VERSION", "unknown"),
)

app = FastAPI(
    title="AI Resume Critic (Diagnostic)",
    description="Diagnostic build that only parses files and shows a snippet.",
    version="diag-1.0"
)

# -------------------- HOME FORM --------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Resume Critic (Diagnostic)</title>
<style>
  body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#0b1220; color:#e5e7eb; margin:0; }}
  .container {{ max-width: 860px; margin: 40px auto; padding: 24px; }}
  .card {{ background:#0f172a; border:1px solid #1f2937; border-radius:14px; padding:24px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }}
  h1 {{ margin:0 0 8px; font-size:28px; }}
  p.muted {{ color:#94a3b8; margin-top:0; }}
  input[type="file"], select, textarea {{ width:100%; padding:12px; border-radius:10px; border:1px solid #334155; background:#0b1220; color:#e5e7eb; }}
  textarea {{ min-height:120px; resize:vertical; }}
  label {{ display:block; margin:18px 0 8px; color:#cbd5e1; }}
  button {{ margin-top:18px; width:100%; background:#2563eb; color:white; padding:14px 18px; border:none; border-radius:12px; font-weight:600; cursor:pointer; }}
  button:hover {{ background:#1d4ed8; }}
  small.helper {{ color:#64748b; }}
</style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>AI Resume Critic (Diagnostic)</h1>
      <p class="muted">This mode only parses your file and shows a snippet (no critic).</p>
      <form action="/upload-resume" method="post" enctype="multipart/form-data">
        <label for="file"><strong>Resume file</strong></label>
        <input type="file" name="file" id="file" accept=".pdf,.docx" required />
        <button type="submit">Parse Only</button>
      </form>
    </div>
  </div>
</body>
</html>
""")

# -------------------- UPLOAD (Parse Only) --------------------
@app.post("/upload-resume", response_class=HTMLResponse)
async def upload_resume(
    file: UploadFile = File(...),
    industry: str = Form(default=""),
    job_description: str = Form(default="")
):
    try:
        file_bytes = await file.read()

        parser = ResumeParser()
        text = await parser.parse_resume(None, file_bytes)  # <-- filename-agnostic

        safe_snippet = (
            text[:1500]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Parsed OK</title></head>
<body style="font-family:system-ui;background:#0b1220;color:#e5e7eb">
  <div style="max-width:960px;margin:40px auto">
    <a href="/" style="color:#a5b4fc;text-decoration:none">&larr; Back</a>
    <h1>Parsed OK</h1>
    <p><strong>Parser version:</strong> {PARSER_VERSION}</p>
    <p><strong>Characters:</strong> {len(text)}</p>
    <pre style="white-space:pre-wrap;border:1px solid #334155;padding:12px;max-height:420px;overflow:auto">{safe_snippet}</pre>
  </div>
</body></html>
        """)

    except Exception as e:
        logging.error("UPLOAD ERROR: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

# -------------------- HEALTH --------------------
@app.get("/health")
async def health():
    import inspect, app.services.pdf_parser as parser_mod
    return {
        "status": "ok",
        "service": "AI Resume Critic (Diagnostic)",
        "parser_file": inspect.getsourcefile(parser_mod),
        "parser_version": getattr(parser_mod, "PARSER_VERSION", "unknown"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
