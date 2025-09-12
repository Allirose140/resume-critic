from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse

# IMPORTS MUST USE app.services.*
from app.services.pdf_parser import ResumeParser, PARSER_VERSION
from app.services.ai_critic import AICritic

# Debug: show which parser is actually loaded on startup
import logging, inspect, traceback
import app.services.pdf_parser as parser_mod
logging.warning(
    "USING PARSER: file=%s version=%s",
    inspect.getsourcefile(parser_mod),
    getattr(parser_mod, "PARSER_VERSION", "unknown"),
)

app = FastAPI(
    title="AI Resume Critic",
    description="Upload your resume and get AI-powered, industry-aware feedback",
    version="1.1.2"
)

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Resume Critic</title>
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
      <h1>AI Resume Critic</h1>
      <p class="muted">Industry-aware feedback. Upload your resume (PDF/DOCX), select an industry (optional), and paste a job description (optional).</p>
      <form action="/upload-resume" method="post" enctype="multipart/form-data">
        <label for="file"><strong>Resume file</strong></label>
        <input type="file" name="file" id="file" accept=".pdf,.docx" required />

        <label for="industry"><strong>Target Industry (optional)</strong></label>
        <select name="industry" id="industry">
          <option value="">Auto-detect</option>
          <option value="technology">Technology</option>
          <option value="healthcare">Healthcare</option>
          <option value="education">Education</option>
          <option value="sales_marketing">Sales/Marketing</option>
          <option value="finance_accounting">Finance/Accounting</option>
          <option value="operations_hr">Operations/HR</option>
          <option value="arts_media">Arts/Media</option>
        </select>
        <small class="helper">Tip: picking a target domain improves the precision of feedback.</small>

        <label for="job_description"><strong>Job Description (optional)</strong></label>
        <textarea name="job_description" id="job_description" placeholder="Paste the job post to tailor keyword & section advice"></textarea>

        <button type="submit">Analyze Resume</button>
      </form>
    </div>
  </div>
</body>
</html>
""")

@app.post("/upload-resume", response_class=HTMLResponse)
async def upload_resume(
    file: UploadFile = File(...),
    industry: str = Form(default=""),
    job_description: str = Form(default="")
):
    try:
        file_bytes = await file.read()

        parser = ResumeParser()
        # IMPORTANT: do not pass a filename; sniff bytes only
        extracted_text = await parser.parse_resume(None, file_bytes)

        critic = AICritic()
        analysis = await critic.analyze_resume(
            extracted_text,
            job_description=job_description or None,
            industry=industry or None
        )

        # Render minimal HTML (use your existing big HTML if you prefer)
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Resume Analysis</title></head>
<body style="font-family:system-ui;background:#0b1220;color:#e5e7eb">
  <div style="max-width:960px;margin:40px auto">
    <a href="/" style="color:#a5b4fc;text-decoration:none">&larr; Analyze another</a>
    <h1>Resume Analysis</h1>
    <p><strong>Score:</strong> {analysis.get('overall_score','-')}/100</p>
    <p><strong>Industry:</strong> {analysis.get('industry','')}</p>
    <h2>Strengths</h2>
    <ul>{"".join(f"<li>{s}</li>" for s in analysis["strengths"])}</ul>
    <h2>Areas for Improvement</h2>
    <ul>{"".join(f"<li>{s}</li>" for s in analysis["areas_for_improvement"])}</ul>
  </div>
</body></html>
        """)
    except Exception as e:
        logging.error("UPLOAD ERROR: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.get("/health")
async def health():
    import inspect, app.services.pdf_parser as parser_mod
    return {
        "status": "ok",
        "service": "AI Resume Critic",
        "parser_file": inspect.getsourcefile(parser_mod),
        "parser_version": getattr(parser_mod, "PARSER_VERSION", "unknown"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
