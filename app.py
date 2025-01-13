import streamlit as st
from pdfminer.high_level import extract_text
import smtplib
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
import spacy
from collections import Counter
import heapq
import requests
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")


SENDER_EMAIL = "shreedeepthi2005@gmail.com"  # Your sender email
SENDER_PASSWORD = "qntm oher jqfz oflt"  # Your email password

def extract_keywords(text):

    doc = nlp(text.lower())

    
    words = [token.text for token in doc if token.is_alpha and not token.is_stop]

    word_freq = Counter(words)

    
    keywords = [word for word, _ in word_freq.most_common(10)]

    return keywords

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

def get_regulatory_updates():
    
    url = "https://www.regulations.gov"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        
        updates = soup.find_all('div', class_='update-info')  
        updates_text = "\n".join([update.get_text() for update in updates[:5]])  
        return updates_text
    except Exception as e:
        return f"Error fetching regulatory updates: {e}"

def detect_risks(text):
  
    risk_terms = ["penalty", "breach", "termination", "liability", "indemnification", "dispute", "default"]

    doc = nlp(text.lower())

    risk_detected = []
    for token in doc:
        if token.text.lower() in risk_terms:
            risk_detected.append(token.text)

    return list(set(risk_detected))  

def send_email(recipient_email, subject, body):
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def main():
    st.title("Legal Document Summarizer and Keyword Extractor with Risk Detection")

    uploaded_file = st.file_uploader("Upload a legal document (PDF)", type="pdf")
    if uploaded_file is not None:
        try:
            
            text = extract_text(uploaded_file)
            st.write("Document Text Extracted Successfully.")
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return

        option = st.selectbox(
            'What would you like to do?',
            ('Summarize', 'Extract Keywords', 'Risk Detection', 'Both')
        )

        summary, keywords, risks = "", [], []
        if option == 'Summarize' or option == 'Both':
            summary = summarize_text(text)
            st.write("Summary:")
            st.write(summary)

        if option == 'Extract Keywords' or option == 'Both':
            keywords = extract_keywords(text)
            st.write("Keywords:")
            st.write(", ".join(keywords))

        if option == 'Risk Detection' or option == 'Both':
            risks = detect_risks(text)
            st.write("Risk Indicators Detected:")
            st.write(", ".join(risks))

       
        regulatory_updates = get_regulatory_updates()
        st.write("Real-time Regulatory Updates:")
        st.write(regulatory_updates)

        email = st.text_input("Enter your email to receive the results:")
        if st.button("Send Email"):
            try:
                v = validate_email(email)
                email = v["email"]
                subject = "Legal Document Analysis Results"
                body = f"Summary:\n{summary}\n\nKeywords:\n{', '.join(keywords)}\n\nRisk Indicators:\n{', '.join(risks)}\n\nRegulatory Updates:\n{regulatory_updates}"
                send_email(email, subject, body)
            except EmailNotValidError as e:
                st.error(f"Invalid email: {e}")

if __name__ == "__main__":
    main()
