Legal Document Analysis Dashboard
An interactive Streamlit-based web application for analyzing legal documents. This application provides various functionalities, including text summarization, key clause extraction, risk detection, and real-time regulatory updates. It also allows users to generate PDF reports and email them for further use.

Features
Data Visualization: Displays word frequency bar charts for better insights into the document.
Key Clause Extraction: Extracts and displays the most significant clauses from the document.
Risk Detection: Identifies predefined risk-related words in the document (e.g., "fraud", "penalty").
Regulatory Updates: Fetches and displays the latest updates from the SEC newsroom.
Text Summarization: Summarizes the document into a concise version.
PDF Report Generation: Creates a comprehensive report of the analysis in PDF format.
Email PDF Reports: Sends the generated PDF report to the specified email address.
Prerequisites
Before running this application, ensure you have the following installed:

Python 3.7 or above
Git
Required Python libraries (see Installation)
Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/yourusername/legal-document-analysis.git
cd legal-document-analysis
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set up email credentials:
Replace the placeholders in the code (SENDER_EMAIL and SENDER_PASSWORD) with your email credentials for sending reports.

Run the application:

bash
Copy
Edit
streamlit run app.py
