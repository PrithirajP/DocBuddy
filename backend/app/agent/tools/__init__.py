from .symptoms import analyze_symptoms_for_disease
from .doctors import search_doctors
from .medications import analyze_medications
from .diet import generate_diet_plan
from .vision import analyze_medical_image

# Re-export the array so nodes.py and graph.py don't need to change at all
evaluator_tools = [
    analyze_symptoms_for_disease, 
    search_doctors, 
    analyze_medications, 
    generate_diet_plan, 
    analyze_medical_image
]