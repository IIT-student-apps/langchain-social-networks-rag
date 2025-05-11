import logging
import requests
import os
import sys
import uuid
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain_utils import get_rag_chain
from chroma_utils import index_document_to_chroma as index_document  # Функция для индексирования файла в ChromaDB
from chroma_utils import list_indexed_files
from chroma_utils import delete_doc_from_chroma
from dotenv import load_dotenv
from db_utils import get_chat_history
from db_utils import insert_application_logs, get_chat_history
from db_utils import get_all_sessions_for_user  
from db_utils import delete_chat_history
from db_utils import insert_application_logs
from vkapi import get_vk_chat_history
from vkapi import get_vk_subscriptions
from conversation import parse_vk_messages, conversation_to_prompt
from vkapi import get_vk_q_and_a
from vkapi import get_vk_post_reactions
from token_grabber import get_vk_token
from pathlib import Path
from vkapi import get_vk_post_reactions
from posts import parse_vk_posts, posts_to_prompt

#from telegram.constants import ParseMode  # импорт, если ещё не добавил
load_dotenv()
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
VK_PEER_ID = os.getenv("VK_PEER_ID")
VK_USER_ID = os.getenv("VK_USER_ID")
VK_OWNER_ID = int(os.getenv("VK_OWNER_ID"))  # ID группы или пользователя
VK_POST_ID = int(os.getenv("VK_POST_ID"))    # ID конкретного поста
VK_DOMAIN = os.getenv("VK_DOMAIN")
VK_CLIENT_ID = os.getenv("VK_CLIENT_ID")




TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Путь к текущей папке, где лежит скрипт
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на уровень выше
BASE_DIR = os.path.dirname(CURRENT_DIR)

# Путь к папке rag_files, которая на уровень выше
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "rag_files")
# Создаём, если не существует
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Загружаем RAG-модель
rag_chain = get_rag_chain()

# Логирование
logging.basicConfig(level=logging.INFO)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

user_sessions = {}

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение"""
    await update.message.reply_text("Привет! Загрузи документ или задай вопрос, и я помогу!")

async def chat(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    session_id = user_sessions.get(user_id, str(user_id))  # если нет сессии — используется Telegram ID

    user_text = update.message.text
    chat_history = get_chat_history(session_id)

    response = rag_chain.invoke({
        "input": user_text,
        "chat_history": chat_history
    })
    answer = response["answer"]

    await update.message.reply_text(answer)

    insert_application_logs(session_id, user_text, answer, model="telegram")



import uuid

async def handle_document(update: Update, context: CallbackContext):
    """Обработчик загруженных документов"""
    document = update.message.document
    file_id = document.file_id

    # Получаем оригинальное имя или создаём своё
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
    user_prompt = " ".join(context.args).strip()

    if not user_prompt:
        await update.message.reply_text("❗ Пожалуйста, укажи, что нужно сделать с перепиской.\n\nПример:\n`/vkchat обобщи переписку`", parse_mode="MarkdownV2")
        return

    try:
        await update.message.reply_text("📥 Загружаю переписку из ВКонтакте...")

        vk_data = get_vk_chat_history(VK_PEER_ID, VK_ACCESS_TOKEN)
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
    try:
        await update.message.reply_text("📥 Получаю переписку из VK...")

        vk_data = get_vk_chat_history(VK_PEER_ID, VK_ACCESS_TOKEN)
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
    await update.message.reply_text("📡 Загружаю подписки пользователя ВКонтакте...")

    try:
        result = get_vk_subscriptions(VK_USER_ID, VK_ACCESS_TOKEN)
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить подписки.")
            return

        groups = result["response"]["items"]
        if not groups:
            await update.message.reply_text("🔍 Подписок не найдено.")
            return

        lines = []
        for group in groups:
            name = group.get("name", "Без названия")
            count = group.get("members_count", "неизвестно")
            desc = group.get("description", "—")

            lines.append(
                f"*Название:* {name}\n"
                f"*Участников:* {count}\n"
                f"*Описание:* {desc[:200]}{'...' if len(desc) > 200 else ''}\n"
                f"`──────────────`"
            )

        full_text = "\n\n".join(lines)

        # 🟢 Если нет аргументов — просто отправляем список
        if not context.args:
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(full_text[i:i+4000])
            return

        # 🧠 Есть аргументы — анализируем через LLM
        user_prompt = " ".join(context.args)
        llm_input = f"Вот список сообществ, на которые подписан пользователь ВКонтакте:\n\n{full_text}\n\n{user_prompt}"

        response = rag_chain.invoke({"input": llm_input, "chat_history": []})
        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def vkcomments(update: Update, context: CallbackContext):
    try:
        await update.message.reply_text("💬 Загружаю комментарии к посту ВКонтакте...")

        result = get_vk_q_and_a(VK_OWNER_ID, VK_POST_ID, VK_ACCESS_TOKEN)
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить комментарии.")
            return

        comments = result["response"].get("items", [])
        profiles = {p["id"]: p.get("name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                    for p in result["response"].get("profiles", []) + result["response"].get("groups", [])}

        if not comments:
            await update.message.reply_text("🔍 Комментарии не найдены.")
            return

        # Сформируем текст всех комментариев
        comment_texts = []
        for comment in comments[:150]:  # можно изменить лимит
            user_id = comment.get("from_id")
            author = profiles.get(user_id, f"ID {user_id}")
            text = comment.get("text", "").strip()
            if text:
                comment_texts.append(f"{author}: {text}")

        full_text = "\n".join(comment_texts)

        # 👇 Вариант 1: без аргументов — просто пересылаем
        if not context.args:
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(full_text[i:i+4000])
            return

        # 👇 Вариант 2: есть аргументы — передаём в LLM
        user_prompt = " ".join(context.args)
        llm_input = f"Вот комментарии к посту ВКонтакте:\n\n{full_text}\n\n{user_prompt}"

        response = rag_chain.invoke({"input": llm_input, "chat_history": []})
        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")



async def vkreactions(update: Update, context: CallbackContext):
    try:
        await update.message.reply_text("📊 Загружаю посты и реакции...")

        # Получаем JSON с постами
        result = get_vk_post_reactions(VK_OWNER_ID, VK_ACCESS_TOKEN)
        if not result or "response" not in result:
            await update.message.reply_text("❌ Не удалось получить посты.")
            return

        post_list = parse_vk_posts(result, post_number=10)  # парсим и берём до 10 постов

        if not post_list.posts:
            await update.message.reply_text("🔍 Посты не найдены.")
            return

        if not context.args:
            # 📋 Просто выводим текст постов и статистику
            for post in post_list.posts:
                short_text = post.text[:60].replace("\n", " ") + "…" if len(post.text) > 60 else post.text
                msg = (
                    f"📝 *{short_text}*\n"
                    f"👍 {post.likes} | 💬 {post.comments} | 🔁 {post.reposts} | 👁 {post.views}\n"
                    f"`──────────────`"
                )
                await update.message.reply_text(msg, parse_mode="Markdown")
            return

        # 🧠 Если есть вопрос — анализируем через LLM
        question = " ".join(context.args)
        prompt = posts_to_prompt(post_list, question)
        response = rag_chain.invoke({"input": prompt, "chat_history": []})

        await update.message.reply_text(f"🧠 Ответ:\n{response['answer']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


def update_env_file_key(key: str, value: str, path=ENV_PATH):
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
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Использование: /set KEY VALUE\nНапример: /set VK_USER_ID 123456789")
        return

    key = context.args[0].strip().upper()
    value = " ".join(context.args[1:]).strip()

    allowed_keys = {"VK_PEER_ID", "VK_USER_ID", "VK_OWNER_ID", "VK_POST_ID", "VK_ACCESS_TOKEN", "VK_START_CMID", "VK_COUNT", "VK_CLIENT_ID"}
    if key not in allowed_keys:
        await update.message.reply_text(f"❌ Недопустимый ключ: `{key}`", parse_mode="Markdown")
        return

    try:
        update_env_file_key(key, value)
        await update.message.reply_text(f"✅ Переменная `{key}` обновлена на `{value}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обновлении: {str(e)}")



async def gettoken(update: Update, context: CallbackContext):
    await update.message.reply_text("🌐 Сейчас откроется браузер. Авторизуйся во ВКонтакте...")
    token = await get_vk_token()
    await update.message.reply_text(f"✅ Токен сохранён в .env:\n`{token}`")


async def restart_bot(update: Update, context: CallbackContext):
    await update.message.reply_text("🔄 Перезапуск бота...")
    await context.bot.close()  # корректно закрываем соединение

    # перезапуск текущего скрипта
    os.execv(sys.executable, [sys.executable] + sys.argv)

def read_env_file():
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env[k] = v
    return env

async def get_env(update: Update, context: CallbackContext):
    allowed_keys = {
        "VK_PEER_ID",
        "VK_USER_ID",
        "VK_OWNER_ID",
        "VK_POST_ID",
        "VK_ACCESS_TOKEN",
        "VK_CLIENT_ID",
        "VK_COUNT",
        "VK_START_CMID"
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
    await update.message.reply_text("Выключение...")
    await context.bot.close()  # корректно закрываем соединение


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




    # Обработка сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Обработка загружаемых файлов
    


    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()