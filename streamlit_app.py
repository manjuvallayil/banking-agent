import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from transformers import pipeline

# Load the text2text-generation pipeline locally
generator = pipeline("text2text-generation", model="google/flan-t5-small")

def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

st.set_page_config(page_title="Banking Agent", layout="wide")
st.title("🏦 Banking Insight Agent")

uploaded_file = st.file_uploader("Upload a bank statement (CSV or PDF)", type=["csv", "pdf"])
st.info("✅ All processing happens locally; no data is uploaded.")

query = st.text_input(
    "What would you like to know from this statement before making a funding decision?",
    placeholder="Enter your query here..."
)

if uploaded_file and query:
    st.info("🧠 Processing your question locally...")

    if uploaded_file.name.endswith(".pdf"):
        context = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        context = df.to_csv(index=False)
    else:
        st.error("Unsupported file type.")
        st.stop()

    prompt = f"You are a banking analyst. Here is a bank statement:\n{context}\n\nQuestion: {query}"

    result = generator(prompt, max_length=150, do_sample=False)[0]['generated_text']

    st.markdown("### 💡 Answer")
    st.write(result)