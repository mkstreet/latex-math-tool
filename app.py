import streamlit as st
import hashlib
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

# Load secrets from Streamlit
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = st.secrets["EMAIL_RECEIVER"]

# Simulated list of approved student IDs
approved_ids = {"12345", "67890", "54321", "98765"}

# CSV file for logging usage
log_file = "usage_log.csv"

# Function to generate check digit
def generate_check_digit(student_id, latex_string):
    data = f"{student_id}{latex_string}"
    hash_value = int(hashlib.sha256(data.encode()).hexdigest(), 16)
    return hash_value % 100000  # 5-digit check digit

# Function to log student usage
def log_usage(student_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Student ID", "Timestamp"])

    df = pd.concat({"Student ID": student_id, "Timestamp": timestamp}, ignore_index=True)
    df.to_csv(log_file, index=False)

# Function to send email with usage log
def send_usage_log():
    if os.path.exists(log_file):
        msg = EmailMessage()
        msg["Subject"] = "Daily Student Usage Log"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("Attached is the daily student usage log for the handwriting-to-LaTeX tool.")

        # Attach CSV file
        with open(log_file, "rb") as file:
            msg.add_attachment(file.read(), maintype="application", subtype="csv", filename="usage_log.csv")

        # Send email securely via SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        # Clear the log file after sending
        open(log_file, "w").close()
        st.sidebar.success("📧 Daily usage log emailed and cleared.")

# Streamlit App UI
st.title("📝 Handwriting-to-LaTeX Math Tool")

# Student ID Authentication
student_id = st.text_input("Enter Your 5-Digit Student ID", max_chars=5)

if student_id:
    if student_id not in approved_ids:
        st.error("❌ Invalid Student ID")
    else:
        st.success("✅ ID Verified! You can now write your math expression.")
        log_usage(student_id)

        # MyScript Handwriting Input
        st.write("✍ Write your math expression below:")
        st.markdown(
            '<iframe src="https://webdemo.myscript.com/views/math/index.html" width="100%" height="400"></iframe>',
            unsafe_allow_html=True
        )

        # LaTeX Input Box
        latex_string = st.text_area("Or manually enter LaTeX:", "")

        if st.button("Copy LaTeX"):
            check_digit = generate_check_digit(student_id, latex_string)
            final_latex = f"{latex_string}  % {check_digit}"  # Hidden label for checksum
            st.code(final_latex, language="latex")
            st.success("✅ LaTeX copied to clipboard!")

# Admin Panel: View Student Usage Log & Send Email
if st.sidebar.checkbox("📊 View Usage Log (Admin)"):
    try:
        df = pd.read_csv(log_file)
        st.sidebar.dataframe(df)
    except FileNotFoundError:
        st.sidebar.warning("No usage data available.")

if st.sidebar.button("📧 Send Daily Report & Clear Log"):
    send_usage_log()
