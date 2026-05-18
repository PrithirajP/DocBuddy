from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from app.utils.hf_client import get_medical_specialist_llm, get_nutrition_specialist_llm

# --- MOCK DATABASES ---
MOCK_DRUG_DB = {
    ("ibuprofen", "lisinopril"): "Warning: Can decrease blood pressure control and strain kidneys.",
    ("metformin", "lisinopril"): "Safe: No known adverse interactions.",
    ("warfarin", "aspirin"): "SEVERE WARNING: High risk of internal bleeding. Immediate medical consultation required.",
}

MOCK_DOCTOR_DB = [
    {"name": "Dr. Sarah Adams", "specialty": "cardiologist", "location": "seattle", "rating": 4.9},
    {"name": "Dr. Rajesh Sharma", "specialty": "endocrinologist", "location": "seattle", "rating": 4.8},
    {"name": "Dr. Emily Lee", "specialty": "general practice", "location": "portland", "rating": 4.7},
]

# --- UPGRADED DIAGNOSTIC TOOL ---
@tool
def analyze_symptoms_for_disease(symptoms: str, patient_context: str = "None") -> str:
    """
    ALWAYS use this tool when a user describes symptoms. 
    It routes the symptoms to a highly specialized medical AI to map symptoms to potential diseases.
    """
    try:
        # 1. Initialize the specialist model
        medical_llm = get_medical_specialist_llm()
        
        # 2. Craft a strict, clinical prompt for the specialist
        clinical_prompt = f"""You are an expert clinical diagnostic AI. 
        Analyze the following symptoms and provide the top 3 most likely differential diagnoses.
        Provide a brief rationale for each based on the symptoms.
        Suggest the level of urgency for seeking physical medical care.
        
        Patient Symptoms: {symptoms}
        Additional Context: {patient_context}
        
        Format the output clearly with bullet points.
        """
        
        # 3. Ask the specialist LLM
        response = medical_llm.invoke([HumanMessage(content=clinical_prompt)])
        
        # 4. Return the specialist's findings back to the main LangGraph agent
        return f"Specialist Medical AI Findings:\n{response.content}"
        
    except Exception as e:
        return "System Note: The specialized medical analysis model is currently unavailable or overloaded. Please advise the user to consult a doctor."

# --- EXISTING TOOLS ---
@tool
def search_doctors(location: str, specialty: str) -> str:
    """Finds recommended doctors nearby based on location and specialty."""
    loc = location.lower()
    spec = specialty.lower()
    matches = [doc for doc in MOCK_DOCTOR_DB if doc["location"] == loc and spec in doc["specialty"]]
    
    if not matches:
        return f"I couldn't find any highly-rated {specialty}s currently available in {location}."
        
    results = "\n".join([f"- {doc['name']} ({doc['specialty'].title()}) - Rating: {doc['rating']}/5" for doc in matches])
    return f"Here are the top-rated specialists I found in {location}:\n{results}"

@tool
def check_drug_interactions(medication_1: str, medication_2: str) -> str:
    """Checks for adverse drug-drug interactions between two specific medications."""
    meds = tuple(sorted([medication_1.lower(), medication_2.lower()]))
    if meds in MOCK_DRUG_DB:
        return MOCK_DRUG_DB[meds]
    return f"No severe interactions documented in the database between {medication_1} and {medication_2}."

@tool
def generate_diet_plan(condition: str, restrictions: str = "None") -> str:
    """
    ALWAYS use this tool when a user asks for a diet, meal plan, or nutritional advice.
    It routes the condition to a specialized Dietitian AI to generate a custom medical diet.
    """
    try:
        # 1. Initialize the Dietitian Model
        nutrition_llm = get_nutrition_specialist_llm()
        
        # 2. Craft the strict Dietitian Prompt
        dietitian_prompt = f"""You are an expert Clinical Registered Dietitian. 
        A patient requires dietary intervention for the following condition: {condition}
        Their dietary restrictions/allergies are: {restrictions}
        
        Provide the following:
        1. The name of the recommended clinical diet (e.g., DASH, Low-FODMAP).
        2. A brief list of "Foods to Focus On" and "Foods to Strictly Avoid".
        3. A simple, 1-day sample meal plan (Breakfast, Lunch, Dinner).
        
        Keep it highly clinical, safe, and format it beautifully with bullet points.
        """
        
        # 3. Ask the Dietitian LLM
        response = nutrition_llm.invoke([HumanMessage(content=dietitian_prompt)])
        
        # 4. Return the findings back to DocBuddy
        return f"Clinical Dietitian AI Recommendations:\n{response.content}"
        
    except Exception as e:
        return "System Note: The specialized nutrition model is currently unavailable. Recommend a doctor or dietician."

evaluator_tools = [analyze_symptoms_for_disease, search_doctors, check_drug_interactions, generate_diet_plan]