
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from ..tools.vk_tools import collect_subscriptions
from ..tools.llm_tools import analyze_subs
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from ..core.llm_factory import get_llm
from dotenv import load_dotenv
load_dotenv()


llm = get_llm() 

prompt = """
Ты — аналитик профилей в VK.
Используй инструменты последовательно:
1. collect_subscriptions — собрать подписки пользователя
2. analyze_subs — проанализировать подписки пользователя

Дай отчёт в формате:
---
Предположительные интересы: ...

(Дополнительно) Возможно какие-либо интересные моменты. 
---
ПРАВИЛА (НАРУШЕНИЕ = ОШИБКА):
1. НЕ ПРИДУМЫВАЙ переписку, имена, сообщения
2. ИСПОЛЬЗУЙ ТОЛЬКО то, что вернул инструмент collect_subscriptions
    """
profile_analyst = create_agent(
    llm,
    tools=[collect_subscriptions, analyze_subs],
    system_prompt=prompt,
    
)