from langchain_core.tools import tool
from app.utils.hf_client import get_medical_specialist_llm

@tool
def analyze_symptoms_for_disease(symptoms: str, patient_context: str = "None") -> str:
    """ALWAYS use this tool when a user describes symptoms."""
    try:
        medical_llm = get_medical_specialist_llm()
        clinical_prompt = f"""You are an expert clinical diagnostic AI. 
        Analyze the following symptoms and provide the top 3 most likely differential diagnoses.
        Provide a brief rationale for each based on the symptoms.
        Suggest the level of urgency for seeking physical medical care.
        
        Patient Symptoms: {symptoms}
        Additional Context: {patient_context}
        
        Format the output clearly with bullet points."""
        
        response = medical_llm.invoke(clinical_prompt)
        return f"Specialist Medical AI Findings:\n{response}"
    except Exception as e:
        print(f"\n--- MEDICAL AI ERROR ---\n{e}\n------------------------\n")
        return "System Note: The specialized medical analysis model is currently unavailable."