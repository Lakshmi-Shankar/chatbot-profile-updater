from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
from databaseConnect import get_connection

router = APIRouter()


class CourseCreate(BaseModel):
    title: str
    duration_months: int
    fee: int
    
    @validator('duration_months')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
    @validator('fee')
    def validate_fee(cls, v):
        if v < 0:
            raise ValueError('Fee cannot be negative')
        return v


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    duration_months: Optional[int] = None
    fee: Optional[int] = None
    
    @validator('duration_months')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
    @validator('fee')
    def validate_fee(cls, v):
        if v is not None and v < 0:
            raise ValueError('Fee cannot be negative')
        return v


@router.get("/")
def get_courses():
    """Get all available courses"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        
        return [dict(course) for course in courses]
    
    finally:
        conn.close()


@router.get("/{course_id}")
def get_course(course_id: int):
    """Get a specific course by ID"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
        course = cursor.fetchone()
        
        if not course:
            raise HTTPException(404, "Course not found")
        
        return dict(course)
    
    finally:
        conn.close()


@router.post("/")
def create_course(data: CourseCreate):
    """Create a new course"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO courses (title, duration_months, fee)
            VALUES (?, ?, ?)
        """, (data.title, data.duration_months, data.fee))
        
        conn.commit()
        course_id = cursor.lastrowid
        
        return {
            "message": "Course created successfully",
            "course_id": course_id
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Failed to create course: {str(e)}")
    finally:
        conn.close()


@router.put("/{course_id}")
def update_course(course_id: int, data: CourseCreate):
    """Fully update a course (all fields required)"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE courses
            SET title=?, duration_months=?, fee=?
            WHERE id=?
        """, (data.title, data.duration_months, data.fee, course_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Course not found")
        
        conn.commit()
        return {"message": "Course updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()


@router.patch("/{course_id}")
def patch_course(course_id: int, data: CourseUpdate):
    """Partially update a course (only provided fields)"""
    
    update_data = data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(400, "No data provided for update")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic query
        fields = [f"{key}=?" for key in update_data.keys()]
        values = list(update_data.values())
        values.append(course_id)
        
        query = f"UPDATE courses SET {', '.join(fields)} WHERE id=?"
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Course not found")
        
        conn.commit()
        return {"message": "Course updated successfully", "updated_fields": list(update_data.keys())}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()


@router.delete("/{course_id}")
def delete_course(course_id: int):
    """Delete a course"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM courses WHERE id=?", (course_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Course not found")
        
        conn.commit()
        return {"message": "Course deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Delete failed: {str(e)}")
    finally:
        conn.close()