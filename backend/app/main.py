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
    """
    Accepts a message and optional file from the frontend, 
    runs it through the LangGraph agent, and returns the response.
    """
    try:
        # 1. Handle optional file uploads (Placeholder for future Vision LLM integration)
        file_context = ""
        if file:
            file_context = f"\n[System Note: The user attached a file named '{file.filename}'.]"
            # To actually read medical reports, you would process file.file.read() here 
            # with a vision model like Qwen2.5-VL before passing the text to Llama.

        # 2. Combine the user's message and file context
        full_prompt = message + file_context

        # 3. Format the input for LangGraph
        inputs = {"messages": [HumanMessage(content=full_prompt)]}
        
        # 4. Set configuration for memory tracking (Thread ID keeps the conversation context)
        config = {"configurable": {"thread_id": "patient_session_001"}}

        # 5. Execute the LangGraph workflow
        result = health_evaluator.invoke(inputs, config)

        # 6. Extract the final AI response from the state
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