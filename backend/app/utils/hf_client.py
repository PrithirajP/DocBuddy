import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()

def get_hf_token():
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        raise ValueError("Error: HUGGINGFACEHUB_API_TOKEN is missing. Please check your .env file.")
    return hf_token

def get_hf_llm():
    """The Generalist/Orchestrator Model (Good at tool calling and conversation)"""
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.3-70B-Instruct",
        task="text-generation",
        max_new_tokens=1024,
        do_sample=False, 
        temperature=0.1, 
        huggingfacehub_api_token=get_hf_token()
    )
    return ChatHuggingFace(llm=llm)

def get_medical_specialist_llm():
    """The Clinical Diagnostic Model (Fine-tuned specifically for medicine)"""
    llm = HuggingFaceEndpoint(
        # Llama3-OpenBioLLM is a SOTA medical model. We use 8B for faster serverless inference.
        repo_id="aaditya/Llama3-OpenBioLLM-8B", 
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        temperature=0.1,
        huggingfacehub_api_token=get_hf_token()
    )
    return ChatHuggingFace(llm=llm)

def get_nutrition_specialist_llm():
    """The Clinical Dietitian Model - Focuses strictly on nutritional science"""
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.3-70B-Instruct", # A highly capable reasoning model
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        temperature=0.2, # Slightly higher temperature for creative meal planning, but still grounded
        huggingfacehub_api_token=get_hf_token()
    )
    return ChatHuggingFace(llm=llm)