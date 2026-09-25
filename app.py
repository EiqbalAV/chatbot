"""
Streamlit Web UI for Local LLM Chatbot (LM Studio / Bionic).

Features:
- Real-time streaming chat responses
- Live connection indicator & health check
- Configurable generation parameters (Temperature, Max Tokens, System Prompt)
- Built-in educational guide on local LLM architectures
- GitHub-safe design (no hardcoded secrets or internal endpoints)
"""

import streamlit as st
from config import load_config
from llm_client import create_llm_client, test_connection, stream_chat_response

# 1. Page Configuration
st.set_page_config(
    page_title="Local AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Load Configuration from Environment
config = load_config()

# 3. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "connected" not in st.session_state:
    # Auto-probe on initial app launch
    init_client = create_llm_client(base_url=config.base_url, api_key=config.api_key, timeout=3.0)
    ok, msg, models = test_connection(init_client)
    st.session_state.connected = ok
    st.session_state.connection_msg = msg
    st.session_state.available_models = models

if "available_models" not in st.session_state:
    st.session_state.available_models = []

if "connection_msg" not in st.session_state:
    st.session_state.connection_msg = ""


# 4. Sidebar Controls
with st.sidebar:
    st.title("⚙️ Connection & Settings")

    st.markdown("### 🌐 Server Endpoint")
    server_url = st.text_input(
        "LM Studio / Bionic URL",
        value=config.base_url,
        help="The local address where LM Studio is listening (e.g. http://localhost:1234/v1 or http://bionic:1234/v1)",
    )

    api_key_input = st.text_input(
        "API Key (Optional)",
        value=config.api_key,
        type="password",
        help="LM Studio doesn't require an active key by default, but you can pass one here if needed.",
    )

    # Initialize client with current UI values
    client = create_llm_client(base_url=server_url, api_key=api_key_input or "lm-studio")

    col_test, col_clear = st.columns(2)
    with col_test:
        if st.button("🔌 Test Link", use_container_width=True):
            with st.spinner("Checking..."):
                ok, msg, models = test_connection(client)
                st.session_state.connected = ok
                st.session_state.connection_msg = msg
                st.session_state.available_models = models
                if ok:
                    st.toast("Connected to Local LLM!", icon="✅")
                else:
                    st.toast("Connection failed!", icon="⚠️")

    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Connection Status Banner
    if st.session_state.connected:
        st.success(f"🟢 **Connected**\n\n{st.session_state.connection_msg}")
    else:
        st.warning(
            "🔴 **Not Verified**\n\nClick **Test Link** to verify your connection to LM Studio / Bionic."
        )

    st.divider()

    st.markdown("### 🧠 Model Selection")
    if st.session_state.available_models:
        selected_model = st.selectbox(
            "Active Model",
            options=st.session_state.available_models,
            index=0,
        )
    else:
        selected_model = st.text_input(
            "Model Name / ID",
            value=config.model,
            help="In LM Studio, this can usually be 'default' to use the loaded model.",
        )

    with st.expander("🛠️ Generation Parameters", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.5,
            value=config.temperature,
            step=0.05,
            help="Higher values make output more random, lower values more deterministic.",
        )
        max_tokens = st.slider(
            "Max Tokens",
            min_value=128,
            max_value=8192,
            value=config.max_tokens,
            step=128,
            help="The maximum number of tokens to generate per response.",
        )
        system_prompt = st.text_area(
            "System Prompt",
            value=config.system_prompt,
            height=100,
            help="Instruct the model on its identity, tone, and formatting rules.",
        )

    st.divider()

    # Security Status Indicator
    st.markdown(
        """
        <div style="background-color: rgba(46, 125, 50, 0.1); border: 1px solid rgba(46, 125, 50, 0.3); border-radius: 8px; padding: 10px; font-size: 0.85em;">
            <strong>🔒 GitHub Security Ready</strong><br>
            • <code>.env</code> is ignored by <code>.gitignore</code><br>
            • No sensitive tokens hardcoded in source<br>
            • Safe to commit and push to public repos
        </div>
        """,
        unsafe_allow_html=True,
    )


# 5. Main Chat Area
st.title("🤖 Local LLM Chatbot")
st.caption("Powered by LM Studio & Streamlit • 100% Private & Running Locally")

# Display welcome message and quick starters if conversation is empty
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            """
            Hello! I am your local AI chatbot. I run completely on your machine via **LM Studio** without sending your data to any third-party cloud.
            
            **Quick Checklist to Start:**
            1. Ensure **LM Studio** has a model loaded in the **Local Server** tab.
            2. Verify the server is running on your target host/port.
            3. Click **🔌 Test Link** in the sidebar to confirm connectivity.
            4. Type a message below to start chatting!
            """
        )

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Type your message here..."):
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Render user message in UI
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Prepare payload for the local LLM
    # Prepend the system prompt as the first message
    conversation_payload = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        conversation_payload.append({"role": msg["role"], "content": msg["content"]})

    # 4. Stream response from the local LLM
    with st.chat_message("assistant"):
        response_generator = stream_chat_response(
            client=client,
            messages=conversation_payload,
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        full_response = st.write_stream(response_generator)

    # 5. Add assistant response to history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# 6. Educational Learning Section
with st.expander("💡 Learning Corner: How Does This Architecture Work?", expanded=False):
    st.markdown(
        """
        ### Architecture Overview
        ```
        [ Browser (Streamlit UI) ]
                     │
                     ▼  (Python OpenAI Client)
        [ app.py / llm_client.py ]
                     │
                     ▼  (HTTP POST /v1/chat/completions)
        [ LM Studio Local Server (Bionic / Localhost:1234) ]
                     │
                     ▼  (llama.cpp / GPU Inference)
        [ Local Open-Source LLM (e.g., Llama 3, Mistral, Qwen, Gemma) ]
        ```
        
        #### Key Concepts:
        1. **OpenAI-Compatible REST API**:
           LM Studio implements the exact same endpoint specifications as OpenAI (`/v1/chat/completions` and `/v1/models`). This means you can use the official `openai` Python SDK simply by changing `base_url="http://localhost:1234/v1"`.
        2. **Streaming with Server-Sent Events (SSE)**:
           Instead of waiting 10-30 seconds for the entire text to generate, the server streams individual tokens as they are predicted using HTTP chunked transfer. Streamlit's `st.write_stream()` listens to this generator and renders it instantly.
        3. **Conversation State**:
           LLMs are stateless functions: `f(context) -> next_token`. In this app, `st.session_state.messages` preserves the conversation thread and re-sends the recent dialogue turns with every prompt.
        4. **GitHub Security Practice**:
           All endpoints and configurations are loaded via `python-dotenv` from a `.env` file that is kept out of Git via `.gitignore`. The template file `.env.example` serves as a safe guide for other developers cloning your repo.
        """
    )
