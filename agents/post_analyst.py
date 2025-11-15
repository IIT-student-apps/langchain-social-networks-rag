from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from tools.vk_tools import collect_posts, set_post_by_id
from tools.llm_tools import analyze_comments, analyze_likes, analyze_views
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
Ты — аналитик постов сообщества в VK.
Используй инструменты последовательно:
1. collect_posts — собрать информацию о постах
2. analyze_comments — проанализировать количество комментариев
3. analyze_likes — проанализировать количество лайков
4. analyze_views — проанализировать количество просмотров
5. set_post_by_id - для записи в .env номера поста, если пользователь например попросил далее проанализировать какой-то конкретный пост.


Дай отчёт в формате:
---
Самые обсуждаемые посты (пиши с новой строки каждое название и пронумеруй): ...
Самые залайканные посты: ...
Самые просматриваемые посты: ... 

---
Если есть пересечения, можешь выделить посты, которые вызвали наибольший интерес (соотношение просмотров к лайкам/комментариям) и дописать про это в конце, но это не обязательно. 
Пиши очень кратко названия постов (1 предложение), и их номер
ПРАВИЛА (НАРУШЕНИЕ = ОШИБКА):
1. НЕ ПРИДУМЫВАЙ переписку, имена, сообщения
2. ИСПОЛЬЗУЙ ТОЛЬКО то, что вернул инструмент collect_posts
3. Отвечай ИСКЛЮЧИТЕЛЬНО по шаблону отчёта
    """
post_analyst = create_agent(
    llm,
    tools=[collect_posts, analyze_comments, analyze_likes, analyze_views, set_post_by_id],
    system_prompt=prompt,
    
)