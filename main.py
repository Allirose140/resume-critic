from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pdf_parser import ResumeParser
from ai_critic import AICritic
import os

app = FastAPI(
    title="AI Resume Critic",
    description="Upload your resume and get AI-powered feedback",
    version="1.0.0"
)


@app.get("/")
async def home():
    return {"message": "AI Resume Critic API", "status": "running"}


@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Critic</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px; 
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .upload-form { 
                border: 2px dashed #007bff; 
                padding: 40px; 
                text-align: center; 
                border-radius: 10px; 
                background: #f8f9fa;
            }
            input[type="file"] { 
                margin: 20px 0; 
                padding: 10px;
            }
            button { 
                background: #007bff; 
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px;
                font-weight: bold;
            }
            button:hover { 
                background: #0056b3; 
            }
            .features {
                margin-top: 30px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }
            .feature {
                text-align: center;
                padding: 20px;
                background: #e9ecef;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Resume Critic</h1>
            <p class="subtitle">Upload your resume (PDF or DOCX) to get instant AI-powered feedback</p>

            <div class="upload-form">
                <form action="/upload-resume" method="post" enctype="multipart/form-data">
                    <h3>Select Your Resume</h3>
                    <input type="file" name="file" accept=".pdf,.docx" required>
                    <br>
                    <button type="submit">Analyze Resume</button>
                </form>
            </div>

            <div class="features">
                <div class="feature">
                    <h4>Text Extraction</h4>
                    <p>Advanced parsing of PDF and DOCX files</p>
                </div>
                <div class="feature">
                    <h4>AI Analysis</h4>
                    <p>Intelligent feedback on content and structure</p>
                </div>
                <div class="feature">
                    <h4>Keyword Optimization</h4>
                    <p>Suggestions for better ATS compatibility</p>
                </div>
                <div class="feature">
                    <h4>Actionable Insights</h4>
                    <p>Specific recommendations for improvement</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/upload-resume", response_class=HTMLResponse)
async def upload_resume(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    try:
        # Read file content
        content = await file.read()

        # Initialize parser and extract text
        parser = ResumeParser()
        extracted_text = await parser.parse_resume(file.filename, content)

        # Basic analysis
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        lines = extracted_text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        # Simple resume structure analysis
        has_email = '@' in extracted_text
        has_phone = any(char.isdigit() for char in extracted_text)

        # AI-powered analysis
        ai_critic = AICritic()
        ai_analysis = await ai_critic.analyze_resume(extracted_text)

        # Return formatted HTML results page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resume Analysis Results</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    max-width: 1000px; 
                    margin: 20px auto; 
                    padding: 20px; 
                    line-height: 1.6; 
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .score {{ 
                    font-size: 48px; 
                    font-weight: bold; 
                    color: #28a745; 
                    margin: 10px 0; 
                }}
                .section {{ 
                    background: #f8f9fa; 
                    padding: 25px; 
                    margin: 20px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #007bff; 
                }}
                .section h3 {{ 
                    margin-top: 0; 
                    color: #333; 
                    font-size: 20px;
                    margin-bottom: 15px;
                }}
                .strengths {{ border-left-color: #28a745; }}
                .improvements {{ border-left-color: #ffc107; }}
                .keywords {{ border-left-color: #17a2b8; }}
                .recommendations {{ border-left-color: #6f42c1; }}
                ul {{ 
                    padding-left: 20px; 
                    margin: 0;
                }}
                li {{ 
                    margin: 10px 0; 
                    padding: 5px 0;
                }}
                .back-btn {{ 
                    display: inline-block; 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin-top: 20px; 
                    font-weight: bold;
                }}
                .back-btn:hover {{ background: #0056b3; }}
                .stats {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                    gap: 15px; 
                    margin: 30px 0; 
                }}
                .stat {{ 
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center; 
                    border: 1px solid #dee2e6;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .stat-number {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #007bff; 
                    margin-bottom: 5px;
                }}
                .stat-label {{ 
                    color: #666; 
                    font-size: 14px; 
                }}
                .keyword-group {{
                    margin: 10px 0;
                }}
                .keyword-group strong {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Resume Analysis Results</h1>
                    <p>Analysis for: <strong>{file.filename}</strong></p>
                    <div class="score">{ai_analysis['overall_score']}/100</div>
                    <p style="color: #666; margin: 0;">Overall Score</p>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{word_count}</div>
                        <div class="stat-label">Words</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(non_empty_lines)}</div>
                        <div class="stat-label">Lines</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{"✓" if has_email else "✗"}</div>
                        <div class="stat-label">Email Found</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{"✓" if has_phone else "✗"}</div>
                        <div class="stat-label">Phone Found</div>
                    </div>
                </div>

                <div class="section strengths">
                    <h3>🎯 Strengths</h3>
                    <ul>
                        {"".join(f"<li>{strength}</li>" for strength in ai_analysis['strengths'])}
                    </ul>
                </div>

                <div class="section improvements">
                    <h3>⚡ Areas for Improvement</h3>
                    <ul>
                        {"".join(f"<li>{improvement}</li>" for improvement in ai_analysis['areas_for_improvement'])}
                    </ul>
                </div>

                <div class="section keywords">
                    <h3>🔍 Keyword Analysis</h3>
                    <div class="keyword-group">
                        <strong>Found Keywords:</strong> {", ".join(ai_analysis['keyword_analysis']['technical_keywords'])}
                    </div>
                    <div class="keyword-group">
                        <strong>Suggested Keywords:</strong> {", ".join(ai_analysis['keyword_analysis']['missing_keywords'])}
                    </div>
                    <div class="keyword-group">
                        <strong>Keyword Density:</strong> {ai_analysis['keyword_analysis']['keyword_density']}
                    </div>
                </div>

                <div class="section recommendations">
                    <h3>💡 Recommendations</h3>
                    <ul>
                        {"".join(f"<li>{rec}</li>" for rec in ai_analysis['recommendations'])}
                    </ul>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="/upload" class="back-btn">Analyze Another Resume</a>
                </div>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Resume Critic"}


if __name__ == "__main__":
    import uvicorn


    uvicorn.run(app, host="0.0.0.0", port=8000)
