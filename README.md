# AI Resume Critic

An intelligent resume analysis tool that provides instant AI-powered feedback to help job seekers improve their resumes. Upload your resume and get comprehensive insights on content quality, structure, keyword optimization, and actionable recommendations.
## Live Demo

Try it live: https://resume-critic.onrender.com
Note: Initial load may take 30-60 seconds due to free hosting limitations.

## Features

- **Document Processing**: Supports PDF and DOCX file formats
- **Text Extraction**: Advanced parsing to extract clean text from resume documents
- **AI-Powered Analysis**: Intelligent feedback on resume content and structure
- **Keyword Analysis**: Identifies existing keywords and suggests improvements for ATS compatibility
- **Structured Feedback**: Organized results with strengths, areas for improvement, and specific recommendations
- **Clean Web Interface**: User-friendly upload form and formatted results display
- **RESTful API**: Backend API for integration with other applications

## Tech Stack

- **Backend**: FastAPI (Python)
- **Document Processing**: PyPDF2, python-docx
- **AI Analysis**: Mock intelligent analysis system (ready for OpenAI/Anthropic integration)
- **Frontend**: HTML/CSS with responsive design
- **Deployment**: Uvicorn ASGI server

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-critic
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Local Development

1. **Start the server**
   ```bash
   cd app
   python main.py
   ```

2. **Access the application**
   - Web interface: `http://localhost:8000/upload`
   - API documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### API Endpoints

- `GET /` - API status
- `GET /upload` - Resume upload page
- `POST /upload-resume` - Upload and analyze resume
- `GET /health` - Health check endpoint

## Project Structure

```
resume-critic/
├── app/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py    # Document parsing logic
│   │   └── ai_critic.py     # AI analysis engine
│   └── __init__.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## How It Works

1. **File Upload**: Users upload PDF or DOCX resume files through the web interface
2. **Text Extraction**: The system extracts and cleans text content from the document
3. **Basic Analysis**: Performs structural analysis (word count, contact info detection, etc.)
4. **AI Analysis**: Generates intelligent feedback using mock AI system
5. **Results Display**: Presents organized feedback with scores, strengths, improvements, and recommendations

## Sample Analysis Output

The system provides:
- **Overall Score**: 0-100 rating
- **Strengths**: Highlights what's working well
- **Areas for Improvement**: Specific suggestions for enhancement
- **Keyword Analysis**: Technical keywords found and suggested additions
- **Recommendations**: Actionable steps for resume improvement

## Deployment

### Railway (Recommended)

1. Create `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Push to GitHub and connect to Railway for automatic deployment

### Other Platforms

The application is compatible with Heroku, Render, and similar platforms. Ensure the `Procfile` and `requirements.txt` are properly configured.

## Future Enhancements

- **Real AI Integration**: Connect to OpenAI or Anthropic APIs for advanced analysis
- **Job Description Matching**: Compare resumes against specific job postings
- **ATS Scoring**: Applicant Tracking System compatibility assessment
- **Multiple Format Support**: Add support for additional document formats
- **User Accounts**: Save analysis history and track improvements
- **Industry-Specific Analysis**: Tailored feedback for different job sectors

## Development

### Adding New Features

1. **Document Parsers**: Extend `pdf_parser.py` for new file formats
2. **Analysis Modules**: Enhance `ai_critic.py` with additional feedback mechanisms
3. **API Endpoints**: Add new routes in `main.py` for expanded functionality

### Testing

The application includes basic error handling and validation. For production use, consider adding:
- Unit tests for parsing logic
- Integration tests for API endpoints
- File format validation
- Security scanning for uploaded files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue in the repository.

---


**Note**: This application currently uses a mock AI analysis system. For production deployment with real AI capabilities, you'll need to integrate with OpenAI, Anthropic, or similar AI service providers.


