# graph/orchestrator.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from src.core.llm_factory import get_llm

llm = get_llm()

class PlanOutput(BaseModel):
    agents: List[str] = Field(description="Список агентов: ['chat_analyst', 'comment_analyst', 'profile_analyst', 'post_analyst]")
    reason: str = Field(description="Почему выбраны эти агенты")

parser = JsonOutputParser(pydantic_object=PlanOutput)

orchestrator_prompt = ChatPromptTemplate.from_template("""
Ты — умный оркестратор. Проанализируй запрос и выбери только нужные агенты.

Запрос: {user_query}

Агенты:
- chat_analyst — если нужно анализировать переписку в чате
- comment_analyst — если нужно анализировать комментарии под постом
- profile_analyst - если нужно анализировать профиль (подписки) пользователя
- post_analyst - если нужно анализировать реакции на посты. 

Верни **ТОЛЬКО JSON**:
{{
  "agents": ["chat_analyst"],
  "reason": "нужен анализ переписки"
}}

Формат: {format_instructions}
""")

orchestrator_chain = (
    {
        "user_query": lambda x: x["user_query"],
        "format_instructions": lambda x: parser.get_format_instructions()
    }
    | orchestrator_prompt
    | llm
    | parser
)