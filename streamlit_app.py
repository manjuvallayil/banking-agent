import streamlit as st
from langchain_community.llms import Ollama
import pandas as pd
import fitz  # PyMuPDF
import io

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
st.info("✅ This app processes files locally and does not upload any data to external servers. Files are machine-read only and never viewed by a human.")

query = st.text_input("Ask a question about the statement")

if uploaded_file and query:
    st.info("🧠 Processing your question privately...")

    # Extract context based on file type
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

    # Call the local model
    llm = Ollama(model="mistral")
    response = llm.invoke(prompt)

    # Show the response
    st.markdown("### 💡 Answer")
    st.write(response)