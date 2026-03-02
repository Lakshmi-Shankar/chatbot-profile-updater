from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
from databaseConnect import get_connection
from authVerify import verify_token

router = APIRouter()


# Models
class EducationCreate(BaseModel):
    tenth_board: str
    tenth_percentage: int
    twelfth_board: str
    twelfth_percentage: int
    
    @validator('tenth_percentage', 'twelfth_percentage')
    def validate_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v


class EducationUpdate(BaseModel):
    tenth_board: Optional[str] = None
    tenth_percentage: Optional[int] = None
    twelfth_board: Optional[str] = None
    twelfth_percentage: Optional[int] = None
    
    @validator('tenth_percentage', 'twelfth_percentage')
    def validate_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentage must be between 0 and 100')
        return v


# GET education
@router.get("/")
def get_education(request: Request):
    """Get current user's education details"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM education_details WHERE student_id=?",
            (student_id,)
        )
        education = cursor.fetchone()
        
        if not education:
            raise HTTPException(404, "Education details not found")
        
        return dict(education)
    
    finally:
        conn.close()


# POST education (create)
@router.post("/")
def create_education(request: Request, data: EducationCreate):
    """Create education details for current user"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if education already exists
        cursor.execute(
            "SELECT id FROM education_details WHERE student_id=?",
            (student_id,)
        )
        if cursor.fetchone():
            raise HTTPException(409, "Education details already exist. Use PUT or PATCH to update.")
        
        cursor.execute("""
            INSERT INTO education_details
            (student_id, tenth_board, tenth_percentage, twelfth_board, twelfth_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            data.tenth_board,
            data.tenth_percentage,
            data.twelfth_board,
            data.twelfth_percentage
        ))
        
        conn.commit()
        return {"message": "Education details created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Failed to create education details: {str(e)}")
    finally:
        conn.close()


# PUT education (full update)
@router.put("/")
def update_education(request: Request, data: EducationCreate):
    """Fully update education details (all fields required)"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE education_details
            SET tenth_board=?, tenth_percentage=?, twelfth_board=?, twelfth_percentage=?
            WHERE student_id=?
        """, (
            data.tenth_board,
            data.tenth_percentage,
            data.twelfth_board,
            data.twelfth_percentage,
            student_id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Education details not found. Use POST to create.")
        
        conn.commit()
        return {"message": "Education details updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()


# PATCH education
@router.patch("/")
def patch_education(request: Request, data: EducationUpdate):
    """Partially update education details (only provided fields)"""
    
    payload = verify_token(request)
    student_id = payload["student_id"]
    
    update_data = data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(400, "No data provided for update")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic query
        fields = [f"{key}=?" for key in update_data.keys()]
        values = list(update_data.values())
        values.append(student_id)
        
        query = f"UPDATE education_details SET {', '.join(fields)} WHERE student_id=?"
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "Education details not found")
        
        conn.commit()
        return {"message": "Education details updated successfully", "updated_fields": list(update_data.keys())}
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Update failed: {str(e)}")
    finally:
        conn.close()