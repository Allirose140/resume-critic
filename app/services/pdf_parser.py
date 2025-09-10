import PyPDF2
from docx import Document
import io
from typing import Optional


class ResumeParser:
    def __init__(self):
        pass

    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")

    async def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")

    async def parse_resume(self, filename: str, file_content: bytes) -> str:
        """Parse resume based on file type"""
        if filename.lower().endswith('.pdf'):
            return await self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return await self.extract_text_from_docx(file_content)
        else:
            raise Exception("Unsupported file type")
