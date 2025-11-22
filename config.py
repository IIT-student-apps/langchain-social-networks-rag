import os

ACTIVE_MODEL = "groq_moonshotai" 

LLM_CONFIGS = {
    "local_qwen3:8b": {
        "provider": "ollama",
        "model": "qwen3:8b",
        "temperature": 0.0,
        "top_p": 0.1,
        "base_url": "http://localhost:11434",
    },
    "groq_qwen": {
        "provider": "groq",
        "model": "qwen/qwen3-32b", 
        "temperature": 0.0,
        "top_p": 0.95,     
        "api_key": os.getenv("GROQ"), 
        "reasoning_effort": "none"
    },
    "groq_moonshotai": {
        "provider": "groq",
        "model": "moonshotai/kimi-k2-instruct-0905", 
        "temperature": 0.0,
        "top_p": 0.95,     
        "api_key": os.getenv("GROQ"), 
        
    }
    
    
}