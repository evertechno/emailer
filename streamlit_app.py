import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure the API key securely
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("AI Sales Proposal Generator")

# File Uploader
uploaded_file = st.file_uploader("Upload your CSV file")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract customer information
        customer_name = row['customer_name']
        customer_email = row['customer_email']
        customer_needs = row['customer_needs']

        # Generate personalized prompt for Gemini AI
        prompt = f"Write a compelling sales proposal for {customer_name} at {customer_company}. Address their specific needs: {customer_needs}. Highlight the benefits of our product/service."

        # Generate the sales proposal
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        proposal_text = response.text

        # Send the email
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = customer_email
        message['Subject'] = "Personalized Sales Proposal"

        message.attach(MIMEText(proposal_text, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, 1  customer_email, message.as_string())

        st.write(f"Email sent to {customer_name} at {customer_email}")
