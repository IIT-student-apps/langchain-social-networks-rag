
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from tools.vk_tools import collect_chat_history, set_chat_from_url
from tools.llm_tools import detect_topics, analyze_sentiment
from dotenv import load_dotenv
load_dotenv()
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.0,    
    top_p=0.1,          
)


prompt = "system", """
Ты — аналитик чата VK. Используй инструменты последовательно:
1. collect_chat_history — собрать переписку
2. detect_topics — определить темы  
3. analyze_sentiment — оценить тон

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
    tools=[collect_chat_history, detect_topics, analyze_sentiment],
    system_prompt=prompt,
    
)