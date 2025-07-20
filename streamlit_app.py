import os
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from huggingface_hub import InferenceClient

# Load the token securely
hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

# Initialize the Hugging Face InferenceClient
client = InferenceClient(
    model="google/flan-t5-large", token=hf_token
)

# 🔍 Utility to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

st.set_page_config(page_title="Banking Agent", layout="wide")
st.title("🏦 Banking Insight Agent")

uploaded_file = st.file_uploader("Upload a bank statement", type=["csv", "pdf"])
st.info("✅ This app processes files within the cloud environment and does not store any data permanently. Files are machine-read only and never viewed by a human.")

query = st.text_input(
    "What would you like to know from this statement before making a funding decision?",
    placeholder="Enter your query here..."
)

if uploaded_file and query:
    st.info("🧠 Processing your question...")

    # Extract context
    if uploaded_file.name.endswith(".pdf"):
        context = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        context = df.to_csv(index=False)
    else:
        st.error("Unsupported file type.")
        st.stop()

    # Prepare the prompt
    prompt = f"""You are a banking analyst. Here is a bank statement:\n{context}\n\nQuestion: {query}"""

    # Get the response from Hugging Face Inference API
    response = client.text_generation(
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.5
    )

    st.markdown("### 💡 Answer")
    st.write(response)