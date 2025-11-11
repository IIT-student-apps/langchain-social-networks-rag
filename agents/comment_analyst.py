
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from tools.vk_tools import collect_comments, set_post_from_url
from tools.llm_tools import find_questions, detect_spam
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
Ты — аналитик комментариев VK.
Используй инструменты последовательно:
1. set_post_from_url - обновить айди поста, используя ссылку из промпта
2. collect_comments — собрать комментарии
3. find_questions — найти вопросы
4. detect_spam — найти спам

Дай рекомендации в формате:
---
Вопросы: ...
Спам: ...
Рекомендация: ...
---
ПРАВИЛА (НАРУШЕНИЕ = ОШИБКА):
1. НЕ ПРИДУМЫВАЙ комментарии, имена, сообщения
2. ИСПОЛЬЗУЙ ТОЛЬКО то, что вернул инструмент collect_comments
    """
comment_analyst = create_agent(
    llm,
    tools=[set_post_from_url, collect_comments, find_questions, detect_spam],
    system_prompt=prompt,
    
)