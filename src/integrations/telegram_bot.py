import logging
import requests
import os
import sys
import uuid
import subprocess
import re
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GETTOKEN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "token_grabber.py"

load_dotenv(PROJECT_ROOT / ".env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
from src.core.db_utils import get_chat_history
from src.core.langchain_utils import get_rag_chain
from src.core.chroma_utils import index_document_to_chroma as index_document
from src.core.chroma_utils import list_indexed_files
from src.core.chroma_utils import delete_doc_from_chroma
from src.core.db_utils import insert_application_logs, get_chat_history
from src.core.db_utils import get_all_sessions_for_user  
from src.core.db_utils import delete_chat_history
from src.core.db_utils import insert_application_logs
from src.integrations.vk_client import get_vk_chat_history
from src.integrations.vk_client import get_vk_subscriptions
from src.core.models import parse_vk_messages, conversation_to_prompt
from src.integrations.vk_client import get_vk_q_and_a
from src.integrations.vk_client import get_vk_post_reactions
from src.core.models import parse_vk_comments, comments_to_prompt
from src.tools.vk_tools import set_post_from_url, set_chat_from_url
from src.core.models import parse_vk_posts, posts_to_prompt
from src.core.models import parse_vk_subscriptions, subscriptions_to_prompt
from src.graph.workflow import app as analysis_graph

ADMIN_ID = 909658267



DOWNLOAD_FOLDER = PROJECT_ROOT / "rag_files"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
ENV_PATH = PROJECT_ROOT / ".env"

rag_chain = get_rag_chain()

# Логирование
logging.basicConfig(level=logging.INFO)
user_sessions = {}


async def chat(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    session_id = user_sessions.get(user_id, str(user_id))

    user_text = update.message.text
    chat_history = get_chat_history(session_id)

    response = rag_chain.invoke({
        "input": user_text,
        "chat_history": chat_history
    })
    answer = response["answer"]

    await update.message.reply_text(answer)

    insert_application_logs(session_id, user_text, answer, model="telegram")


async def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    if not file_name:
        file_ext = os.path.splitext(document.mime_type)[1] or ".bin"
        file_name = f"file_{file_id}{file_ext}"

    # Нормализуем путь и избегаем дубликатов
    base_name, ext = os.path.splitext(file_name)
    clean_name = f"{base_name}{ext}"
    file_path = os.path.join(DOWNLOAD_FOLDER, clean_name)

    # Если файл уже есть, добавим суффикс
    counter = 1
    while os.path.exists(file_path):
        clean_name = f"{base_name}_{counter}{ext}"
        file_path = os.path.join(DOWNLOAD_FOLDER, clean_name)
        counter += 1

    # Скачиваем файл
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(file_path)

    # Индексируем
    try:
        success = index_document(file_path, file_id=hash(clean_name))
        if success:
            await update.message.reply_text(f"✅ Файл *{clean_name}* загружен и проиндексирован!", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Не удалось проиндексировать файл {clean_name}.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке файла: {str(e)}")





async def list_files(update: Update, context: CallbackContext):
    file_info = list_indexed_files()
    if not file_info:
        await update.message.reply_text("Нет загруженных файлов.")
        return

    message = "📂 *Загруженные файлы:*\n"
    for (fid, fname), count in file_info.items():
        message += f"• `{fname}`\n  file\\_id: `{str(fid)}` — {count} чанков\n\n"

    await update.message.reply_text(message)




async def delete(update: Update, context: CallbackContext):
    try:
        file_id = int(context.args[0])
        result = delete_doc_from_chroma(file_id)
        if result:
            await update.message.reply_text(f"Документы с file_id {file_id} удалены.")
        else:
            await update.message.reply_text(f"Не удалось удалить документы с file_id {file_id}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажи file_id после команды. Пример:\n/delete 123456789")


async def session_id_cmd(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    session_id = user_sessions.get(user_id, str(user_id))  # <-- важно!
    await update.message.reply_text(f"🆔 Текущий session_id:\n`{session_id}`", parse_mode="MarkdownV2")



async def history(update: Update, context: CallbackContext):
    session_id = str(update.effective_user.id)
    history = get_chat_history(session_id)

    if not history:
        await update.message.reply_text("История пуста.")
        return

    message = f"💬 История:\n"
    for msg in history[-10:]:  # последние 10 сообщений
        role = "👤" if msg["role"] == "human" else "🤖"
        content = msg["content"].strip()
        message += f"{role} {content}\n"

    # Дробим длинные сообщения
    for chunk in split_message(message):
        await update.message.reply_text(chunk)


def split_message(text, max_length=4000):
    """Делит длинное сообщение на части"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]



async def newchat(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    new_session_id = f"{user_id}_{uuid.uuid4()}"
    user_sessions[user_id] = new_session_id

    insert_application_logs(new_session_id, "[system] новая сессия", "", "telegram")

    await update.message.reply_text(
        f"✨ Новый чат начат!\nТекущий session_id: `{new_session_id}`" )


async def switch(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        new_session_id = context.args[0]
        user_sessions[user_id] = new_session_id
        await update.message.reply_text(f"🔁 Переключено на сессию `{new_session_id}`")
    except IndexError:
        await update.message.reply_text("⚠️ Укажи session_id. Пример: /switch 8f1c...")


async def sessions(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    sessions = get_all_sessions_for_user(user_id)
    if not sessions:
        await update.message.reply_text("❌ У тебя пока нет сохранённых сессий.")
        return

    message = "📂 Твои сессии:\n"
    for sid in sessions:
        active_marker = " (текущая)" if user_sessions.get(update.effective_user.id) == sid else ""
        message += f"• `{sid}`{active_marker}\n"

    await update.message.reply_text(message)


async def reset(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    session_id = user_sessions.get(user_id, str(user_id))

    delete_chat_history(session_id)
    await update.message.reply_text(f"🧹 История чата для session_id `{session_id}` удалена.")



async def vkchat(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    user_prompt = " ".join(context.args).strip()

    if not user_prompt:
        await update.message.reply_text("❗ Пожалуйста, укажи, что нужно сделать с перепиской.\n\nПример:\n`/vkchat обобщи переписку`", parse_mode="MarkdownV2")
        return

    try:
        await update.message.reply_text("📥 Загружаю переписку из ВКонтакте...")

        vk_data = get_vk_chat_history(os.getenv("VK_PEER_ID"), os.getenv("VK_ACCESS_TOKEN"))
        if not vk_data:
            await update.message.reply_text("❌ Не удалось получить переписку из VK.")
            return

        convo = parse_vk_messages(vk_data)
        prompt = conversation_to_prompt(convo, user_prompt)

        response = rag_chain.invoke({"input": prompt, "chat_history": []})
        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке: {str(e)}")

def format_conversation_text(convo):
    return "\n".join(
        [f"{msg.author_first_name} {msg.author_last_name}: {msg.text}" for msg in convo.messages]
    )


async def vkraw(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    try:
        await update.message.reply_text("📥 Получаю переписку из VK...")

        vk_data = get_vk_chat_history(os.getenv("VK_PEER_ID"), os.getenv("VK_ACCESS_TOKEN"))
        if not vk_data:
            await update.message.reply_text("❌ Не удалось получить переписку из VK.")
            return

        convo = parse_vk_messages(vk_data)
        raw_text = format_conversation_text(convo)

        # Делим текст на части (в Telegram есть лимит 4096 символов)
        max_len = 4000
        parts = [raw_text[i:i+max_len] for i in range(0, len(raw_text), max_len)]

        for i, part in enumerate(parts):
            await update.message.reply_text(f"{part}")

        await update.message.reply_text(f"✅ Отправлено {len(parts)} сообщений.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке: {str(e)}")


async def vksubs(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    await update.message.reply_text("📡 Загружаю подписки пользователя ВКонтакте...")

    try:
        result = get_vk_subscriptions(os.getenv("VK_USER_ID"), os.getenv("VK_ACCESS_TOKEN"))
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить подписки.")
            return

        sub_list = parse_vk_subscriptions(result, group_number=int(os.getenv("VK_COUNT", 10)))
        if not sub_list.groups:
            await update.message.reply_text("🔍 Подписок не найдено.")
            return

        if not context.args:
            # 📋 Просто выводим список подписок
            for group in sub_list.groups:
                msg = (
                    f"*Название:* {group.name}\n"
                    f"*Участников:* {group.members_count}\n"
                    f"*Описание:* {group.description or '—'}\n"
                    f"`──────────────`"
                )
                await update.message.reply_text(msg)
            return

        # Есть аргументы — анализ через LLM
        question = " ".join(context.args)
        prompt = subscriptions_to_prompt(sub_list, question)
        response = rag_chain.invoke({"input": prompt, "chat_history": []})

        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def vkcomments(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    try:
        await update.message.reply_text("💬 Загружаю комментарии к посту ВКонтакте...")

        result = get_vk_q_and_a(os.getenv("VK_OWNER_ID"), os.getenv("VK_POST_ID"), os.getenv("VK_ACCESS_TOKEN"))
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить комментарии.")
            return

        thread = parse_vk_comments(result, comment_number=int(os.getenv("VK_COUNT", 10)))
        if not thread.comments:
            await update.message.reply_text("🔍 Комментарии не найдены.")
            return

        #Просто показать комментарии
        if not context.args:
            for comment in thread.comments:
                full_text = comment.text.replace("\n", " ")
                msg = (
                    f"*{comment.author_name}*\n"
                    f"{full_text}\n"
                    f"👍 {comment.likes}\n"
                    f"`──────────────`"
                )
                await update.message.reply_text(msg)
            return

        #Вопрос к LLM
        question = " ".join(context.args)
        prompt = comments_to_prompt(thread, question)
        response = rag_chain.invoke({"input": prompt, "chat_history": []})

        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def vkreactions(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    try:
        await update.message.reply_text("📊 Загружаю посты и реакции...")

        # Получаем JSON с постами
        result = get_vk_post_reactions(os.getenv("VK_OWNER_ID"), os.getenv("VK_ACCESS_TOKEN"))
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить посты.")
            return

        post_list = parse_vk_posts(result, post_number=int(os.getenv("VK_COUNT", 10)))  

        if not post_list.posts:
            await update.message.reply_text("🔍 Посты не найдены.")
            return

        if not context.args:
            # 📋 Просто выводим текст постов и статистику
            for post in post_list.posts:
                short_text = post.text[:120].replace("\n", " ") + "…" if len(post.text) > 120 else post.text
                msg = (
                    f"📝 *{short_text}*\n"
                    f"👍 {post.likes} | 💬 {post.comments} | 🔁 {post.reposts} | 👁 {post.views}\n"
                    f"`──────────────`"
                )
                await update.message.reply_text(msg)
            return

        # 🧠 Если есть вопрос — анализируем через LLM
        question = " ".join(context.args)
        prompt = posts_to_prompt(post_list, question)
        response = rag_chain.invoke({"input": prompt, "chat_history": []})

        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


def update_env_file_key(key: str, value: str, path=ENV_PATH):
    load_dotenv(override=True)
    updated = False
    lines = []

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break

    if not updated:
        lines.append(f"{key}={value}\n")

    with path.open("w", encoding="utf-8") as f:
        f.writelines(lines)

async def set_env(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Использование: /set KEY VALUE\nНапример: /set VK_USER_ID 123456789")
        return

    key = context.args[0].strip().upper()
    value = " ".join(context.args[1:]).strip()

    allowed_keys = {"VK_PEER_ID", "VK_USER_ID", "VK_OWNER_ID", "VK_POST_ID", "VK_ACCESS_TOKEN", "VK_START_CMID", "VK_COUNT", "VK_CLIENT_ID", "VK_START_CMID", "VK_OFFSET"}
    if key not in allowed_keys:
        await update.message.reply_text(f"❌ Недопустимый ключ: `{key}`", parse_mode="Markdown")
        return

    try:
        update_env_file_key(key, value)
        await update.message.reply_text(f"✅ Переменная `{key}` обновлена на `{value}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обновлении: {str(e)}")



async def gettoken(update: Update, context: CallbackContext):
    try:
        subprocess.Popen(["python", GETTOKEN_SCRIPT_PATH])
        await update.message.reply_text(
            "🌐 Окно браузера должно открыться. Авторизуйся во ВКонтакте.\n"
            "Токен будет сохранён в `.env`, как только будет обнаружен."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при запуске граббера: {str(e)}")




async def restart_bot(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 У тебя нет прав перезапускать бота.")
        return

    await update.message.reply_text("🔄 Перезапуск бота...")

    # Просто перезапуск процесса
    os.execv(sys.executable, [sys.executable, __file__])



def read_env_file():
    load_dotenv(override=True)
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env[k] = v
    return env

async def get_env(update: Update, context: CallbackContext):
    load_dotenv(override=True)
    allowed_keys = {
        "VK_PEER_ID",
        "VK_USER_ID",
        "VK_OWNER_ID",
        "VK_POST_ID",
        "VK_ACCESS_TOKEN",
        "VK_CLIENT_ID",
        "VK_COUNT",
        "VK_START_CMID",
        "VK_OFFSET"
    }

    if not context.args:
        await update.message.reply_text(
            "⚠️ Использование: /get VK_USER_ID\nМожно получить одну из: " +
            ", ".join(allowed_keys)
        )
        return

    key = context.args[0].strip().upper()
    if key not in allowed_keys:
        await update.message.reply_text(f"❌ Недопустимый ключ: `{key}`", parse_mode="Markdown")
        return

    env_vars = read_env_file()
    value = env_vars.get(key)

    if value:
        await update.message.reply_text(f"🔐 `{key}` = `{value}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ Значение `{key}` не найдено в .env", parse_mode="Markdown")


async def close_bot(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 У тебя нет прав выключать бота.")
        return

    await update.message.reply_text("⏹ Бот отключается...")
    

    sys.exit(0)





async def analyze_vk(update: Update, context: CallbackContext):
    text = update.message.text
    query = " ".join(context.args) or "Проанализируй сообщество"
    await update.message.reply_text("Анализирую данные...")

    url = None
    url_match = re.search(r"wall(-?\d+)_(\d+)", query)     # пост
    url2_match = re.search(r"convo\/(\d+)", query)         # беседа / диалог

    # 1. Если нашли ссылку на пост VK
    if url_match:
        url = url_match.group(0)

        try:
            result = set_post_from_url.invoke({"url": url})
            await update.message.reply_text(f"{result}\n\nАнализирую...")
        except Exception as e:
            await update.message.reply_text(f"Ошибка установки поста: {e}")
            return

    # 2. Если нашли ссылку на беседу VK
    elif url2_match:
        convo_id = url2_match.group(1)
        try:
            result = set_chat_from_url.invoke({"url": convo_id})
            await update.message.reply_text(f"{result}\n\nАнализирую...")
        except Exception as e:
            await update.message.reply_text(f"Ошибка установки беседы: {e}")
            return

    # 3. Основной анализ
    try:
        result = await analysis_graph.ainvoke({
            "user_query": query,
            "results": []
        })
        
        final_answer = result["final_answer"]
        

        max_length = 4000
        parts = [final_answer[i:i + max_length] for i in range(0, len(final_answer), max_length)]

        for i, part in enumerate(parts):
            prefix = f"**Часть {i+1}/{len(parts)}**\n\n" if len(parts) > 1 else ""
            await update.message.reply_text(prefix + part)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")




def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("delete", delete))  
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("session_id", session_id_cmd))
    app.add_handler(CommandHandler("sessions", sessions))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("vkchat", vkchat))
    app.add_handler(CommandHandler("vkraw", vkraw))
    app.add_handler(CommandHandler("vksubs", vksubs))
    app.add_handler(CommandHandler("vkcomments", vkcomments))
    app.add_handler(CommandHandler("vkreactions", vkreactions))
    app.add_handler(CommandHandler("gettoken", gettoken))
    app.add_handler(CommandHandler("set", set_env))
    app.add_handler(CommandHandler("restart", restart_bot))
    app.add_handler(CommandHandler("get", get_env))
    app.add_handler(CommandHandler("close", close_bot))

    app.add_handler(CommandHandler("analyze", analyze_vk))


    # Обработка сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Обработка загружаемых файлов
    


    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()