
from langchain_core.tools import tool

from vkapi import get_vk_chat_history, get_vk_q_and_a, get_vk_subscriptions, get_vk_post_reactions 
from conversation import parse_vk_messages, conversation_to_prompt
from comments import parse_vk_comments, comments_to_prompt
from subscriptions import parse_vk_subscriptions, subscriptions_to_prompt
from posts import parse_vk_posts, posts_to_prompt
import os
import re
from typing import Optional
from langchain_core.tools import tool
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(r"D:\RAG\langchain-social-networks-rag\.env")
load_dotenv()


@tool
def collect_chat_history(max_messages: int = 20) -> str:
    """
    Собирает последние сообщения из чата VK.

    Использует VK API (messages.getHistory) и возвращает отформатированную переписку.

    Args:
        max_messages (int): Максимальное количество сообщений (по умолчанию 20).

    Returns:
        str: Переписка в формате:
             [Имя] Текст сообщения
             [Имя] Текст сообщения
             ...
             Если ошибка — сообщение об ошибке.
    """
    try:
        data = get_vk_chat_history(
            peer_id=os.getenv("VK_PEER_ID"),
            access_token=os.getenv("VK_ACCESS_TOKEN")
        )
        if not data or "response" not in data:
            return "Ошибка: не удалось получить историю чата (проверьте токен или peer_id)."

        conv = parse_vk_messages(data, msg_number=max_messages)
        if not conv:
            return "Чат пустой или нет сообщений."

        return conversation_to_prompt(conv, "")
    except Exception as e:
        return f"Ошибка при сборе чата: {str(e)}"


@tool
def collect_comments(post_id: Optional[str] = None, max_comments: int = 30) -> str:
    """
    Собирает комментарии под постом VK.

    Использует VK API (wall.getComments) и возвращает отформатированные комментарии.

    Args:
        post_id (str, optional): ID поста. Если не указан — берётся из .env (VK_POST_ID).
        max_comments (int): Максимальное количество комментариев (по умолчанию 30).

    Returns:
        str: Комментарии в формате:
             [Имя]
             Текст комментария
             Лайков: N

             [Имя]
             ...
             Если ошибка — сообщение об ошибке.
    """
    try:
        post_id = os.getenv("VK_POST_ID")
        if not post_id:
            return "Ошибка: не указан VK_POST_ID в .env или в аргументе."

        owner_id = os.getenv("VK_OWNER_ID")
        if not owner_id:
            return "Ошибка: не указан VK_OWNER_ID в .env."

        data = get_vk_q_and_a(
            owner_id=owner_id,
            post_id=post_id,
            access_token=os.getenv("VK_ACCESS_TOKEN")
        )
        if not data or "response" not in data:
            return "Ошибка: не удалось получить комментарии (проверьте post_id или токен)."

        thread = parse_vk_comments(data, comment_number=max_comments)
        if not thread:
            return "Под постом нет комментариев."

        return comments_to_prompt(thread, "")
    except Exception as e:
        return f"Ошибка при сборе комментариев: {str(e)}"





@tool
def collect_subscriptions() -> str:
    """Собирает подписки пользователя."""
    try:
        data = get_vk_subscriptions(
            user_id=os.getenv("VK_USER_ID"),
            access_token=os.getenv("VK_ACCESS_TOKEN")
        )
        if not data or "response" not in data:
            return "Ошибка: не удалось получить подписки."

        subs = parse_vk_subscriptions(data)
        return subscriptions_to_prompt(subs, "")
    except Exception as e:
        return f"Ошибка при сборе подписок: {str(e)}"


@tool
def collect_posts(max_posts: int = 10) -> str:
    """Собирает последние посты с реакциями."""
    try:
        data = get_vk_post_reactions(
            owner_id=os.getenv("VK_OWNER_ID"),
            access_token=os.getenv("VK_ACCESS_TOKEN")
        )
        if not data or "response" not in data:
            return "Ошибка: не удалось получить посты."

        posts = parse_vk_posts(data, post_number=max_posts)
        return posts_to_prompt(posts, "")
    except Exception as e:
        return f"Ошибка при сборе постов: {str(e)}"
    



@tool
def set_post_from_url(url: str) -> str:
    """
    Парсит ссылку на пост VK и обновляет .env (VK_OWNER_ID, VK_POST_ID).

    Пример: https://vk.com/warthunder?w=wall-13137988_6241470
    → VK_OWNER_ID = -13137988
    → VK_POST_ID = 6241470

    Args:
        url (str): Полная ссылка на пост VK.

    Returns:
        str: Подтверждение или сообщение об ошибке.
    """

    def update_env(key: str, value: str):

        if ENV_PATH.exists():
            lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
        else:
            lines = []

        new_lines = []
        found = False

        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key}={value}")

        ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        os.environ[key] = value

  
    match = re.search(r"wall(-?\d+)_(\d+)", url)
    if not match:
        return "Ошибка: неверный формат ссылки. Ожидается wall-XXXX_YYYY"

    owner_id = match.group(1)
    post_id = match.group(2)

    if not owner_id.startswith("-"):
        owner_id = f"-{owner_id}"


    update_env("VK_OWNER_ID", owner_id)
    update_env("VK_POST_ID", post_id)

    return f"Пост установлен:\nVK_OWNER_ID = {owner_id}\nVK_POST_ID = {post_id}"



@tool
def set_chat_from_url(url: str) -> str:
    """
    Парсит ссылку на чат VK и обновляет .env (VK_PEER_ID).

    Пример: https://vk.com/im/convo/2000000006?entrypoint=list_all
    → VK_PEER_ID = 2000000006

    Args:
        url (str): Полная ссылка на чат VK.

    Returns:
        str: Подтверждение или сообщение об ошибке.
    """

    def update_env(key: str, value: str):
        if ENV_PATH.exists():
            lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
        else:
            lines = []

        new_lines = []
        found = False

        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key}={value}")

        ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        os.environ[key] = value


    match = re.search(r"convo/(\d+)", url)
    if not match:
        return "Ошибка: не удалось распознать ссылку на чат. Ожидается формат: convo/XXXXXXXXX"

    peer_id = match.group(1)
    update_env("VK_PEER_ID", peer_id)

    return f"Чат установлен:\nVK_PEER_ID = {peer_id}\n\nТеперь используйте /analyze"