import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("app.main.health_evaluator.ainvoke", new_callable=AsyncMock)
def test_chat_endpoint_no_file(mock_ainvoke):
    # Mock the return value of the graph
    mock_ainvoke.return_value = {
        "messages": [
            type('obj', (object,), {'content': 'This is a mock response from LangGraph.'})()
        ]
    }
    
    response = client.post(
        "/api/chat",
        data={"message": "I have a headache", "thread_id": "1234"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"reply": "This is a mock response from LangGraph."}
    mock_ainvoke.assert_called_once()
