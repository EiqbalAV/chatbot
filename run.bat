@echo off
echo Starting Local LLM Chatbot...
call .venv\Scripts\activate.bat
streamlit run app.py
pause
