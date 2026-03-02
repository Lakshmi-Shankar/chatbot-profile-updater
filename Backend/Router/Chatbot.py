from functools import lru_cache
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Optional
from groq import RateLimitError
from authVerify import verify_token
from Router.Tools import (
    get_my_profile_tool,
    update_my_profile_tool,
    get_my_education_tool,
    add_my_education_tool,
    update_my_education_tool,
    get_my_applications_tool,
    apply_to_course_tool,
    update_application_status_tool,
    delete_application_tool,
    get_available_courses_tool,
    get_course_by_id_tool,
    add_course_tool
)
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY_1"),
    temperature=0,
    max_tokens=1024
)


class ChatMessage(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = []


SYSTEM_PROMPT = """You are a helpful assistant for a course application system.

You have access to tools to help students manage their profile, education, applications, and courses.

STRICT RULES:
- ALWAYS call the appropriate tool first before responding. Never guess or assume data.
- NEVER fabricate data. If a tool returns no data, tell the user exactly that.
- After receiving a tool result, respond IMMEDIATELY to the user. Do NOT call another tool unless absolutely necessary.
- Never call the same tool twice in one request.
- Display ALL fields returned by the tool clearly in your response.
- If a tool returns an error or empty result, report it honestly to the user.
- NEVER guess a course ID. If the user refers to a course by name, always call get_available_courses first to find the correct course ID, then use that ID.
- If the user asks for multiple things (e.g. profile AND education), call each tool one by one and display ALL results together. Never skip a tool call.
- Never respond with "here are your details" without actually calling the tools first.

CAPABILITIES:
- Profile: view and update (name, phone, date of birth, city)
- Education: view, add, or update 10th and 12th board details
- Applications: view, apply, update status, or cancel
- If the user asks a general question about what fields exist or what data is available, answer directly from your knowledge. Do NOT call any tool for general questions.
- Courses: view all courses or a specific course by ID"""


# def create_agent(student_id: int):

#     @tool
#     def get_my_profile() -> str:
#         """Get the student's profile: name, email, phone, date of birth, city."""
#         return get_my_profile_tool.func(student_id=student_id)

#     @tool
#     def update_my_profile(full_name: str = None, phone: str = None, date_of_birth: str = None, city: str = None) -> str:
#         """Update the student's profile fields. date_of_birth must be YYYY-MM-DD format. Only pass fields to change."""
#         return update_my_profile_tool.func(
#             student_id=student_id,
#             full_name=full_name,
#             phone=phone,
#             date_of_birth=date_of_birth,
#             city=city
#         )

#     @tool
#     def get_my_education() -> str:
#         """Get the student's education details: 10th and 12th board and percentage."""
#         return get_my_education_tool.func(student_id=student_id)

#     @tool
#     def add_my_education(tenth_board: str, tenth_percentage: float, twelfth_board: str, twelfth_percentage: float) -> str:
#         """Add education details. Use ONLY if student has no education details yet."""
#         return add_my_education_tool.func(
#             student_id=student_id,
#             tenth_board=tenth_board,
#             tenth_percentage=tenth_percentage,
#             twelfth_board=twelfth_board,
#             twelfth_percentage=twelfth_percentage
#         )

#     @tool
#     def update_my_education(tenth_board: str = None, tenth_percentage: float = None,
#                              twelfth_board: str = None, twelfth_percentage: float = None) -> str:
#         """Update existing education details. Only pass fields to change."""
#         return update_my_education_tool.func(
#             student_id=student_id,
#             tenth_board=tenth_board,
#             tenth_percentage=tenth_percentage,
#             twelfth_board=twelfth_board,
#             twelfth_percentage=twelfth_percentage
#         )

#     @tool
#     def get_my_applications() -> str:
#         """Get all of the student's course applications with status and details."""
#         return get_my_applications_tool.func(student_id=student_id)

#     @tool
#     def apply_to_course(course_id: int) -> str:
#         """Apply to a course using its course ID."""
#         return apply_to_course_tool.func(course_id=course_id, student_id=student_id)
    
#     @tool
#     def add_course_tool(title: str, duration_months: int, fee: int) -> str:
#         """Add a new course with title, duration in months, and fee amount."""
#         return add_course_tool.func(title=title, duration_months=duration_months, fee=fee)

#     @tool
#     def update_application_status(application_id: int, new_status: str) -> str:
#         """Update application status. new_status must be one of: submitted, under_review, accepted, rejected."""
#         return update_application_status_tool.func(
#             application_id=application_id,
#             new_status=new_status,
#             student_id=student_id
#         )

#     @tool
#     def delete_application(application_id: int) -> str:
#         """Permanently cancel and delete an application by its ID."""
#         return delete_application_tool.func(application_id=application_id, student_id=student_id)

#     @tool  # ← THIS WAS THE BUG - now wrapped consistently like all other tools
#     def get_available_courses() -> str:
#         """Get all available courses with their ID, title, duration, and fee."""
#         return get_available_courses_tool.func()

#     @tool
#     def get_course_by_id(course_id: int) -> str:
#         """Get details of a specific course by its numeric ID only. 
#         If you only have the course name, call get_available_courses first to find the ID."""
#         return get_course_by_id_tool.func(course_id=course_id)

#     tools = [
#         get_my_profile,
#         update_my_profile,
#         get_my_education,
#         add_my_education,
#         update_my_education,
#         get_my_applications,
#         apply_to_course,
#         update_application_status,
#         delete_application,
#         get_available_courses,  # ← now using the local wrapper
#         get_course_by_id,
#         add_course_tool
#     ]

#     return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

def create_agent(student_id: int):

    def make_tools(sid: int):
        @tool
        def get_my_profile() -> str:
            """Get the student's profile: name, email, phone, date of birth, city."""
            return get_my_profile_tool.func(student_id=sid)

        @tool
        def update_my_profile(full_name: str = None, phone: str = None, date_of_birth: str = None, city: str = None) -> str:
            """Update the student's profile fields. date_of_birth must be YYYY-MM-DD. Only pass fields to change."""
            return update_my_profile_tool.func(student_id=sid, full_name=full_name, phone=phone, date_of_birth=date_of_birth, city=city)

        @tool
        def get_my_education() -> str:
            """Get the student's education details: 10th and 12th board and percentage."""
            return get_my_education_tool.func(student_id=sid)

        @tool
        def add_my_education(tenth_board: str, tenth_percentage: float, twelfth_board: str, twelfth_percentage: float) -> str:
            """Add education details. Use ONLY if student has no education details yet."""
            return add_my_education_tool.func(student_id=sid, tenth_board=tenth_board, tenth_percentage=tenth_percentage, twelfth_board=twelfth_board, twelfth_percentage=twelfth_percentage)

        @tool
        def update_my_education(tenth_board: str = None, tenth_percentage: float = None,
                                 twelfth_board: str = None, twelfth_percentage: float = None) -> str:
            """Update existing education details. Only pass fields to change."""
            return update_my_education_tool.func(student_id=sid, tenth_board=tenth_board, tenth_percentage=tenth_percentage, twelfth_board=twelfth_board, twelfth_percentage=twelfth_percentage)

        @tool
        def get_my_applications() -> str:
            """Get all of the student's course applications with status and details."""
            return get_my_applications_tool.func(student_id=sid)

        @tool
        def apply_to_course(course_id: int) -> str:
            """Apply to a course using its numeric course ID."""
            return apply_to_course_tool.func(course_id=course_id, student_id=sid)
        @tool
        def update_application_status(application_id: int, new_status: str) -> str:
            """Update an application's status. Must be one of: submitted, under_review, accepted, rejected.
            IMPORTANT: application_id must be a numeric ID only. If you don't know the ID, call get_my_applications first to find it."""
            return update_application_status_tool.func( application_id=application_id, new_status=new_status, student_id=student_id )

        @tool
        def delete_application(application_id: int) -> str:
            """Permanently cancel and delete an application by its ID."""
            return delete_application_tool.func(application_id=application_id, student_id=sid)

        @tool
        def get_available_courses() -> str:
            """Get all available courses with their ID, title, duration, and fee."""
            return get_available_courses_tool.func()

        @tool
        def add_course(title: str, duration_months: int, fee: int) -> str:
            """Add a new course with title, duration in months, and fee amount."""
            return add_course_tool.func(title=title, duration_months=duration_months, fee=fee)

        @tool
        def get_course_by_id(course_id: int) -> str:
            """Get details of a specific course by its numeric ID only. 
            If you only have the course name, call get_available_courses first to find the ID."""
            return get_course_by_id_tool.func(course_id=course_id)

        return [
            get_my_profile, update_my_profile,
            get_my_education, add_my_education, update_my_education,
            get_my_applications, apply_to_course, update_application_status, delete_application,
            get_available_courses, add_course, get_course_by_id,
        ]

    tools = make_tools(student_id)
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

@router.post("/chat")
def chat(request: Request, data: ChatMessage):
    payload = verify_token(request)
    student_id = payload["student_id"]

    try:
        agent = create_agent(student_id)

        recent_history = data.chat_history[-6:] if len(data.chat_history) > 6 else data.chat_history

        messages = []
        for msg in recent_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=data.message))

        response = agent.invoke(
            {"messages": messages},
            config={"recursion_limit": 50}
        )

        for msg in response["messages"]:
            print(type(msg).__name__, ":", msg.content[:150] if msg.content else "[no content]")

        ai_message = response["messages"][-1].content

        return {
            "response": ai_message,
            "success": True
        }
    except RateLimitError as e:
        raise HTTPException(429, "You've reached the AI usage limit. Please wait a few minutes and try again.")

    except Exception as e:
        raise HTTPException(500, f"Chat failed: {str(e)}")