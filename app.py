import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

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

        # MyScript Handwriting Input (WITHOUT the extra Copy Button)
        st.write("Write your math equation below:")

        st.markdown(
            """
            <iframe id="myscriptFrame" src="https://webdemo.myscript.com/views/math/index.html"
            width="100%" height="400" style="border: none;"></iframe>
            
            <br>
            <label>Converted LaTeX Output:</label>
            <input type="text" id="latexOutput" readonly style="width: 100%; padding: 5px; font-size: 16px;">
            <br>
            <button onclick="copyLatex()" style="padding: 8px 12px; font-size: 16px;">📋 Copy LaTeX</button>

            <script>
                function copyLatex() {
                    var iframe = document.getElementById("myscriptFrame").contentWindow;
                    var latexField = document.getElementById("latexOutput");

                    // Extract LaTeX from iframe
                    iframe.postMessage({ type: 'EXPORT', mimeType: 'application/x-latex' }, '*');

                    window.addEventListener('message', function(event) {
                        if (event.data.type === 'EXPORT' && event.data.mimeType === 'application/x-latex') {
                            latexField.value = event.data.data;
                        }
                    });

                    // Copy to clipboard
                    latexField.select();
                    document.execCommand("copy");
                    alert("LaTeX copied to clipboard!");
                }
            </script>
            """,
            unsafe_allow_html=True
        )

        # LaTeX Input Box (for manually entered LaTeX)
        latex_string = st.text_area("Or manually enter LaTeX:", "")

        if st.button("Copy LaTeX with Checksum"):
            check_digit = generate_check_digit(student_id, latex_string)
            final_latex = f"{latex_string}  % {check_digit}"  # Hidden label for checksum
            st.code(final_latex, language="latex")
            st.success("✅ LaTeX copied to clipboard!")
