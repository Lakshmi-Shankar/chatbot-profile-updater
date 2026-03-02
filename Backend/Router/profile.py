from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from databaseConnect import get_connection
from authVerify import verify_token
from typing import Optional

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    city: Optional[str] = None


@router.get("/")
def get_profile(request: Request):
    """Get current user's profile with education details"""

    payload = verify_token(request)
    student_id = payload["student_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get student profile
        cursor.execute(
            "SELECT id, full_name, email, phone, date_of_birth, city FROM students WHERE id=?",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            raise HTTPException(404, "User not found")

        # Get education details
        cursor.execute(
            "SELECT * FROM education_details WHERE student_id=?",
            (student_id,)
        )
        education = cursor.fetchone()

        return {
            "student": dict(student),
            "education": dict(education) if education else None
        }

    finally:
        conn.close()


@router.patch("/")
def update_profile(request: Request, data: ProfileUpdate):
    """Update specific fields of user profile"""

    payload = verify_token(request)
    student_id = payload["student_id"]

    update_data = data.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No data provided for update")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Build dynamic update query
        fields = [f"{key}=?" for key in update_data.keys()]
        values = list(update_data.values())
        values.append(student_id)

        query = f"UPDATE students SET {', '.join(fields)} WHERE id=?"

        cursor.execute(query, values)

        if cursor.rowcount == 0:
            raise HTTPException(404, "User not found")

        conn.commit()

        return {"message": "Profile updated successfully", "updated_fields": list(update_data.keys())}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()