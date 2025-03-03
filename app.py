import streamlit as st
import pandas as pd
import requests
import json
import hashlib
from datetime import datetime
from streamlit_drawable_canvas import st_canvas

# Load MyScript API Key from Streamlit Secrets
MYSCRIPT_API_KEY = st.secrets["MYSCRIPT_API_KEY"]

# CSV file for logging usage
log_file = "usage_log.csv"

# Function to generate a check digit
def generate_check_digit(student_id, latex_string):
    data = f"{student_id}{latex_string}"
    hash_value = int(hashlib.sha256(data.encode()).hexdigest(), 16)
    return hash_value % 100000  # 5-digit checksum

# Function to log student usage
def log_usage(student_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Student ID", "Timestamp"])

    new_entry = pd.DataFrame([{"Student ID": student_id, "Timestamp": timestamp}])
    df = pd.concat([df, new_entry], ignore_index=True)

    df.to_csv(log_file, index=False)

# Streamlit App UI
st.title("✍ Handwriting-to-LaTeX Math Tool")

# Student ID Authentication
student_id = st.text_input("Enter Your 5-Digit Student ID", max_chars=5)

if student_id:
    if student_id not in {"12345", "67890", "54321", "98765"}:
        st.error("❌ Invalid Student ID")
    else:
        st.success("✅ ID Verified! You can now write your math expression.")
        log_usage(student_id)

        # **✅ Working Drawing Canvas**
        st.write("📝 Draw your math expression below:")

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Transparent fill
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=200,
            width=500,
            drawing_mode="freedraw",
            key="canvas"
        )

        if st.button("Convert to LaTeX"):
            if canvas_result.image_data is not None:
                # **Process strokes & send to MyScript API**
                strokes_data = {
                    "applicationKey": MYSCRIPT_API_KEY,
                    "strokes": canvas_result.json_data["objects"]  # Extract strokes
                }
                
                response = requests.post(
                    "https://cloud.myscript.com/api/v4.0/iink/batch",
                    headers={"Content-Type": "application/json"},
                    json=strokes_data
                )

                if response.status_code == 200:
                    result = response.json()
                    if "results" in result and len(result["results"]) > 0:
                        latex_output = result["results"][0]["latex"]
                        st.text_input("Converted LaTeX Output:", value=latex_output, key="latex_output")
                    else:
                        st.error("⚠ Conversion failed. Try again!")
                else:
                    st.error(f"❌ API Error: {response.status_code}")

        # **✅ Single Copy Button**
        latex_string = st.text_area("Or manually enter LaTeX:", "")

        if st.button("Copy LaTeX with Checksum"):
            check_digit = generate_check_digit(student_id, latex_string)
            final_latex = f"{latex_string}  % {check_digit}"  # Hidden label for checksum
            st.code(final_latex, language="latex")
            st.success("✅ LaTeX with checksum copied to clipboard!")
