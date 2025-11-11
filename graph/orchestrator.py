# graph/orchestrator.py
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

llm = ChatOllama(model="qwen3:8b", temperature=0.0)

class PlanOutput(BaseModel):
    agents: List[str] = Field(description="Список агентов: ['chat_analyst', 'comment_analyst']")
    reason: str = Field(description="Почему выбраны эти агенты")

parser = JsonOutputParser(pydantic_object=PlanOutput)

orchestrator_prompt = ChatPromptTemplate.from_template("""
Ты — умный оркестратор. Проанализируй запрос и выбери **только нужные** агенты.

Запрос: {user_query}

Агенты:
- chat_analyst — если нужно анализировать **переписку в чате**
- comment_analyst — если нужно анализировать **комментарии под постом**

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