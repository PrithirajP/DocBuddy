import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DocBuddy AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatMessage(BaseModel):
    message: str

@app.get("/api/health")
def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "healthy", "service": "DocBuddy API"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    """
    PASTE YOUR LANGGRAPH INVOCATION HERE
    """
    try:
        user_input = request.message
        
        return {"response": f"Message received: {user_input}"} # Replace this line
        
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

os.makedirs("uploads", exist_ok=True)

frontend_build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(frontend_build_path):
    print("Frontend build found. Serving React app...")
    
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build_path, "index.html"))
else:
    print("======================================================")
    print("WARNING: Frontend build not found.")
    print("API is running, but UI will not load. Ensure you ran `npm run build`.")
    print("======================================================")