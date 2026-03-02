# LMS Chatbot Profile Updater

A Learning Management System (LMS) with an AI-powered chatbot assistant that helps students manage their profile, education details, course applications, and more.

## 🔗 Links

| Resource | Link |
|----------|------|
| 🚀 Deployed Backend | `https://chatbot-profile-updater.onrender.com` |
| 🌐 Deployed Frontend | `https://chatbot-profile-updater.vercel.app` |
| 🎨 Figma Design | `https://www.figma.com/design/9xDbJwhaCoETyeeJcfwHF7/LMS_Update_ChatBot?node-id=0-1&t=NafuzwdOtFzkRgnr-1` |
| 📦 GitHub Repository | `https://github.com/Lakshmi-Shankar/chatbot-profile-updater` |

---

## 📌 Project Overview

This project is a full-stack LMS portal where students can:
- Register and login securely
- View and update their personal profile
- Add and update education details (10th and 12th board)
- Browse available courses
- Apply to courses and track application status
- Use an **AI chatbot** to perform all of the above via natural language

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI | REST API framework |
| SQLite | Database |
| LangChain + LangGraph | AI agent framework |
| Groq (llama-3.3-70b-versatile) | LLM for chatbot |
| PyJWT | Authentication (JWT) |
| bcrypt | Password hashing |
| Render | Deployment |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React + Vite | UI framework |
| Tailwind CSS | Styling |
| React Router | Client-side routing |

---

## 📁 Project Structure

```
chatbot-profile-updater/
├── Backend/
│   ├── Router/
│   │   ├── auth.py           # Register & login
│   │   ├── profile.py        # Profile CRUD
│   │   ├── Education.py      # Education CRUD
│   │   ├── Courses.py        # Course CRUD
│   │   ├── Application.py    # Application CRUD
│   │   ├── Chatbot.py        # AI chatbot agent
│   │   └── Tools.py          # LangChain tools
│   ├── authVerify.py         # JWT middleware
│   ├── databaseConnect.py    # SQLite connection
│   ├── server.py             # FastAPI app entry point
│   ├── schema.sql            # Database schema
│   └── requirements.txt
│
└── Client/
    ├── src/
    │   ├── pages/
    │   │   ├── authPage.jsx      # Login & Register
    │   │   └── dashboardPage.jsx # Main dashboard
    │   ├── App.jsx
    │   └── main.jsx
    └── package.json
```

---

## 🚀 Getting Started

### Backend Setup
```bash
cd Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key
```

Run the server:
```bash
uvicorn server:app --reload
```

### Frontend Setup
```bash
cd Client
npm install
npm run dev
```

---

## 🤖 Chatbot Capabilities

The AI assistant can handle natural language requests like:

- *"Show my profile"*
- *"Update my phone to 9876543210"*
- *"Add my education: 10th CBSE 85%, 12th CBSE 90%"*
- *"Show all available courses"*
- *"Enroll me in the DSA course"*
- *"What is the status of my application?"*
- *"Cancel my application for course ID 2"*

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new student |
| POST | `/auth/login` | Login and get JWT token |

### Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile/` | Get profile + education |
| PATCH | `/profile/` | Update profile fields |

### Education
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/education/` | Get education details |
| POST | `/education/` | Add education details |
| PATCH | `/education/` | Update education details |

### Courses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/` | Get all courses |
| GET | `/courses/{id}` | Get course by ID |
| POST | `/courses/` | Add new course |
| PATCH | `/courses/{id}` | Update course |
| DELETE | `/courses/{id}` | Delete course |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/application/` | Get all applications |
| POST | `/application/` | Apply to a course |
| PATCH | `/application/{id}` | Update application status |
| DELETE | `/application/{id}` | Cancel application |

### Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chatbot/chat` | Send message to AI agent |


