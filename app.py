import streamlit as st
from pdfminer.high_level import extract_text
import smtplib
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
import spacy
from collections import Counter
import heapq
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Predefined risk-related words
RISK_WORDS = [
    "fraud", "penalty", "violation", "risk", "lawsuit", "breach",
    "noncompliance", "litigation", "regulatory", "fine"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SENDER_EMAIL = "shreedeepthi2005@gmail.com"
SENDER_PASSWORD = "qntm oher jqfz oflt"

def extract_text_from_pdf(uploaded_file):
    return extract_text(uploaded_file)

def extract_key_clauses(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    clauses = [str(sentence).strip() for sentence in sentences if len(sentence) > 10]
    return clauses[:10]  # Return top 10 clauses for simplicity

def summarize_text(text, num_sentences=5):
    doc = nlp(text)
    sentences = list(doc.sents)
    word_frequencies = Counter([token.text.lower() for token in doc if token.is_alpha and not token.is_stop])
    sentence_scores = {}
    for sent in sentences:
        sentence_score = 0
        for word in sent:
            if word.text.lower() in word_frequencies:
                sentence_score += word_frequencies[word.text.lower()]
        sentence_scores[sent] = sentence_score
    summarized_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join([str(sentence) for sentence in summarized_sentences])
    return summary

def detect_risks(text):
    doc = nlp(text.lower())
    detected_risks = [token.text for token in doc if token.text in RISK_WORDS]
    return list(set(detected_risks))

def get_regulatory_updates():
    # Fallback: Pre-defined updates
    predefined_updates = [
        {"title": "New Compliance Guidelines", "summary": "SEC released new guidelines for regulatory compliance."},
        {"title": "Update on Financial Risks", "summary": "New policies to mitigate risks in the financial sector."},
    ]
    url = "https://www.sec.gov/newsroom/press-releases"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        updates = []  # Placeholder for parsed updates (needs a proper parsing method)
        return updates if updates else predefined_updates
    except requests.exceptions.RequestException:
        return predefined_updates

def generate_pdf(summary, clauses, risks, updates, pdf_path="Analysis_Results.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Legal Document Analysis Results", ln=True, align="C")

    # Summary
    pdf.ln(10)
    pdf.cell(200, 10, txt="Summary", ln=True, align="L")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, summary)

    # Key Clauses
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Key Clauses", ln=True, align="L")
    pdf.set_font("Arial", size=10)
    for clause in clauses:
        pdf.multi_cell(0, 10, f"- {clause}")

    # Risks
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Detected Risks", ln=True, align="L")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, ", ".join(risks))

    # Regulatory Updates
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Regulatory Updates", ln=True, align="L")
    pdf.set_font("Arial", size=10)
    if updates:
        for update in updates:
            pdf.multi_cell(0, 10, f"- {update.get('title', 'N/A')}: {update.get('summary', 'N/A')}")

    pdf.output(pdf_path)

def send_email(pdf_path, recipient_email):
    msg = EmailMessage()
    msg["Subject"] = "Legal Document Analysis Results"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    msg.set_content("Please find attached the analysis results PDF.")

    with open(pdf_path, "rb") as file:
        msg.add_attachment(file.read(), maintype="application", subtype="pdf", filename="Analysis_Results.pdf")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def visualize_key_clauses_frequency(clauses):
    clause_counts = Counter(clauses)
    common_clauses = clause_counts.most_common()
    if common_clauses:
        labels, values = zip(*common_clauses)
        plt.figure(figsize=(10, 6))
        plt.barh(labels, values, color='skyblue')
        plt.xlabel('Frequency')
        plt.title('Key Clauses Frequency')
        st.pyplot(plt)
    else:
        st.write("No key clauses to visualize.")

def main():
    st.title("Interactive Legal Document Analysis Dashboard")

    # Sidebar options
    st.sidebar.title("Options")
    features = st.sidebar.multiselect("Select Features", 
                                       ["Data Visualization", "Summary", "Key Clauses", "Risk Detection", "Regulatory Updates"])

    # File upload
    uploaded_file = st.file_uploader("Upload a legal document (PDF)", type="pdf")
    recipient_email = st.text_input("Enter your email to receive the analysis results (optional)")

    if uploaded_file is not None:
        try:
            text = extract_text_from_pdf(uploaded_file)
            st.success("Text extracted successfully!")
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return

        summary = ""
        clauses, risks, updates = [], [], []

        if "Summary" in features:
            summary = summarize_text(text)
            st.subheader("Summary")
            st.write(summary)

        if "Key Clauses" in features:
            clauses = extract_key_clauses(text)
            st.subheader("Key Clauses")
            for i, clause in enumerate(clauses, 1):
                st.write(f"{i}. {clause}")
            # Visualize key clauses frequency
            if "Data Visualization" in features:
                visualize_key_clauses_frequency(clauses)

        if "Risk Detection" in features:
            risks = detect_risks(text)
            st.subheader("Detected Risks")
            st.write(", ".join(risks) if risks else "No risks detected.")

        if "Regulatory Updates" in features:
            updates = get_regulatory_updates()
            st.subheader("Regulatory Updates")
            for update in updates:
                st.write(f"- **{update.get('title')}**: {update.get('summary')}")

        # Generate PDF and send via email if required
        if st.button("Generate PDF Report"):
            pdf_path = "Analysis_Results.pdf"
            generate_pdf(summary, clauses, risks, updates, pdf_path)
            with open(pdf_path, "rb") as file:
                st.download_button("Download PDF Report", file, file_name="Analysis_Results.pdf", mime="application/pdf")

            # Email PDF
            if recipient_email:
                try:
                    validate_email(recipient_email)
                    send_email(pdf_path, recipient_email)
                    st.success(f"PDF sent to {recipient_email} successfully!")
                except EmailNotValidError:
                    st.error("Invalid email address. Please enter a valid one.")

if __name__ == "__main__":
    main()

