import streamlit as st
from PIL import Image
import os
import fitz  # PyMuPDF
import datetime
import shutil
import time
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ----- Page Setup -----
st.set_page_config(page_title="Smart Resume Filter", page_icon="📄", layout="centered")

# ----- Custom CSS -----
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        background-color: #eaf3fb !important;
    }
    .title {
        font-size: 3rem;
        text-align: center;
        color: #1a237e;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .stTextInput > div > input, .stTextArea textarea {
        border-radius: 10px;
        background-color: #ffffff;
        padding: 10px;
    }
    .stButton button {
        background-color: #2e7d32;
        color: white;
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1b5e20;
    }
    .tip {
        font-size: 0.9rem;
        background-color: #fffde7;
        padding: 8px;
        border-radius: 10px;
        margin-top: 5px;
        color: #333;
        border-left: 5px solid #fbc02d;
    }
    </style>
""", unsafe_allow_html=True)

# ----- Title -----
st.markdown('<h1 class="title">Smart Resume Filter</h1>', unsafe_allow_html=True)

# ----- Load Image -----
image = Image.open("search.png")
st.image(image, use_container_width=False, width=150)

# ----- Resume Parsing -----
def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return " ".join([page.get_text() for page in doc])

def match_keywords(text, jd):
    jd_keywords = [x.strip().lower() for x in jd.split(",") if x.strip()]
    text_lower = text.lower()
    return any(kw in text_lower for kw in jd_keywords)

# ----- Input Section -----
st.subheader("🔍 Input Configuration")

folder = st.text_input("📂 Path to folder containing resumes (PDFs):", placeholder="E.g., C:\\Users\\yamun\\Desktop\\resumes")
jd = st.text_area("🧠 Enter Job Description (comma-separated keywords):", placeholder="E.g., Python, machine learning, SQL, pandas")

st.markdown('''
<div class="tip">
💡 <b>Tip:</b> Use comma-separated role-specific skills for accurate matching. Example:<br><br>
<code>python, tensorflow, pytorch, sql, tableau, system design, git</code>
</div>
''', unsafe_allow_html=True)

output = st.text_input("📁 Path to save matched resumes:", placeholder="E.g., C:\\Users\\yamun\\Desktop\\matched_resumes")
timestamped = st.checkbox("✅ Create new timestamped subfolder for results", value=True)

# ----- Filter Button -----
if st.button("✅ Filter Resumes"):
    if not folder or not os.path.isdir(folder):
        st.error("❌ Invalid input folder.")
    elif not output or not os.path.isdir(output):
        st.error("❌ Invalid output folder.")
    elif not jd.strip():
        st.error("❌ Please enter job description keywords.")
    else:
        with st.spinner("🔍 Scanning resumes..."):
            time.sleep(1)
            matched = 0
            jd_main = "_".join([x.strip().lower().replace(" ", "_") for x in jd.split(",") if x.strip()])[:50]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{jd_main}_resumes_{timestamp}" if timestamped else f"{jd_main}_resumes"
            save_path = os.path.join(output, folder_name)

            for file in os.listdir(folder):
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(folder, file)
                    text = extract_text_from_pdf(pdf_path)
                    if match_keywords(text, jd):
                        if matched == 0:
                            os.makedirs(save_path, exist_ok=True)
                        shutil.copy(pdf_path, os.path.join(save_path, file))
                        matched += 1

        if matched:
            st.success(f"✅ Done! {matched} resumes matched.")
            st.info(f"📁 Results saved to: `{save_path}`")
        else:
            st.warning("⚠️ No resumes matched the given job description.")
