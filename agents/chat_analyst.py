
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from tools.vk_tools import collect_chat_history, set_chat_from_url
from tools.llm_tools import detect_topics, analyze_sentiment

from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.0,    
    top_p=0.1,          
)


prompt = "system", """
Ты — аналитик чата VK. Используй инструменты последовательно:
1. set_chat_from_url - обновить айди нужного чата, если пользователь указал ссылку на чат в запросе (если не указал - пропустить)
2. collect_chat_history — собрать переписку
3. detect_topics — определить темы  
4. analyze_sentiment — оценить тон

Дай итоговый отчёт в формате:
---
Темы: ...
Тон: ...
Вывод: ...
---
ПРАВИЛА (НАРУШЕНИЕ = ОШИБКА):
1. НЕ ПРИДУМЫВАЙ переписку, имена, сообщения
2. ИСПОЛЬЗУЙ ТОЛЬКО то, что вернул инструмент collect_chat_history 
    """

chat_analyst = create_agent(
    llm,
    tools=[set_chat_from_url, collect_chat_history, detect_topics, analyze_sentiment],
    system_prompt=prompt,
    
)