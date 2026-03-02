from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3

from Router import auth, profile, Education, Courses, Application, Chatbot

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            date_of_birth TEXT,
            city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS education_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            tenth_board TEXT,
            tenth_percentage INTEGER,
            twelfth_board TEXT,
            twelfth_percentage INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            duration_months INTEGER,
            fee INTEGER
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            status TEXT CHECK(
                status IN ('submitted','under_review','accepted','rejected','pending')
            ) NOT NULL DEFAULT 'submitted',
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)
    conn.commit()
    conn.close()

# Run before app starts
init_db()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://chatbot-profile-updater.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthCheck")
def health():
    return {"message": "Server running"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(Education.router, prefix="/education", tags=["Education"])
app.include_router(Courses.router, prefix="/courses", tags=["Courses"])
app.include_router(Application.router, prefix="/application", tags=["Application"])
app.include_router(Chatbot.router, prefix="/chatbot", tags=["Chatbot"])

if __name__ == "__main__":
    uvicorn.run(app, port=8000)