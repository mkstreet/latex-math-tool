import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

# Load secrets from Streamlit
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = st.secrets["EMAIL_RECEIVER"]

# CSV file for logging usage
log_file = "usage_log.csv"

# Function to log student usage (remains, but no buttons shown)
def log_usage(student_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Student ID", "Timestamp"])

    # Fix: Ensure proper DataFrame format
    new_entry = pd.DataFrame([{"Student ID": student_id, "Timestamp": timestamp}])
    df = pd.concat([df, new_entry], ignore_index=True)

    df.to_csv(log_file, index=False)

# Streamlit App UI (NO ADMIN BUTTONS)
st.title("📝 Handwriting-to-LaTeX Math Tool")

# Student ID Authentication
student_id = st.text_input("Enter Your 5-Digit Student ID", max_chars=5)

if student_id:
    if student_id not in {"12345", "67890", "54321", "98765"}:
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
            check_digit = int(hash(str(student_id) + latex_string) % 100000)
            final_latex = f"{latex_string}  % {check_digit}"  # Hidden label for checksum
            st.code(final_latex, language="latex")
            st.success("✅ LaTeX copied to clipboard!")
