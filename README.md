# 💬 Gemini Chatbot with FastAPI & MySQL

A smart chatbot powered by **FastAPI**, **Google Gemini API**, and **MySQL**.  
This project allows users to chat with an AI assistant and saves conversation history for each session.

---

## 🚀 Features

- **AI-powered chat** using Google Gemini API.
- **Session-based conversation** stored in MySQL.
- **FastAPI backend** with REST endpoints:
  - `/chat` → Send messages to AI.
  - `/history/{session_id}` → Retrieve chat history.
- **Frontend chat interface** with automatic session ID management.
- **CORS enabled** for easy integration with frontend.
- Error handling for server/API failures.

---

## 🛠 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** MySQL
- **API:** Google Gemini API
- **Frontend:** HTML, CSS, JavaScript
- **Environment Management:** python-dotenv

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/pmaheshwari1903/ChatBOT.git
cd gemini-chatbot
```

2. **Create virtual environment & activate**
```python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. **Install dependencies**
```pip install -r requirements.txt```

4. **Set environment variables**
```
Create a .env file:

GEMINI_API_KEY=your_gemini_api_key
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_DB=chatbot_db

```

5. **Run FastAPI server**
```
uvicorn main:app --reload
```

## 💻 Usage

Open the frontend index.html in a browser and start chatting with the AI chatbot. Chat history is automatically saved per session.


## 🔧 Project Structure

.
├── main.py            # FastAPI backend
├── models.py          # SQLAlchemy models
├── database.py        # MySQL connection setup
├── script.js          # Frontend JS logic
├── index.html         # Chat UI
├── requirements.txt   # Python dependencies
└── .env               # Environment variables


## ⚡ Future Improvements

User authentication for personalized sessions, WebSocket integration for real-time chat, deployment with Docker & cloud hosting, and support for multiple AI models.


## 📜 License

This project is MIT Licensed – see LICENSE for details.



## 🎉 Credits

Developed by PARTH MAHESHWARI. Powered by Google Gemini API, FastAPI, and MySQL.


TRY THIS CHAT BOT : https://chat-bot-git-main-pmaheshwari1903s-projects.vercel.app?_vercel_share=oaJb1uqcbtcwxNgllBTWhQ5JqNeex1gS
