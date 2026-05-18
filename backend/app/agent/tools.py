from langchain_core.tools import tool

@tool
def search_doctors(location: str, specialty: str) -> str:
    """
    Finds recommended doctors nearby based on location and specialty.
    Always use this when a patient needs a physical consultation.
    """
    # TODO: In the future, integrate a real API like Google Places or Zocdoc
    return f"Found 3 highly-rated {specialty}s available in {location}: Dr. Adams, Dr. Sharma, and Dr. Lee. I recommend booking an appointment."

@tool
def check_drug_interactions(current_medications: list[str], new_medication: str = None) -> str:
    """
    Checks for adverse drug-drug interactions between medications.
    """
    # TODO: In the future, integrate the NIH RxNorm API
    meds = current_medications + ([new_medication] if new_medication else [])
    
    if "Ibuprofen" in meds and "Lisinopril" in meds:
        return "Warning: Taking Ibuprofen with Lisinopril can decrease the effectiveness of the blood pressure medication and strain the kidneys."
    
    return f"No severe interactions found among: {', '.join(meds)}."

@tool
def generate_diet_plan(condition: str) -> str:
    """
    Generates a high-level diet and routine recommendation based on a diagnosed condition.
    """
    if "hypertension" in condition.lower() or "blood pressure" in condition.lower():
        return "Recommended Diet: DASH Diet (Dietary Approaches to Stop Hypertension). High in vegetables, fruits, and whole grains. Low in sodium. Routine: 30 mins of moderate aerobic exercise daily."
    return "Recommended Diet: Balanced whole-food diet, rich in proteins and fiber. Ensure 8 hours of sleep and adequate hydration."

# Export the tools as a list to easily bind them to our model later
evaluator_tools = [search_doctors, check_drug_interactions, generate_diet_plan]