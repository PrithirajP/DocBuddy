import requests
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# Import the specialized LLM connections from our client file
from app.utils.hf_client import get_medical_specialist_llm, get_nutrition_specialist_llm

# ==========================================
# HELPER FUNCTIONS (For APIs)
# ==========================================

def get_rxcui(drug_name: str) -> str:
    """Fetches the NIH RxCUI ID for a given drug."""
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if "idGroup" in data and "rxnormId" in data["idGroup"]:
            return data["idGroup"]["rxnormId"][0]
    except Exception as e:
        print(f"Error fetching RxCUI for {drug_name}: {e}")
    return None

def get_fda_drug_info(drug_name: str) -> str:
    """Fetches general indications and warnings directly from the OpenFDA API."""
    url = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{drug_name}"+openfda.brand_name:"{drug_name}"&limit=1'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()["results"][0]
            
            # Extract and truncate the data so we don't overwhelm the LLM's context window
            indications = data.get("indications_and_usage", ["No specific indications found."])[0][:600]
            warnings = data.get("warnings", ["No general warnings found."])[0][:600]
            adverse = data.get("adverse_reactions", ["No adverse reactions listed."])[0][:600]
            
            return f"""FDA Clinical Data for {drug_name.upper()}:
            - INDICATIONS: {indications}...
            - WARNINGS: {warnings}...
            - ADVERSE REACTIONS: {adverse}..."""
    except Exception:
        pass
    
    return f"Could not retrieve specific FDA database info for {drug_name}. Please rely on your general clinical knowledge."

# ==========================================
# THE AGENT TOOLS
# ==========================================

@tool
def analyze_symptoms_for_disease(symptoms: str, patient_context: str = "None") -> str:
    """
    ALWAYS use this tool when a user describes symptoms. 
    It routes the symptoms to a highly specialized medical AI to map symptoms to potential diseases.
    """
    try:
        medical_llm = get_medical_specialist_llm()
        
        clinical_prompt = f"""You are an expert clinical diagnostic AI. 
        Analyze the following symptoms and provide the top 3 most likely differential diagnoses.
        Provide a brief rationale for each based on the symptoms.
        Suggest the level of urgency for seeking physical medical care.
        
        Patient Symptoms: {symptoms}
        Additional Context: {patient_context}
        
        Format the output clearly with bullet points.
        """
        
        response = medical_llm.invoke([HumanMessage(content=clinical_prompt)])
        return f"Specialist Medical AI Findings:\n{response.content}"
        
    except Exception as e:
        return "System Note: The specialized medical analysis model is currently unavailable. Please advise the user to consult a doctor."

@tool
def search_doctors(city: str, specialty: str) -> str:
    """
    Finds hospitals, clinics, and medical specialists globally.
    Connects to the OpenStreetMap (Nominatim) public database.
    """
    # OpenStreetMap requires a User-Agent header for their free API
    headers = {
        "User-Agent": "DocBuddy-HealthApp/1.0"
    }
    
    query = f"{specialty} in {city}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        # Fallback: If a highly specific specialty fails, search for general clinics nearby
        if not data:
            fallback_url = f"https://nominatim.openstreetmap.org/search?q=clinic or hospital in {city}&format=json&addressdetails=1&limit=3"
            response = requests.get(fallback_url, headers=headers, timeout=8)
            data = response.json()
            
        if not data:
            return f"I couldn't find any medical facilities for {specialty} in {city} in the public map database. Try searching for a broader term or a larger neighboring city."
            
        formatted_results = []
        for place in data:
            # Extract the name of the clinic/hospital
            name = place.get("name") or place.get("display_name", "Unknown Facility").split(",")[0]
            
            # Extract the full address
            address = place.get("display_name", "Address unlisted")
            
            formatted_results.append(f"- {name} | Location: {address}")
            
        return f"Here are the nearest medical facilities I found in or near {city}:\n" + "\n".join(formatted_results)

    except Exception as e:
        print(f"OpenStreetMap API Error: {e}")
        return "System Note: The global map database is currently unresponsive. Please try again later."

@tool
def analyze_medications(medications: list[str]) -> str:
    """
    ALWAYS use this tool when a user mentions medications or drugs.
    - If 1 medication is provided: Returns general FDA usage, side effects, and warnings.
    - If 2 medications are provided: Checks the NIH database for adverse drug interactions.
    """
    if not medications:
        return "No medications provided to analyze."
        
    # --- MODE 1: General Drug Information (OpenFDA) ---
    if len(medications) == 1:
        return get_fda_drug_info(medications[0])
        
    # --- MODE 2: Drug-Drug Interactions (NIH RxNav) ---
    elif len(medications) >= 2:
        med1, med2 = medications[0], medications[1]
        
        rx1 = get_rxcui(med1)
        rx2 = get_rxcui(med2)
        
        if not rx1 or not rx2:
            return f"Could not find official clinical records to compare {med1} and {med2}. Verify spelling."

        url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rx1}+{rx2}"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if "fullInteractionTypeGroup" in data:
                interactions = []
                for group in data["fullInteractionTypeGroup"]:
                    for interaction in group["fullInteractionType"]:
                        description = interaction["interactionPair"][0]["description"]
                        severity = interaction["interactionPair"][0].get("severity", "CAUTION")
                        interactions.append(f"- [{severity.upper()}] {description}")
                
                return "NIH Database Interaction Warning:\n" + "\n".join(interactions)
            else:
                return f"No documented clinical interactions found between {med1} and {med2} in the NIH database."
                
        except Exception as e:
            return "System Note: The National Institutes of Health (NIH) database is temporarily unreachable."

@tool
def generate_diet_plan(condition: str, restrictions: str = "None") -> str:
    """
    ALWAYS use this tool when a user asks for a diet, meal plan, or nutritional advice.
    It routes the condition to a specialized Dietitian AI to generate a custom medical diet.
    """
    try:
        nutrition_llm = get_nutrition_specialist_llm()
        
        dietitian_prompt = f"""You are an expert Clinical Registered Dietitian. 
        A patient requires dietary intervention for the following condition: {condition}
        Their dietary restrictions/allergies are: {restrictions}
        
        Provide the following:
        1. The name of the recommended clinical diet (e.g., DASH, Low-FODMAP).
        2. A brief list of "Foods to Focus On" and "Foods to Strictly Avoid".
        3. A simple, 1-day sample meal plan (Breakfast, Lunch, Dinner).
        
        Keep it highly clinical, safe, and format it beautifully with bullet points.
        """
        
        response = nutrition_llm.invoke([HumanMessage(content=dietitian_prompt)])
        return f"Clinical Dietitian AI Recommendations:\n{response.content}"
        
    except Exception as e:
        return "System Note: The specialized nutrition model is currently unavailable. Recommend a general balanced diet for now."

# ==========================================
# TOOL EXPORT
# ==========================================

evaluator_tools = [
    analyze_symptoms_for_disease, 
    search_doctors, 
    analyze_medications, 
    generate_diet_plan
]