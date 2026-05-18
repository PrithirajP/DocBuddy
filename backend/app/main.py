from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

# Import your compiled LangGraph workflow
from app.agent.graph import health_evaluator

app = FastAPI(title="AI Health Evaluator API")

# Configure CORS so the React frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (update this in production to your React port, e.g., "http://localhost:5173")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        file_context = ""
        if file:
            file_context = f"\n[System Note: The user attached a file named '{file.filename}'.]"

        full_prompt = message + file_context
        inputs = {"messages": [HumanMessage(content=full_prompt)]}
        
        # Using a static thread_id for now. 
        # In the future, this would be the actual Patient's ID from your frontend.
        config = {"configurable": {"thread_id": "patient_session_001"}}

        # UPGRADE: Changed .invoke() to .ainvoke() for asynchronous, non-blocking execution
        result = await health_evaluator.ainvoke(inputs, config)
        
        final_message = result["messages"][-1].content

        return {"reply": final_message}

    except Exception as e:
        print(f"Error during graph execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Health check route
@app.get("/")
def read_root():
    return {"status": "AI Health Evaluator Backend is Running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)