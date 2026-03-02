# Low Level Design (LLD) — LMS Chatbot Profile Updater

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│                  React + Vite + Tailwind                │
│                                                         │
│   ┌─────────────┐          ┌──────────────────────┐    │
│   │  AuthPage   │          │    DashboardPage     │    │
│   │  (Login /   │          │  (Profile, Courses,  │    │
│   │  Register)  │          │  Applications, Chat) │    │
│   └──────┬──────┘          └──────────┬───────────┘    │
└──────────┼─────────────────────────────┼───────────────┘
           │ HTTP (fetch)                │ HTTP (fetch)
           ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│                      BACKEND                            │
│                  FastAPI + Uvicorn                      │
│                                                         │
│  ┌──────┐ ┌─────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Auth │ │ Profile │ │Education │ │    Courses    │  │
│  └──────┘ └─────────┘ └──────────┘ └───────────────┘  │
│                                                         │
│  ┌─────────────┐        ┌──────────────────────────┐   │
│  │ Application │        │         Chatbot          │   │
│  └─────────────┘        │  LangGraph ReAct Agent   │   │
│                         │  + LangChain Tools       │   │
│                         └────────────┬─────────────┘   │
└──────────────────────────────────────┼─────────────────┘
                                       │ API Call
                    ┌──────────────────┼──────────────┐
                    │    GROQ API      │              │
                    │  llama-3.3-70b   ◄──────────────┘
                    └──────────────────┘
           │
           ▼
┌─────────────────┐
│   SQLite DB     │
│  database.db    │
└─────────────────┘
```

---

## 2. Database Schema

### students
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| full_name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password | TEXT | NOT NULL (bcrypt hashed) |
| phone | TEXT | nullable |
| date_of_birth | TEXT | nullable |
| city | TEXT | nullable |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### education_details
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| student_id | INTEGER | NOT NULL, UNIQUE, FK → students.id |
| tenth_board | TEXT | nullable |
| tenth_percentage | INTEGER | nullable |
| twelfth_board | TEXT | nullable |
| twelfth_percentage | INTEGER | nullable |

### courses
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| title | TEXT | NOT NULL |
| duration_months | INTEGER | nullable |
| fee | INTEGER | nullable |

### applications
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| student_id | INTEGER | NOT NULL, FK → students.id |
| course_id | INTEGER | NOT NULL, FK → courses.id |
| status | TEXT | CHECK: submitted/under_review/accepted/rejected/pending |
| applied_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

**Relationships:**
```
students (1) ──── (1) education_details
students (1) ──── (N) applications
courses  (1) ──── (N) applications
```

---

## 3. Authentication Flow

```
Client                          Backend
  │                                │
  │── POST /auth/register ────────►│
  │   { full_name, email, pwd }    │
  │                                │── bcrypt.hashpw(password)
  │                                │── INSERT INTO students
  │◄── { message, email } ────────│
  │                                │
  │── POST /auth/login ───────────►│
  │   { email, password }          │
  │                                │── SELECT student by email
  │                                │── bcrypt.checkpw(password)
  │                                │── jwt.encode({ student_id, email, exp })
  │◄── { token, user } ───────────│
  │                                │
  │── Store token in localStorage  │
  │                                │
  │── All future requests:         │
  │   Authorization: Bearer <token>│
  │                                │── verify_token() decodes JWT
  │                                │── extracts student_id
```

---

## 4. Chatbot Architecture

```
User Message
     │
     ▼
┌─────────────────────────────────────────┐
│           LangGraph ReAct Agent         │
│                                         │
│  1. Receives user message               │
│  2. Decides which tool to call          │
│  3. Calls tool → gets result            │
│  4. Forms response from tool result     │
│  5. Returns response to user            │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │    Tool Selection   │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────────┐
    ▼              ▼                  ▼
get_my_profile  get_my_education  get_my_applications
update_my_profile  add_my_education  apply_to_course
get_available_courses  update_application_status
add_course  get_course_by_id  delete_application
```

### Tool Binding Pattern
Each tool is wrapped inside `create_agent()` to bind the `student_id` from the JWT token, so the agent never needs to ask the user for their ID:

```python
def create_agent(student_id: int):
    def make_tools(sid: int):
        @tool
        def get_my_profile() -> str:
            return get_my_profile_tool.func(student_id=sid)
        ...
    tools = make_tools(student_id)
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
```

---

## 5. API Request Flow

### Example: Apply to a Course via Chatbot

```
User: "Enroll me in the DSA course"
        │
        ▼
POST /chatbot/chat
{ message: "Enroll me in the DSA course", chat_history: [...] }
        │
        ▼
verify_token() → extract student_id
        │
        ▼
create_agent(student_id)
        │
        ▼
Agent decides → call get_available_courses()
        │
        ▼
Tool queries SQLite → returns course list with IDs
        │
        ▼
Agent identifies DSA course ID
        │
        ▼
Agent calls apply_to_course(course_id=X)
        │
        ▼
Tool inserts into applications table
        │
        ▼
Agent returns: "You have been enrolled in DSA. Application ID: 3"
        │
        ▼
{ response: "...", success: true }
```

---

## 6. Frontend Component Structure

```
App.jsx
├── /              → AuthPage
│   ├── Login Form
│   └── Register Form (auto-login after register)
│
└── /dashboard     → DashboardPage (protected)
    ├── Sidebar Navigation
    │   ├── Overview Tab
    │   ├── Courses Tab
    │   └── Applications Tab
    ├── Overview Tab
    │   ├── Stats Row (enrolled, accepted, pending)
    │   ├── Profile Card (inline editable fields)
    │   ├── Education Card (progress bars)
    │   └── Recent Applications
    ├── Courses Tab
    │   └── Course Grid (apply button per course)
    ├── Applications Tab
    │   └── Application List (status badges)
    └── Chat Drawer (floating, triggered by "Ask AI" button)
        ├── Message History
        ├── Suggested Prompts
        └── Input Box
```

---

## 7. Security Design

| Concern | Solution |
|---------|----------|
| Password storage | bcrypt hashing with salt |
| Authentication | JWT tokens with 1 day expiry |
| Authorization | Every protected route calls `verify_token()` |
| Student isolation | All tools receive `student_id` from JWT, not from user input |
| SQL Injection | Parameterized queries throughout (`?` placeholders) |

---

## 8. Error Handling

| Layer | Strategy |
|-------|----------|
| FastAPI routes | try/except with HTTPException and rollback on DB errors |
| Chatbot | RateLimitError caught separately, returns 429 with friendly message |
| Frontend | All fetch calls wrapped in try/catch, errors shown in UI |
| JWT | ExpiredSignatureError and InvalidTokenError return 401 |