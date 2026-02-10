```markdown
# Mail Assistant (Single-User Edition)

An AI-powered Email Assistant built with **FastAPI**, **LangGraph**, **PostgreSQL**, and the **Gmail API**.

This project enables intelligent email interactions including unread email retrieval, important email summarization, deadline extraction, and email drafting — all powered by an LLM-driven workflow engine.

---

## 🚀 Overview

Mail Assistant is a backend-driven AI system that:

- Retrieves unread email counts
- Fetches and filters important emails
- Summarizes email content using an LLM
- Extracts deadlines and converts them into structured tasks
- Drafts and sends emails with confirmation
- Maintains persistent conversation state in PostgreSQL

This version supports **single-user Gmail integration** via OAuth 2.0.

---

## 🏗 Architecture

### Backend
- FastAPI
- LangGraph (stateful agent workflow)
- SQLAlchemy
- PostgreSQL
- Gmail API (OAuth 2.0)
- LLM Service Integration

### Frontend (Optional)
- Streamlit

### Persistence
- PostgreSQL for conversation history
- Local OAuth token storage (`token.json`)

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Santu004/MailAssistant_SingleUser.git
cd MailAssistant_SingleUser
````

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Gmail API Configuration

### Enable Gmail API

1. Visit Google Cloud Console
2. Create a new project
3. Enable **Gmail API**
4. Create OAuth 2.0 credentials (Desktop App)
5. Download the credentials JSON

Place the file inside:

```
backend/
```

Rename it to:

```
credentials.json
```

---

## 🗄 Database Setup (PostgreSQL)

Create database:

```sql
CREATE DATABASE mailassistant2;
```

Tables are automatically created on application startup.

---

## 🔧 Environment Configuration

Create a `.env` file inside `backend/`:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost/mailassistant2
GOOGLE_CLIENT_SECRET_FILE=backend/credentials.json
GOOGLE_TOKEN_FILE=backend/token.json
```

---

## ▶️ Running the Application

### Start Backend

```bash
uvicorn backend.app.main:app --reload
```

API available at:

```
http://127.0.0.1:8000
```

---

### Optional: Run Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

## 🧠 Core Features

### Email Operations

* Unread email count (supports optional date filtering)
* Important email retrieval with system email filtering
* Email summarization (LLM-powered)
* Email drafting with confirmation workflow
* Email sending via Gmail API

### Intelligence Layer

* Intent detection
* State-based workflow orchestration (LangGraph)
* Deadline extraction
* Structured task generation

### Persistence

* Conversation state stored in PostgreSQL
* Session-based history tracking

---

## 🔒 Security Notes

Sensitive files are excluded via `.gitignore`:

* `.venv/`
* `.env`
* `token.json`
* `credentials.json`
* Database files

This project is configured for **local development use**.

---

## 🛠 Development Workflow

Typical update cycle:

```bash
git add .
git commit -m "Meaningful commit message"
git push origin main
```


## 👨‍💻 Author

**Sayan Kr Maiti**
GitHub: [https://github.com/Santu004](https://github.com/Santu004)

