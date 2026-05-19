import os
import sqlite3
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

# Import your compiled LangGraph workflow
from app.agent.graph import health_evaluator

app = FastAPI(title="DocBuddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    thread_id: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        file_context = ""
        if file:
            # Create a temporary folder to hold uploads for the Vision AI
            os.makedirs("uploads", exist_ok=True)
            file_path = f"uploads/{file.filename}"
            
            # Save the physical file to the disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Tell the Orchestrator EXACTLY where the file is!
            file_context = f"\n\n[System Note: The user attached an image saved at '{file_path}'. You MUST use the 'analyze_medical_image' tool to look at it!]"

        full_prompt = message + file_context
        inputs = {"messages": [HumanMessage(content=full_prompt)]}
        
        # Isolate this specific chat session using the frontend's thread_id
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the graph asynchronously
        result = await health_evaluator.ainvoke(inputs, config)
        
        final_message = result["messages"][-1].content

        return {"reply": final_message}

    except Exception as e:
        print(f"Error during graph execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))