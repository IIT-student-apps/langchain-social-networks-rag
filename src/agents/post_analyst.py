import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv
from src.tools.vk_tools import collect_posts, set_post_by_id
from src.tools.llm_tools import analyze_comments, analyze_likes, analyze_views
from src.core.llm_factory import get_llm
load_dotenv()


llm = get_llm() 

prompt = """
Ты — аналитик постов сообщества в VK.
Используй инструменты последовательно:
1. collect_posts — собрать информацию о постах
2. analyze_comments — проанализировать количество комментариев
3. analyze_likes — проанализировать количество лайков
4. analyze_views — проанализировать количество просмотров
5. set_post_by_id - для записи в .env VK_POST_ID поста, на который указал пользователь и который ты нашёл. 
Например пользователь может попросить проанализировать посты и проанализировать комментарии под самым комментируемым. Тогда тебе надо будет выбрать номер поста с самым
большим количеством комментариев и вызвать set_post_by_id для записи в .env номера этого поста. Анализ комментариев - задача другого агента. Тебе надо только обновить .env.

Дай отчёт в формате:
---
Самые обсуждаемые посты (пиши с новой строки каждое название и пронумеруй): ...
Самые залайканные посты: ...
Самые просматриваемые посты: ... 

Укажи, был ли вызван set_post_by_id и обновлён ли .env
---
Если есть пересечения, можешь выделить посты, которые вызвали наибольший интерес (соотношение просмотров к лайкам/комментариям) и дописать про это в конце, но это не обязательно. 
Пиши очень кратко названия постов (1 предложение), и их номер
ПРАВИЛА (НАРУШЕНИЕ = ОШИБКА):
1. НЕ ПРИДУМЫВАЙ посты, названия, реакции
2. ИСПОЛЬЗУЙ ТОЛЬКО то, что вернул инструмент collect_posts
3. Отвечай ИСКЛЮЧИТЕЛЬНО по шаблону отчёт
4. Если пользователь попросил проанализировать комментарии под каким-то постом, ОБЯЗАТЕЛЬНО вызови set_post_by_id с указанием данных этого поста
5. Если collect_postsничего не вернул, то сообщи об этом, а не придумывай
    """
post_analyst = create_agent(
    llm,
    tools=[collect_posts, analyze_comments, analyze_likes, analyze_views, set_post_by_id],
    system_prompt=prompt,
    
)