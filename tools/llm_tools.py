
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

@tool
def analyze_subs(text: str) -> str:
    """Оценивает подписки пользователя."""
    prompt = f"Сделай вывод об интересах пользователя, его увлечениях и т.д. исходя из сообществ, на которые он подписан.\n\n{text[:6000]}"
    return llm.invoke(prompt).content

@tool
def analyze_likes(text: str) -> str:
    """Оценивает реакции на посты."""
    prompt = f"Сделай топ 3 самых залайканых постов. Формат: 1 место: ... и т.д.\n\n{text[:6000]}"
    return llm.invoke(prompt).content

@tool
def analyze_comments(text: str) -> str:
    """Оценивает количество комментариев на постах."""
    prompt = f"Сделай топ 3 постов с самым большим количеством комментариев. Формат: 1 место: ... и т.д.\n\n{text[:6000]}"
    return llm.invoke(prompt).content

@tool
def analyze_views(text: str) -> str:
    """Оценивает количество просмотров на постах."""
    prompt = f"Сделай топ 3 постов с самым большим количеством просмотров. Формат: 1 место: ... и т.д.\n\n{text[:6000]}"
    return llm.invoke(prompt).content