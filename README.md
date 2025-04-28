📄 AI Resume Parser
A simple Streamlit web app that extracts key information from resumes (PDFs) using intelligent parsing and basic natural language techniques.

🛠 Approach
Text Extraction:
Used pdfminer.six to extract raw text from PDFs. It ensures compatibility with text-based PDFs.

Link Extraction:
Used PyMuPDF (fitz) to parse embedded links (e.g., LinkedIn URLs) inside the PDF.

Information Extraction:
Used regular expressions (re) and custom parsing to extract:

Name

Email

Phone Number

LinkedIn Profile

Skills (matches from a predefined list)

Education (degree, institution, year)

Experience (company, title, duration, description)

Projects
