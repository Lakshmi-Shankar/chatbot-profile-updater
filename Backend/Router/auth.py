from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from databaseConnect import get_connection
import bcrypt
import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")

router = APIRouter()


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(user: UserRegister):
    """Register a new student account"""

    if len(user.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM students WHERE email=?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(409, "Email already registered")

        # Hash password and insert user
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO students (full_name, email, password) VALUES (?, ?, ?)",
            (user.full_name, user.email, hashed)
        )
        conn.commit()

        return {"message": "Registered successfully", "email": user.email}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Registration failed: {str(e)}")
    finally:
        conn.close()


@router.post("/login")
def login(user: UserLogin):
    """Login and receive JWT token"""

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM students WHERE email=?", (user.email,))
        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(401, "Invalid email or password")

        if not bcrypt.checkpw(user.password.encode(), db_user["password"]):
            raise HTTPException(401, "Invalid email or password")

        # Generate JWT token
        token = jwt.encode({
            "student_id": db_user["id"],
            "email": db_user["email"],
            "exp": datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY, algorithm="HS256")

        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": db_user["id"],
                "full_name": db_user["full_name"],
                "email": db_user["email"]
            }
        }

    finally:
        conn.close()