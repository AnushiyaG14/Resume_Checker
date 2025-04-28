import streamlit as st
import re
import fitz  # PyMuPDF
import json
from typing import List, Dict, Tuple
from pdfminer.high_level import extract_text
import io
import base64
def set_image_local(image_path):
    with open(image_path, "rb") as file:
        img = file.read()
    base64_image = base64.b64encode(img).decode("utf-8")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            background-repeat: no-repeat;
            #background-position: center;
            #background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_image_local(r"img2.jpg")

def extract_text_from_pdf(file_bytes) -> str:
    with io.BytesIO(file_bytes) as pdf_io:
        return extract_text(pdf_io)

def extract_links_from_pdf(file_bytes) -> List[str]:
    links = []
    with fitz.open("pdf", file_bytes) as doc:
        for page in doc:
            for link in page.get_links():
                if "uri" in link:
                    links.append(link["uri"])
    return links

def extract_name(text: str) -> Tuple[str, float]:
    match = re.search(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)
    return (match.group(0), 0.9) if match else (None, 0.0)

def extract_email(text: str) -> Tuple[str, float]:
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    return (match.group(0), 0.9) if match else (None, 0.0)

def extract_phone(text: str) -> Tuple[str, float]:
    match = re.search(r'\b\d{10}\b', text)
    return (match.group(0), 0.9) if match else (None, 0.0)

def extract_linkedin(text: str, file_bytes) -> Tuple[str, float]:
    match = re.search(r"https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-\_\/]+", text)
    if match:
        return match.group(0), 0.9
    embedded_links = extract_links_from_pdf(file_bytes)
    for link in embedded_links:
        if "linkedin.com" in link:
            return link, 0.9
    return None, 0.0

def extract_skills(text: str) -> Tuple[List[str], float]:
    skills_list = ["Python", "Java", "SQL", "AWS", "Git", "NLP", "TensorFlow", "Machine Learning"]
    extracted = [skill for skill in skills_list if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return (extracted, 0.9) if extracted else (None, 0.0)

def extract_education(text: str) -> Tuple[List[Dict[str, str]], float]:
    education = []
    education_section = re.findall(r'(?i)(?:Education|Academics)\s*(.*?)\s*(Experience|Skills|Projects|Certifications|$)', text, re.DOTALL)
    if education_section:
        content = education_section[0][0]
        entries = re.split(r'\n{2,}', content)
        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 1:
                degree = lines[0]
                institution = lines[1] if len(lines) > 1 else ""
                year_match = re.search(r'\b(19|20)\d{2}\b', entry)
                year = year_match.group(0) if year_match else ""
                education.append({
                    "degree": degree.strip(),
                    "institution": institution.strip(),
                    "year": year
                })
    return (education, 0.9) if education else (None, 0.0)

def extract_experience(text: str) -> Tuple[List[Dict[str, str]], float]:
    experience = []
    experience_section = re.findall(r'(?i)(?:Experience|Work Experience|Professional Experience)\s*(.*?)\s*(Education|Certifications|Skills|Projects|$)', text, re.DOTALL)
    if experience_section:
        content = experience_section[0][0]
        entries = re.split(r'\n{2,}', content)
        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 2:
                company_title = lines[0]
                duration = lines[1]
                description = " ".join(lines[2:]) if len(lines) > 2 else ""
                if "-" in company_title:
                    parts = company_title.split("-", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()
                else:
                    company = company_title.strip()
                    title = ""
                experience.append({
                    "company": company,
                    "title": title,
                    "duration": duration.strip(),
                    "description": description.strip()
                })
    return (experience, 0.9) if experience else (None, 0.0)

def extract_projects(text: str) -> Tuple[List[str], float]:
    projects = []
    project_section = re.findall(r'(?i)(?:Projects|Academic Projects|Personal Projects)\s*(.*?)\s*(Education|Certifications|Experience|Skills|$)', text, re.DOTALL)
    if project_section:
        content = project_section[0][0]
        entries = re.split(r'\n{2,}', content)
        for entry in entries:
            clean_entry = entry.strip()
            if len(clean_entry) > 5:
                projects.append(clean_entry)
    return (projects, 0.9) if projects else (None, 0.0)

st.title("📄 AI Resume Parser")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting..."):
        file_bytes = uploaded_file.read()

        raw_text = extract_text_from_pdf(file_bytes)

        name, name_conf = extract_name(raw_text)
        email, email_conf = extract_email(raw_text)
        phone, phone_conf = extract_phone(raw_text)
        linkedin, linkedin_conf = extract_linkedin(raw_text, file_bytes)
        skills, skills_conf = extract_skills(raw_text)
        education, education_conf = extract_education(raw_text)
        experience, experience_conf = extract_experience(raw_text)
        projects, projects_conf = extract_projects(raw_text)

        parsed_data = {
            "name": name,
            "name_confidence": name_conf,
            "email": email,
            "email_confidence": email_conf,
            "phone": phone,
            "phone_confidence": phone_conf,
            "linkedin": linkedin,
            "linkedin_confidence": linkedin_conf,
            "skills": skills,
            "skills_confidence": skills_conf,
            "education": education,
            "education_confidence": education_conf,
            "experience": experience,
            "experience_confidence": experience_conf,
            "certifications": None,
            "certifications_confidence": 0.0,
            "projects": projects,
            "projects_confidence": projects_conf
        }

    st.success("✅ Resume Parsed Successfully!")
    st.json(parsed_data)
