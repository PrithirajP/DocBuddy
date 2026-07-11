import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()

def get_hf_token():
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set in the .env file")
    return token

def get_hf_llm():
    """The Generalist/Orchestrator Model"""
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
    """The Clinical Diagnostic Model"""
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct", 
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        temperature=0.1,
        huggingfacehub_api_token=get_hf_token()
    )
    return ChatHuggingFace(llm=llm)

def get_nutrition_specialist_llm():
    """The Dietitian Model"""
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct", 
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        temperature=0.1,
        huggingfacehub_api_token=get_hf_token()
    )
    return ChatHuggingFace(llm=llm)