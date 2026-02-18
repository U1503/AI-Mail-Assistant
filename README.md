🚀 AI Mail Assistant

An AI-powered Email Assistant built using FastAPI, LangGraph, Groq LLM, Gmail API, and PostgreSQL.
Draft, modify, and send emails intelligently using natural language.

✨ Features

  * 🤖 AI-powered email drafting using Groq LLM
  * 📧 Send real emails via Gmail API
  * 🧠 Agent-based workflow using LangGraph
  * 💾 PostgreSQL for chat & history persistence
  * 🔐 Secure OAuth 2.0 authentication
  * 🌐 Interactive Streamlit frontend
  * 🧩 Modular backend architecture


🏗️ Architecture Overview
```bash
User → Streamlit UI → FastAPI Backend → LangGraph Agent → LLM (Groq) → Gmail Tool → PostgreSQL → Response to UI
```

🛠️ Tech Stack
                         Layer	                               Technology
                         Backend	                             FastAPI
                         Agent Framework	                     LangGraph
                         LLM	Groq                             (LLaMA 3.1)
                         Database	                             PostgreSQL
                         Frontend	                             Streamlit
                         Authentication                        Gmail OAuth 2.0

📂 Project Structure

                            ```bash
                            AI-Mail-Assistant/
                            │
                            ├── backend/
                            │   ├── app/
                            │   │   ├── agents/
                            │   │   ├── api/
                            │   │   ├── core/
                            │   │   ├── services/
                            │   │   └── main.py
                            │   ├── .env
                            │   └── credentials.json (ignored)
                            │
                            ├── frontend/
                            │   └── app.py
                            │
                            ├── requirements.txt
                            └── README.md
                            ```
                            

⚙️ Setup Instructions
1️⃣ Clone Repository
  ```bash      
  git clone https://github.com/YOUR_USERNAME/AI-Mail-Assistant.git
  cd AI-Mail-Assistant
  ```


2️⃣ Create Virtual Environment
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

3️⃣ Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

4️⃣ Configure Environment Variables
Create .env inside backend:
   ```env      
    APP_NAME=Mail Assistant
    ENV=development
    DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/mailassistant2
    GOOGLE_CLIENT_SECRET_FILE=credentials.json
    GOOGLE_TOKEN_FILE=token.json
    GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.send
    GROQ_API_KEY=your_groq_api_key
    LLM_MODEL=llama-3.1-8b-instant
   ```       
5️⃣ Setup PostgreSQL
   ```sql  
   CREATE DATABASE mailassistant2;
   ``` 
6️⃣ Run Backend
   ```bash
    cd backend
    uvicorn app.main:app --reload
   ```
7️⃣ Run Frontend
   ```bash
    cd frontend
    streamlit run app.py
   ```
🔐 Security

Sensitive files excluded via .gitignore:

  * .env
  * credentials.json
  * token.json
  * venv/
  * Database files
 
🧠 How It Works

  1. User sends natural language request.
  2. LangGraph determines intent.
  3. LLM extracts email details (to, subject, body).
  4. Confirmation step before sending.
  5. Gmail API sends email.
  6. Chat history stored in PostgreSQL.

🚀 Future Improvements

  * Real-time weather API integration
  * Multi-user authentication
  * Docker deployment
  * Cloud hosting (AWS / Render)
  * Advanced email classification
  * Logging & monitoring

👨‍💻 Author

Udit Narayan Sah

GitHub: https://github.com/U1503
  

                         
