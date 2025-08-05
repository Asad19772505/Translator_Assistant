import streamlit as st
import PyPDF2
from groq import Groq
from io import BytesIO
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os

# --- Secure API Key Retrieval ---
client = Groq(api_key=st.secrets["groq"]["api_key"])  # or use os.getenv("GROQ_API_KEY")

# --- App Title ---
st.set_page_config(page_title="PDF Translator with GROQ", layout="centered")
st.title("📄 PDF Translator to English using GROQ AI")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a PDF file (Arabic or other language)", type=["pdf"])
output_format = st.selectbox("Select Output Format", ["PDF", "Word (.docx)"])

if uploaded_file:
    # --- Step 1: Extract Text from PDF ---
    reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() + "\n"

    st.success("✅ Text extracted from PDF.")
    st.text_area("📄 Extracted Text", extracted_text, height=200)

    # --- Step 2: Translate Using GROQ ---
    if st.button("🔁 Translate to English"):
        with st.spinner("Translating with GROQ..."):
            prompt = f"Translate this Arabic (or other-language) text into professional English:\n\n{extracted_text}"
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a professional legal and document translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            translated_text = response.choices[0].message.content.strip()

        st.success("✅ Translation complete.")
        st.text_area("📝 Translated English Text", translated_text, height=200)

        # --- Step 3: Export Translated Text ---
        if output_format == "PDF":
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(line, styles["Normal"]) for line in translated_text.split("\n")]
            doc.build(story)
            buffer.seek(0)
            st.download_button("📥 Download Translated PDF", buffer, file_name="translated.pdf", mime="application/pdf")

        elif output_format == "Word (.docx)":
            doc = Document()
            for line in translated_text.split("\n"):
                doc.add_paragraph(line)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button("📥 Download Translated Word File", buffer, file_name="translated.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
