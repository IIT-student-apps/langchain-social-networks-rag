
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.3
)



@tool
def detect_topics(text: str) -> str:
    """Определяет основные темы"""
    prompt = f"Выдели несколько основных тем. Формат: нумерованный список. Запрещено придумывать собственные\n\n{text[:6000]}"
    return llm.invoke(prompt).content


@tool
def analyze_sentiment(text: str) -> str:
    """Оценивает общий эмоциональный тон."""
    prompt = f"Оцени тон: позитивный, негативный, нейтральный. Объясни.\n\n{text[:6000]}"
    return llm.invoke(prompt).content


@tool
def find_questions(text: str) -> str:
    """Находит вопросы пользователей."""
    prompt = f"Найди все вопросы. Формат: - Вопрос: ... . Запрещено придумывать самостоятельно\n\n{text[:6000]}"
    return llm.invoke(prompt).content


@tool
def detect_spam(text: str) -> str:
    """Находит спам и рекламу."""
    prompt = f"Найди спам, рекламу, ссылки без контекста. Формат: - Спам: ... . Запрещено придумывать самостоятельно.\n\n{text[:6000]}"
    return llm.invoke(prompt).content