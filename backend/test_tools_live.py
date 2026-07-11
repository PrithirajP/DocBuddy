import asyncio
import os
from dotenv import load_dotenv

# Load env before importing tools
load_dotenv()

from app.agent.tools.diet import generate_diet_plan
from app.agent.tools.doctors import search_doctors
from app.agent.tools.medications import analyze_medications
from app.agent.tools.symptoms import analyze_symptoms_for_disease
from app.agent.tools.vision import analyze_medical_image

async def test_tools():
    print("Testing Diet Plan...")
    try:
        res = generate_diet_plan.invoke({"condition": "diabetes", "restrictions": "vegetarian"})
        print("DIET:", res[:200] + "...")
    except Exception as e:
        print("DIET ERROR:", e)

    print("\nTesting Doctors...")
    try:
        res = search_doctors.invoke({"city": "London", "specialty": "cardiologist"})
        print("DOCTORS:", res[:200] + "...")
    except Exception as e:
        print("DOCTORS ERROR:", e)

    print("\nTesting Medications (Single)...")
    try:
        res = analyze_medications.invoke({"medications": ["aspirin"]})
        print("MEDS (Single):", res[:200] + "...")
    except Exception as e:
        print("MEDS ERROR:", e)

    print("\nTesting Medications (Double - NIH)...")
    try:
        res = analyze_medications.invoke({"medications": ["lisinopril", "ibuprofen"]})
        print("MEDS (Double):", res[:200] + "...")
    except Exception as e:
        print("MEDS ERROR:", e)

    print("\nTesting Symptoms...")
    try:
        res = analyze_symptoms_for_disease.invoke({"symptoms": "headache and fever", "patient_context": "adult male"})
        print("SYMPTOMS:", res[:200] + "...")
    except Exception as e:
        print("SYMPTOMS ERROR:", e)

    print("\nTesting Vision (with dummy file)...")
    try:
        # create a dummy file
        with open("dummy_image.jpg", "w") as f:
            f.write("dummy base64 content")
        res = analyze_medical_image.invoke({"file_path": "dummy_image.jpg", "specific_question": "What is this?"})
        print("VISION:", res[:200] + "...")
        os.remove("dummy_image.jpg")
    except Exception as e:
        print("VISION ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test_tools())
