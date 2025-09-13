from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse

from app.services.pdf_parser import ResumeParser, PARSER_VERSION
from app.services.ai_critic import AICritic

import logging, inspect, traceback
import app.services.pdf_parser as parser_mod

def _no_store_headers():
    return {"Cache-Control": "no-store"}  # avoid browser reusing prior POST result

logging.warning(
    "USING PARSER: file=%s version=%s",
    inspect.getsourcefile(parser_mod),
    getattr(parser_mod, "PARSER_VERSION", "unknown"),
)

app = FastAPI(
    title="AI Resume Critic",
    description="Upload your resume and get industry-aware feedback",
    version="1.6.0"
)

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=f"""
<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Resume Critic</title>
<style>
  body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#0b1220; color:#e5e7eb; margin:0; }}
  .container {{ max-width: 860px; margin: 40px auto; padding: 24px; }}
  .card {{ background:#0f172a; border:1px solid #1f2937; border-radius:14px; padding:24px; }}
  h1 {{ margin:0 0 8px; font-size:28px; }}
  p.muted {{ color:#94a3b8; margin-top:0; }}
  input, select, textarea {{ width:100%; padding:12px; border-radius:10px; border:1px solid #334155; background:#0b1220; color:#e5e7eb; }}
  textarea {{ min-height:120px; resize:vertical; }}
  label {{ display:block; margin:18px 0 8px; color:#cbd5e1; }}
  button {{ margin-top:18px; width:100%; background:#2563eb; color:white; padding:14px 18px; border:none; border-radius:12px; font-weight:600; cursor:pointer; }}
  button:hover {{ background:#1d4ed8; }}
</style></head>
<body>
  <div class="container">
    <div class="card">
      <h1>AI Resume Critic</h1>
      <p class="muted">Upload your resume (PDF/DOCX), select an industry (optional), and paste a job description (optional).</p>
      <form action="/upload-resume" method="post" enctype="multipart/form-data">
        <label><strong>Resume file</strong></label>
        <input type="file" name="file" accept=".pdf,.docx" required />

        <label><strong>Target Industry (optional)</strong></label>
        <select name="industry">
          <option value="" selected>Auto-detect</option>
          <option value="technology">Technology</option>
          <option value="healthcare">Healthcare</option>
          <option value="education">Education</option>
          <option value="sales_marketing">Sales/Marketing</option>
          <option value="finance_accounting">Finance/Accounting</option>
          <option value="operations_hr">Operations/HR</option>
          <option value="arts_media">Arts/Media</option>
          <option value="service_retail">Service/Retail</option>
        </select>
        <label><strong>Job Description (optional)</strong></label>
        <textarea name="job_description" placeholder="Paste the target job post to tailor keywords & coverage"></textarea>

        <button type="submit">Analyze Resume</button>
      </form>
    </div>
  </div>
</body></html>
""", headers=_no_store_headers())

@app.post("/upload-resume", response_class=HTMLResponse)
async def upload_resume(
    file: UploadFile = File(...),
    industry: str = Form(default=""),
    job_description: str = Form(default="")
):
    try:
        file_bytes = await file.read()
        parser = ResumeParser()
        text = await parser.parse_resume(None, file_bytes)  # sniff bytes only

        critic = AICritic()
        analysis = await critic.analyze_resume(
            text,
            job_description=job_description or None,
            industry=industry or None
        )

        logging.warning("ANALYSIS: detected_industry=%s chars=%d",
                        analysis.get("industry"), len(text))

        styles = """
        <style>
          body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#0b1220; color:#e5e7eb; }
          .card { background:#0f172a; border:1px solid #1f2937; border-radius:14px; padding:18px; }
          .grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
          .pill { display:inline-block; background:#1f2937; padding:6px 10px; border-radius:999px; margin:4px 6px 0 0; }
        </style>
        """

        return HTMLResponse(content=f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><title>Resume Analysis</title>{styles}</head>
<body>
  <div style="max-width:980px;margin:40px auto">
    <a href="/" style="color:#a5b4fc;text-decoration:none">&larr; Analyze another</a>
    <h1>Resume Analysis</h1>
    <div class="grid">
      <div class="card">
        <h2>Overview</h2>
        <p><strong>Overall Score:</strong> {analysis.get('overall_score','-')}/100</p>
        <p><strong>Detected Industry:</strong> {analysis.get('industry','')}</p>
      </div>
      <div class="card">
        <h2>Keyword Summary</h2>
        <p><strong>Found Keywords:</strong><br>
          {''.join(f'<span class="pill">{k}</span>' for k in analysis["keyword_analysis"]["industry_keywords"]) or "—"}
        </p>
        <p><strong>Suggested Keywords (from job post):</strong><br>
          {''.join(f'<span class="pill">{k}</span>' for k in analysis["keyword_analysis"]["suggested_keywords"]) or "—"}
        </p>
        <p><strong>Keyword Coverage:</strong> {analysis["keyword_analysis"]["keyword_coverage"]}</p>
      </div>
      <div class="card">
        <h2>Strengths</h2>
        <ul>{"".join(f"<li>{s}</li>" for s in analysis["strengths"])}</ul>
      </div>
      <div class="card">
        <h2>Areas for Improvement</h2>
        <ul>{"".join(f"<li>{s}</li>" for s in analysis["areas_for_improvement"])}</ul>
      </div>
      <div class="card">
        <h2>Formatting Feedback</h2>
        <p><strong>Structure:</strong> {analysis["formatting_feedback"]["structure"]}</p>
        <p><strong>Readability:</strong> {analysis["formatting_feedback"]["readability"]}</p>
        <ul>{"".join(f"<li>{s}</li>" for s in analysis["formatting_feedback"]["suggestions"])}</ul>
      </div>
      <div class="card">
        <h2>Recommendations</h2>
        <ul>{"".join(f"<li>{s}</li>" for s in analysis["recommendations"])}</ul>
      </div>
    </div>
  </div>
</body></html>
        """, headers=_no_store_headers())
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
