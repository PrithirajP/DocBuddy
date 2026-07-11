import requests
from langchain_core.tools import tool
import os
from app.utils.hf_client import get_hf_llm

# --- HELPERS ---
def get_rxcui(drug_name: str) -> str:
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    
    # Apply the Good Citizen header here too!
    dev_email = os.getenv("DEVELOPER_EMAIL", "developer@example.com")
    headers = {
        "User-Agent": f"DocBuddy-PortfolioProject/1.0 (mailto:{dev_email})",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        if "idGroup" in data and "rxnormId" in data["idGroup"]:
            return data["idGroup"]["rxnormId"][0]
    except Exception as e:
        print(f"RxCUI Error for {drug_name}: {e}")
    return None

def get_fda_drug_info(drug_name: str) -> str:
    url = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{drug_name}"+openfda.brand_name:"{drug_name}"&limit=1'
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()["results"][0]
            indications = data.get("indications_and_usage", ["No specific indications found."])[0][:600]
            warnings = data.get("warnings", ["No general warnings found."])[0][:600]
            adverse = data.get("adverse_reactions", ["No adverse reactions listed."])[0][:600]
            return f"FDA Clinical Data for {drug_name.upper()}:\n- INDICATIONS: {indications}...\n- WARNINGS: {warnings}...\n- ADVERSE REACTIONS: {adverse}..."
    except Exception:
        pass
    return f"Could not retrieve specific FDA database info for {drug_name}."

# --- TOOL ---
@tool
def analyze_medications(medications: list[str]) -> str:
    """ALWAYS use this tool when a user mentions medications or drugs."""
    if not medications:
        return "No medications provided to analyze."
        
    if len(medications) == 1:
        return get_fda_drug_info(medications[0])
        
    elif len(medications) >= 2:
        med1 = medications[0].strip().lower()
        med2 = medications[1].strip().lower()
        
        # EMERGENCY PORTFOLIO FALLBACK
        FALLBACK_DB = {
            tuple(sorted(["omeprazole", "clopidogrel"])): "- [SEVERE] Omeprazole blocks the activation of Clopidogrel, significantly increasing the risk of blood clots and stroke. Avoid using together.",
            tuple(sorted(["aspirin", "warfarin"])): "- [SEVERE] Combining these medications severely increases the risk of dangerous internal bleeding.",
            tuple(sorted(["lisinopril", "ibuprofen"])): "- [MODERATE] Ibuprofen can decrease the blood-pressure-lowering effects of Lisinopril and may strain the kidneys."
        }
        
        try:
            llm = get_hf_llm()
            prompt = f"Analyze potential clinical drug interactions between '{med1}' and '{med2}'. Focus strictly on pharmacological interactions and list the severity (SEVERE, MODERATE, or NONE). Keep it highly concise."
            response = llm.invoke(prompt)
            return "AI Interaction Analysis:\n" + response.content
        except Exception as e:
            print(f"\n--- LLM API ERROR ---\n{e}\n------------------------\n")
            meds_tuple = tuple(sorted([med1, med2]))
            if meds_tuple in FALLBACK_DB:
                return "Interaction Warning (Cached Offline Backup):\n" + FALLBACK_DB[meds_tuple]
            return "System Note: Interaction analysis is currently unavailable."