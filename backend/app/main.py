import os
from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import shutil
from app.agent.graph import health_evaluator

load_dotenv()

app = FastAPI(title="DocBuddy AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    thread_id: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        user_input = message
        
        if file:
            file_path = f"uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            user_input += f"\n\n[Attached File: {file.filename} saved at {file_path}]"
            
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke LangGraph
        result = await health_evaluator.ainvoke({"messages": [("user", user_input)]}, config)
        
        # Extract the last message from the agent
        final_message = result["messages"][-1].content
        
        return {"reply": final_message}
        
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