from langchain_core.tools import tool
from typing import Optional
from databaseConnect import get_connection


# ============================================================
# PROFILE TOOLS
# ============================================================

@tool
def get_my_profile_tool(student_id: int) -> str:
    """Get the student's profile information including name, email, phone, date of birth, and city."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT full_name, email, phone, date_of_birth, city FROM students WHERE id=?",
            (student_id,)
        )
        student = cursor.fetchone()
        if not student:
            return "Profile not found."
        result = "Your Profile:\n"
        result += f"Name: {student['full_name']}\n"
        result += f"Email: {student['email']}\n"
        result += f"Phone: {student['phone'] or 'Not set'}\n"
        result += f"Date of Birth: {student['date_of_birth'] or 'Not set'}\n"
        result += f"City: {student['city'] or 'Not set'}\n"
        return result
    finally:
        conn.close()


@tool
def update_my_profile_tool(student_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, date_of_birth: Optional[str] = None, city: Optional[str] = None) -> str:
    """Update the student's profile. You can update full_name, phone, date_of_birth (YYYY-MM-DD format), and/or city.
    Only provide the fields you want to update."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        fields = []
        values = []
        if full_name is not None:
            fields.append("full_name=?")
            values.append(full_name)
        if phone is not None:
            fields.append("phone=?")
            values.append(phone)
        if date_of_birth is not None:
            fields.append("date_of_birth=?")
            values.append(date_of_birth)
        if city is not None:
            fields.append("city=?")
            values.append(city)

        if not fields:
            return "No fields provided to update. Please specify phone, date_of_birth, or city."

        values.append(student_id)
        cursor.execute(
            f"UPDATE students SET {', '.join(fields)} WHERE id=?",
            values
        )
        conn.commit()
        updated = ", ".join([f.split("=")[0] for f in fields])
        return f"Successfully updated profile fields: {updated}."
    except Exception as e:
        conn.rollback()
        return f"Failed to update profile: {str(e)}"
    finally:
        conn.close()


# ============================================================
# EDUCATION TOOLS
# ============================================================

@tool
def get_my_education_tool(student_id: int) -> str:
    """Get the student's education details including 10th and 12th board and percentage."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM education_details WHERE student_id=?",
            (student_id,)
        )
        education = cursor.fetchone()
        if not education:
            return "No education details found. You can add them."
        result = "Your Education Details:\n"
        result += f"10th Board: {education['tenth_board']}\n"
        result += f"10th Percentage: {education['tenth_percentage']}%\n"
        result += f"12th Board: {education['twelfth_board']}\n"
        result += f"12th Percentage: {education['twelfth_percentage']}%\n"
        return result
    finally:
        conn.close()


@tool
def add_my_education_tool(student_id: int, tenth_board: str, tenth_percentage: float,
                           twelfth_board: str, twelfth_percentage: float) -> str:
    """Add education details for the student. Requires 10th and 12th board name and percentage.
    Use this only if the student has no education details yet."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM education_details WHERE student_id=?",
            (student_id,)
        )
        if cursor.fetchone():
            return "Education details already exist. Use the update tool to modify them."
        cursor.execute("""
            INSERT INTO education_details (student_id, tenth_board, tenth_percentage, twelfth_board, twelfth_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, tenth_board, tenth_percentage, twelfth_board, twelfth_percentage))
        conn.commit()
        return "Education details added successfully."
    except Exception as e:
        conn.rollback()
        return f"Failed to add education details: {str(e)}"
    finally:
        conn.close()


@tool
def update_my_education_tool(student_id: int, tenth_board: str = None, tenth_percentage: float = None,
                              twelfth_board: str = None, twelfth_percentage: float = None) -> str:
    """Update the student's education details. Only provide the fields you want to update."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM education_details WHERE student_id=?",
            (student_id,)
        )
        if not cursor.fetchone():
            return "No education details found. Please add them first."

        fields = []
        values = []
        if tenth_board is not None:
            fields.append("tenth_board=?")
            values.append(tenth_board)
        if tenth_percentage is not None:
            fields.append("tenth_percentage=?")
            values.append(tenth_percentage)
        if twelfth_board is not None:
            fields.append("twelfth_board=?")
            values.append(twelfth_board)
        if twelfth_percentage is not None:
            fields.append("twelfth_percentage=?")
            values.append(twelfth_percentage)

        if not fields:
            return "No fields provided to update."

        values.append(student_id)
        cursor.execute(
            f"UPDATE education_details SET {', '.join(fields)} WHERE student_id=?",
            values
        )
        conn.commit()
        updated = ", ".join([f.split("=")[0] for f in fields])
        return f"Successfully updated education fields: {updated}."
    except Exception as e:
        conn.rollback()
        return f"Failed to update education details: {str(e)}"
    finally:
        conn.close()


# ============================================================
# APPLICATION TOOLS
# ============================================================

@tool
def get_my_applications_tool(student_id: int) -> str:
    """Get all applications for the current student including status, course info, and application ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT applications.id, applications.status, applications.applied_at,
                   courses.title, courses.duration_months, courses.fee
            FROM applications
            JOIN courses ON applications.course_id = courses.id
            WHERE student_id=?
        """, (student_id,))
        apps = cursor.fetchall()
        if not apps:
            return "You have no applications yet."
        result = "Your applications:\n"
        for app in apps:
            result += f"\n- Application ID: {app['id']}\n"
            result += f"  Course: {app['title']}\n"
            result += f"  Status: {app['status']}\n"
            result += f"  Duration: {app['duration_months']} months\n"
            result += f"  Fee: ${app['fee']}\n"
            result += f"  Applied: {app['applied_at']}\n"
        return result
    finally:
        conn.close()


@tool
def apply_to_course_tool(course_id: int, student_id: int) -> str:
    """Apply to a course by course ID. Creates a new application with status 'submitted'."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title FROM courses WHERE id=?", (course_id,))
        course = cursor.fetchone()
        if not course:
            return f"Course {course_id} not found."
        cursor.execute(
            "SELECT id FROM applications WHERE student_id=? AND course_id=?",
            (student_id, course_id)
        )
        if cursor.fetchone():
            return f"You have already applied to '{course['title']}'."
        cursor.execute(
            "INSERT INTO applications (student_id, course_id, status) VALUES (?, ?, 'submitted')",
            (student_id, course_id)
        )
        conn.commit()
        return f"Successfully applied to '{course['title']}'. Your application ID is {cursor.lastrowid}."
    except Exception as e:
        conn.rollback()
        return f"Failed to apply: {str(e)}"
    finally:
        conn.close()


@tool
def update_application_status_tool(application_id: int, new_status: str, student_id: int) -> str:
    """Update an application's status. Status must be one of: submitted, under_review, accepted, rejected."""
    allowed_statuses = ['submitted', 'under_review', 'accepted', 'rejected']
    new_status = new_status.lower()
    if new_status not in allowed_statuses:
        return f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM applications WHERE id=? AND student_id=?",
            (application_id, student_id)
        )
        if not cursor.fetchone():
            return f"Application {application_id} not found or doesn't belong to you."
        cursor.execute(
            "UPDATE applications SET status=? WHERE id=?",
            (new_status, application_id)
        )
        conn.commit()
        return f"Successfully updated application {application_id} status to '{new_status}'."
    except Exception as e:
        conn.rollback()
        return f"Failed to update application: {str(e)}"
    finally:
        conn.close()


@tool
def delete_application_tool(application_id: int, student_id: int) -> str:
    """Delete/cancel an application. Only deletes applications belonging to the current student."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM applications WHERE id=? AND student_id=?",
            (application_id, student_id)
        )
        if cursor.rowcount == 0:
            return f"Application {application_id} not found or doesn't belong to you."
        conn.commit()
        return f"Successfully cancelled application {application_id}."
    except Exception as e:
        conn.rollback()
        return f"Failed to delete application: {str(e)}"
    finally:
        conn.close()


# ============================================================
# COURSE TOOLS
# ============================================================

@tool
def get_available_courses_tool() -> str:
    """Get list of all available courses with their ID, title, duration, and fee."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, duration_months, fee FROM courses")
        courses = cursor.fetchall()
        if not courses:
            return "No courses available at the moment."
        result = "Available courses:\n"
        for course in courses:
            result += f"\n- Course ID: {course['id']}\n"
            result += f"  Title: {course['title']}\n"
            result += f"  Duration: {course['duration_months']} months\n"
            result += f"  Fee: ${course['fee']}\n"
        return result
    finally:
        conn.close()


@tool
def get_course_by_id_tool(course_id: int) -> str:
    """Get details of a specific course by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, title, duration_months, fee FROM courses WHERE id=?",
            (course_id,)
        )
        course = cursor.fetchone()
        if not course:
            return f"Course {course_id} not found."
        result = f"Course Details:\n"
        result += f"ID: {course['id']}\n"
        result += f"Title: {course['title']}\n"
        result += f"Duration: {course['duration_months']} months\n"
        result += f"Fee: ${course['fee']}\n"
        return result
    finally:
        conn.close()

@tool
def add_course_tool(title: str, duration_months: int, fee: int) -> str:
    """Add a new course. Requires title, duration_months, and fee."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO courses (title, duration_months, fee) VALUES (?, ?, ?)",
            (title, duration_months, fee)
        )
        conn.commit()
        return f"Course '{title}' added successfully with ID {cursor.lastrowid}."
    except Exception as e:
        conn.rollback()
        return f"Failed to add course: {str(e)}"
    finally:
        conn.close()