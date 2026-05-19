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
    thread_id: str = Form(...), # <-- NEW: The server now expects a chat ID
    file: UploadFile = File(None)
):
    try:
        file_context = ""
        if file:
            file_context = f"\n[System Note: The user attached a file named '{file.filename}'.]"

        full_prompt = message + file_context
        inputs = {"messages": [HumanMessage(content=full_prompt)]}
        
        # We pass the dynamic thread_id from the frontend to isolate this specific chat
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the graph asynchronously (Memory is handled automatically by graph.py now!)
        result = await health_evaluator.ainvoke(inputs, config)
        
        final_message = result["messages"][-1].content

        return {"reply": final_message}

    except Exception as e:
        print(f"Error during graph execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))