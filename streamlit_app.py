import streamlit as st
import google.generativeai as genai
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
import datetime

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to send email
def send_email(recipient, subject, body):
    sender_email = st.secrets["SENDER_EMAIL"]
    sender_password = st.secrets["SENDER_PASSWORD"]
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
            server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Function to generate sales proposal
def generate_proposal(data, template):
    prompt = f"Generate a sales proposal based on the following data: {data.to_dict()} and using the template: {template}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Function to log proposals
def log_proposal(recipient, proposal):
    with open("proposal_log.txt", "a") as file:
        file.write(f"Recipient: {recipient}\n")
        file.write(f"Proposal: {proposal}\n")
        file.write(f"Date: {datetime.datetime.now()}\n")
        file.write("-" * 50 + "\n")

# Streamlit App UI
st.title("Sales Proposal Generator")
st.write("Generate and send personalized sales proposals using Generative AI.")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Email details
    email_col = st.selectbox("Select email column", df.columns)
    subject = st.text_input("Email Subject", "Your Sales Proposal")
    template = st.text_area("Proposal Template", "Dear [Name],\n\nWe are pleased to present our sales proposal...\n\nBest regards,\n[Company Name]")

    if st.button("Generate and Send Proposals"):
        for index, row in df.iterrows():
            recipient = row[email_col]
            try:
                validate_email(recipient)
                proposal = generate_proposal(row, template)
                st.write(f"Preview of Proposal for {recipient}:")
                st.write(proposal)
                
                if send_email(recipient, subject, proposal):
                    log_proposal(recipient, proposal)
                    st.success(f"Proposal sent to {recipient} successfully!")
                else:
                    st.error(f"Failed to send proposal to {recipient}")
            except EmailNotValidError as e:
                st.error(f"Invalid email: {recipient} - {e}")

if st.button("View Proposal Log"):
    with open("proposal_log.txt", "r") as file:
        st.text(file.read())
