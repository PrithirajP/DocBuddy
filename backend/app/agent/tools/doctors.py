import requests
from langchain_core.tools import tool

@tool
def search_doctors(city: str, specialty: str) -> str:
    """Finds hospitals, clinics, and medical specialists globally using OpenStreetMap."""
    headers = {"User-Agent": "DocBuddy-HealthApp/1.0"}
    spec = specialty.lower()
    
    if any(k in spec for k in ["physician", "general", "internal", "gastro", "neuro", "stomach", "migraine"]):
        search_term = "hospital"
    elif "dentist" in spec or "dental" in spec:
        search_term = "dentist"
    elif "eye" in spec or "ophthalmologist" in spec:
        search_term = "eye hospital"
    else:
        search_term = f"{specialty} hospital"

    query = f"{search_term}, {city}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=8"
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        if not data and search_term != "hospital":
            fallback_url = f"https://nominatim.openstreetmap.org/search?q=hospital, {city}&format=json&addressdetails=1&limit=5"
            response = requests.get(fallback_url, headers=headers, timeout=8)
            data = response.json()
            
        if not data:
            return f"I couldn't find any medical facilities listed under '{search_term}' in {city}."
            
        formatted_results = []
        for place in data:
            name = place.get("name") or place.get("display_name", "Medical Facility").split(",")[0]
            address = place.get("display_name", "Address unlisted")
            
            name_lower = name.lower()
            is_cosmetic = any(k in name_lower for k in ["dental", "hair", "skin", "cosmetic", "dental care"])
            requested_cosmetic = any(k in spec for k in ["dentist", "dental", "skin", "dermatologist"])
            
            if is_cosmetic and not requested_cosmetic:
                continue 
                
            formatted_results.append(f"- {name} | Location: {address}")
            
        if not formatted_results and data:
            for place in data[:3]:
                name = place.get("name") or place.get("display_name", "Medical Facility").split(",")[0]
                formatted_results.append(f"- {name} | Location: {place.get('display_name', 'Unknown')}")
            
        return f"Here are the recommended medical facilities found in or near {city}:\n" + "\n".join(formatted_results)
    except Exception as e:
        print(f"OpenStreetMap API Error: {e}")
        return "System Note: The global map database is temporarily unresponsive."