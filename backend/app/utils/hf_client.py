import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()

def get_hf_llm():
    """Initializes and returns the Hugging Face Chat Model."""
    
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.3-70B-Instruct",
        task="text-generation",
        max_new_tokens=1024,
        do_sample=False, 
        temperature=0.1, # Low temperature for more deterministic, factual medical responses
    )
    
    chat_model = ChatHuggingFace(llm=llm)
    return chat_model