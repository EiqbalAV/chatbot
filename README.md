# 🤖 Local LLM Chatbot (LM Studio / Bionic)

A lightweight, secure, and modern local chatbot web app built with **Python**, **Streamlit**, and the **OpenAI Python SDK**, designed to connect directly to **LM Studio** (or any OpenAI-compatible local/network LLM endpoint like `bionic`).

This project is built with **learning** and **security best practices** in mind—ready to be safely published to **GitHub** without leaking internal IP addresses, ports, or credentials.

---

## 🌟 Key Features

- **100% Private & Local**: Zero data is transmitted to external cloud providers. All inference runs directly on your machine or local network.
- **Real-Time Token Streaming**: Watch responses generate word-by-word with low latency via Server-Sent Events (SSE).
- **One-Click Connection Health Check**: Built-in diagnostic tool and UI indicator to verify LM Studio connectivity and list available models.
- **Interactive UI**: Powered by Streamlit with real-time sliders for Temperature, Max Tokens, and custom System Prompts.
- **GitHub Security First**: Pre-configured `.gitignore` and `.env.example` templates to prevent secret or IP leakage.
- **Educational Architecture**: Clean, modular code with comments explaining local LLM client-server mechanics.

---

## 🔒 Security & Safe GitHub Publishing

When publishing projects to public GitHub repositories, **never** commit:
1. Hardcoded internal IP addresses or server hostnames (`bionic:1234`, `192.168.x.x`).
2. API keys or authorization tokens.
3. Virtual environments (`.venv/`) or Python cache files (`__pycache__/`).

### How this project keeps you safe:
- **`.gitignore`**: Automatically ignores `.env`, `.venv/`, `__pycache__/`, logs, and temporary files.
- **`.env.example`**: Safe placeholder template checked into Git. Developers copy it locally to `.env`.
- **`config.py`**: Centralized, validated environment configuration with fallback defaults.

> [!IMPORTANT]
> Always verify with `git status` before committing. Ensure `.env` is **never** listed under tracked or staged files!

---

## 📁 Project Structure

```
chatbot/
├── .env.example        # Safe template for environment variables (tracked in Git)
├── .gitignore          # Prevents .env, .venv, and caches from being committed
├── config.py           # Safe configuration loader and endpoint normalizer
├── llm_client.py       # OpenAI-compatible client wrapper for LM Studio & streaming
├── test_connection.py  # Quick CLI diagnostic script to test your LM Studio link
├── app.py              # Main Streamlit web application
├── requirements.txt    # Python dependencies
└── README.md           # Documentation and learning guide
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+**
- **LM Studio** installed and running on your machine or on your network (`bionic`).

### 2. Set Up Virtual Environment
Open PowerShell or your terminal in this project folder:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Your LM Studio / Bionic Link
Copy the template to create your personal local configuration:
```powershell
Copy-Item .env.example .env
```

Open `.env` in any text editor and adjust the settings to match your setup:
```env
# If LM Studio is running locally on the same PC:
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# If LM Studio is on another machine (e.g., named 'bionic' or an IP):
# LM_STUDIO_BASE_URL=http://bionic:1234/v1
# LM_STUDIO_BASE_URL=http://192.168.1.50:1234/v1

LM_STUDIO_API_KEY=lm-studio
LM_STUDIO_MODEL=default
```

### 5. Start LM Studio Local Server
1. Open **LM Studio**.
2. Click the **Local Server** icon (`<->`) in the left sidebar.
3. Select and load a model from the top dropdown (e.g. Llama 3, Mistral, Qwen 2.5, Gemma 2).
4. Click **Start Server**.
5. (Optional) If connecting from another device on the same local network, enable **"Serve on Local Network (0.0.0.0)"** and note the port (default `1234`).

### 6. Test Your Connection (CLI)
Before launching the UI, test that Python can communicate with your local LLM:
```powershell
python test_connection.py
```
You should see:
```
✅ CONNECTION SUCCESSFUL!
Successfully connected to local LLM server!
```

### 7. Run the Web Chatbot
Launch the Streamlit app:
```powershell
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## 💡 Learning Corner: How It Works

### 1. Why OpenAI SDK for LM Studio?
LM Studio implements an **OpenAI-compatible REST API**. When you set:
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
```
Every standard API call (`client.chat.completions.create(...)`, `client.models.list()`) maps directly to LM Studio's embedded inference engine without requiring proprietary vendor libraries.

### 2. Streaming Responses with Server-Sent Events (SSE)
Instead of waiting for the LLM to generate the entire paragraph, setting `stream=True` causes the server to emit chunks over an open HTTP connection:
```python
response = client.chat.completions.create(
    model="default",
    messages=[{"role": "user", "content": "Explain quantum computing in 1 sentence."}],
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)
```
Streamlit's `st.write_stream()` consumes this generator directly and renders each token with natural animation.

### 3. Context Window & Stateless Inference
LLMs have no built-in memory across requests. To maintain conversation context, the client stores previous messages (`st.session_state.messages`) and re-submits the entire dialogue history with every new question:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Hello Alice! How can I help you today?"},
    {"role": "user", "content": "What is my name?"}
]
```

---

## 🛠️ GitHub Publishing Checklist

When you are ready to push this repo to GitHub:
```powershell
# 1. Initialize git (if not already done)
git init

# 2. Check that .env is NOT tracked
git status
# Make sure .env is not in the list! Only .env.example should be present.

# 3. Stage and commit files
git add .
git commit -m "Initial commit: local LLM chatbot with Streamlit and LM Studio support"

# 4. Push to your GitHub repository
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```
