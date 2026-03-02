from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from Router import auth, profile, Education, Courses, Application, Chatbot

app = FastAPI()

origins = [
    "http://localhost:5173",  # your frontend URL (React dev server)
    "http://127.0.0.1:5173",  # optional
    # add more origins if needed, e.g., deployed frontend URLs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # which origins can access
    allow_credentials=True,      # allow cookies, auth headers
    allow_methods=["*"],         # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],         # which headers are allowed
)

@app.get("/healthCheck")
def health():
    return {"message": "Server running"}

# include routes with proper prefixes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(Education.router, prefix="/education", tags=["Education"])
app.include_router(Courses.router, prefix="/courses", tags=["Courses"])
app.include_router(Application.router, prefix="/application", tags=["Application"])
app.include_router(Chatbot.router, prefix="/chatbot", tags=["Chatbot"])


if __name__ == "__main__":
    uvicorn.run(app, port=8000)