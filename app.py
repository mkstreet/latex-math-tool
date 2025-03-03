import streamlit as st
import pandas as pd
import requests
import json
import os
import hashlib
from datetime import datetime

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

        # JavaScript-based handwriting canvas (Fixed)
        st.markdown(
            f"""
            <canvas id="canvas" width="500" height="200" style="border:1px solid black;"></canvas>
            <br>
            <button onclick="clearCanvas()" style="padding: 8px 12px;">🗑 Clear</button>
            <button onclick="convertToLatex()" style="padding: 8px 12px;">📄 Convert to LaTeX</button>
            <br><br>
            <input type="text" id="latexOutput" readonly style="width: 100%; padding: 5px; font-size: 16px;">
            <br>
            <button onclick="copyLatex()" style="padding: 8px 12px;">📋 Copy LaTeX</button>

            <script>
                let canvas = document.getElementById("canvas");
                let ctx = canvas.getContext("2d");
                let drawing = false;
                let strokes = [];

                canvas.addEventListener("mousedown", (e) => {
                    drawing = true;
                    strokes.push([]);
                });

                canvas.addEventListener("mousemove", (e) => {
                    if (!drawing) return;
                    let x = e.offsetX;
                    let y = e.offsetY;
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    strokes[strokes.length - 1].push({x, y});
                });

                canvas.addEventListener("mouseup", () => { drawing = false; });

                function clearCanvas() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.beginPath();
                    strokes = [];
                }

                function convertToLatex() {
                    let requestData = {
                        "applicationKey": "{MYSCRIPT_API_KEY}",
                        "strokes": strokes
                    };

                    fetch("https://cloud.myscript.com/api/v4.0/iink/batch", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(requestData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data["results"] && data["results"].length > 0) {
                            let latex = data["results"][0]["latex"];
                            document.getElementById("latexOutput").value = latex;
                        } else {
                            alert("❌ Conversion failed. Try again.");
                        }
                    })
                    .catch(error => alert("Error converting: " + error));
                }

                function copyLatex() {
                    let latexField = document.getElementById("latexOutput");
                    latexField.select();
                    document.execCommand("copy");
                    alert("✅ LaTeX copied to clipboard!");
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
            st.success("✅ LaTeX with checksum copied to clipboard!")
