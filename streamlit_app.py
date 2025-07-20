import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import requests

# 🔐 Load Hugging Face token from secrets
hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {hf_token}"}

# 🧠 Query the Hugging Face Inference API
def query_huggingface(prompt):
    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.5
            }
        })

        if response.status_code == 503:
            return "⏳ Model is loading. Please wait a few seconds and try again."
        if response.status_code != 200:
            return f"❌ API returned status {response.status_code}: {response.text}"

        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            return f"❌ Error from model: {result['error']}"
        else:
            return "⚠️ Unexpected response format."

    except requests.exceptions.JSONDecodeError:
        return "❌ Failed to decode response (model may still be loading)."
    except Exception as e:
        return f"❌ Request failed: {str(e)}"

# 📄 Extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# 🧾 Streamlit UI
st.set_page_config(page_title="Banking Agent", layout="wide")
st.title("🏦 Banking Insight Agent")

uploaded_file = st.file_uploader("Upload a bank statement (CSV or PDF)", type=["csv", "pdf"])
st.info("✅ This app processes files within the cloud environment and does not store any data permanently. Files are machine-read only and never viewed by a human.")

query = st.text_input(
    "What would you like to know from this statement before making a funding decision?",
    placeholder="Enter your question here..."
)

if uploaded_file and query:
    st.info("🧠 Processing your question...")

    # Get context from the uploaded file
    if uploaded_file.name.endswith(".pdf"):
        context = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        context = df.to_csv(index=False)
    else:
        st.error("Unsupported file type.")
        st.stop()

    # Construct the prompt
    prompt = f"""You are a banking analyst. Here is a bank statement:\n{context}\n\nQuestion: {query}"""

    # Get the response
    response = query_huggingface(prompt)

    st.markdown("### 💡 Answer")
    st.write(response)