from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from app.utils.hf_client import get_nutrition_specialist_llm

@tool
def generate_diet_plan(condition: str, restrictions: str = "None") -> str:
    """ALWAYS use this tool when a user asks for a diet, meal plan, or nutritional advice."""
    try:
        nutrition_llm = get_nutrition_specialist_llm()
        dietitian_prompt = f"""You are an expert Clinical Registered Dietitian. 
        A patient requires dietary intervention for the following condition: {condition}
        Their dietary restrictions/allergies are: {restrictions}
        Provide: 1. Diet name. 2. Foods to focus on/avoid. 3. Simple 1-day meal plan. Format with bullet points."""
        
        response = nutrition_llm.invoke([HumanMessage(content=dietitian_prompt)])
        return f"Clinical Dietitian AI Recommendations:\n{response.content}"
    except Exception as e:
        return "System Note: The specialized nutrition model is currently unavailable."