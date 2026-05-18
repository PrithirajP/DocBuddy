from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class PatientState(TypedDict):
    # add_messages ensures that new messages are appended to the list, not overwritten
    messages: Annotated[list, add_messages]