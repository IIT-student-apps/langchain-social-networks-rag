import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv
from src.tools.vk_tools import collect_comments, set_post_from_url
from src.tools.llm_tools import find_questions, detect_spam
from src.core.llm_factory import get_llm

load_dotenv()

llm = get_llm() 


prompt = """
Ты — аналитик комментариев VK.
Используй инструменты последовательно:
1. collect_comments — собрать комментарии
2. find_questions — найти вопросы
3. detect_spam — найти спам

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
    tools=[collect_comments, find_questions, detect_spam],
    system_prompt=prompt,
    
)