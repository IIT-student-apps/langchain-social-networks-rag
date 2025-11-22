# llm_factory.py
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import config

def get_llm():
    # Получаем настройки активной модели
    active_config = config.LLM_CONFIGS[config.ACTIVE_MODEL]
    provider = active_config["provider"]

    if provider == "ollama":
        return ChatOllama(
            model=active_config["model"],
            temperature=active_config["temperature"],
            top_p=active_config.get("top_p", 0.1), # .get позволяет задать дефолт
            base_url=active_config.get("base_url")
        )
    
    elif provider == "groq":
        
        return ChatGroq(
            model=active_config["model"],
            temperature=active_config["temperature"],
            api_key=active_config["api_key"],
            max_tokens=active_config.get("max_tokens"),
            
        )
    
    else:
        raise ValueError(f"Неизвестный провайдер LLM: {provider}")