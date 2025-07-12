# Base image with Ollama preinstalled
FROM ollama/ollama:latest

# Set working directory inside container
WORKDIR /app

# Install Python and pip, skip recommended packages to keep image lean
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip

# Copy local files into container
COPY . /app

# Create and use a virtual environment
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install --break-system-packages --no-cache-dir -r requirements.txt

# Expose ports for Ollama (11434) and Streamlit (8501)
EXPOSE 11434 8501

# Disable default Ollama entrypoint so we control what runs
ENTRYPOINT []

# Pull model only if not already cached, then start Ollama + Streamlit
CMD ["sh", "-c", "\
  ollama serve & \
  sleep 10 && \
  echo '🔄 Pulling model (if needed)...' && \
  ollama list | grep -q mistral || ollama pull mistral && \
  echo '🚀 Launching Streamlit...' && \
  /opt/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]