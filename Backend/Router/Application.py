from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
from databaseConnect import get_connection
from authVerify import verify_token

router = APIRouter()


class ApplicationCreate(BaseModel):
    course_id: int


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['submitted','under_review','accepted','rejected']
            if v.lower() not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v.lower() if v else v


@router.get("/")
def get_my_applications(request: Request):
    """Get all applications for current user"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT applications.*, courses.title, courses.duration_months, courses.fee
            FROM applications
            JOIN courses ON applications.course_id = courses.id
            WHERE student_id=?
        """, (student_id,))
        
        apps = cursor.fetchall()
        
        return [dict(app) for app in apps]
    
    finally:
        conn.close()


@router.post("/")
def apply_course(request: Request, data: ApplicationCreate):
    """Apply for a course"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if course exists
        cursor.execute("SELECT id FROM courses WHERE id=?", (data.course_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Course not found")
        
        # Check if already applied
        cursor.execute(
            "SELECT id FROM applications WHERE student_id=? AND course_id=?",
            (student_id, data.course_id)
        )
        if cursor.fetchone():
            raise HTTPException(409, "Already applied to this course")
        
        # Create application
        cursor.execute("""
            INSERT INTO applications (student_id, course_id, status)
            VALUES (?, ?, 'pending')
        """, (student_id, data.course_id))
        
        conn.commit()
        application_id = cursor.lastrowid
        
        return {
            "message": "Applied successfully",
            "application_id": application_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Application failed: {str(e)}")
    finally:
        conn.close()


@router.get("/{app_id}")
def get_application(request: Request, app_id: int):
    """Get specific application details"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT applications.*, courses.title, courses.duration_months, courses.fee
            FROM applications
            JOIN courses ON applications.course_id = courses.id
            WHERE applications.id=? AND applications.student_id=?
        """, (app_id, student_id))
        
        app = cursor.fetchone()
        
        if not app:
            raise HTTPException(404, "Application not found")
        
        return dict(app)
    
    finally:
        conn.close()


@router.patch("/{app_id}")
def patch_application(app_id: int, data: ApplicationUpdate):
    """Update application status (admin functionality)"""
    
    update_data = data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(400, "No data provided for update")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic query
        fields = [f"{key}=?" for key in update_data.keys()]
        values = list(update_data.values())
        values.append(app_id)
        
        query = f"UPDATE applications SET {', '.join(fields)} WHERE id=?"
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Application not found")
        
        conn.commit()
        return {"message": "Application updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()


@router.delete("/{app_id}")
def delete_application(request: Request, app_id: int):
    """Delete/cancel application"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM applications WHERE id=? AND student_id=?",
            (app_id, student_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Application not found")
        
        conn.commit()
        return {"message": "Application cancelled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Delete failed: {str(e)}")
    finally:
        conn.close()