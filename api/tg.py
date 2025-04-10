import logging
import requests
import os
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



load_dotenv()
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


user_sessions = {}

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение"""
    await update.message.reply_text("Привет! Загрузи документ или задай вопрос, и я помогу!")

async def chat(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    session_id = user_sessions.get(user_id, str(user_id))  # по умолчанию Telegram ID

    user_text = update.message.text
    chat_history = get_chat_history(session_id)
    response = rag_chain.invoke({"input": user_text, "chat_history": chat_history})
    answer = response["answer"]

    await update.message.reply_text(answer)
    insert_application_logs(session_id, user_text, answer, model="telegram")


async def handle_document(update: Update, context: CallbackContext):
    """Обработчик загруженных документов"""
    document: Document = update.message.document
    file_id = document.file_id
    file_name = document.file_name

    # Скачиваем файл
    file = await context.bot.get_file(file_id)
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    await file.download_to_drive(file_path)

    # Отправляем файл в ChromaDB
    try:
        success = index_document(file_path, file_id=hash(file_name))  # Генерируем file_id из имени файла
        if success:
            await update.message.reply_text(f"Файл {file_name} загружен и проиндексирован!")
        else:
            await update.message.reply_text(f"Не удалось проиндексировать файл {file_name}.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке файла: {str(e)}")


from telegram.constants import ParseMode  # импорт, если ещё не добавил

async def list_files(update: Update, context: CallbackContext):
    file_info = list_indexed_files()
    if not file_info:
        await update.message.reply_text("Нет загруженных файлов.")
        return

    message = "📂 *Загруженные файлы:*\n"
    for (fid, fname), count in file_info.items():
        message += f"• `{fname}`\n  file\\_id: `{str(fid)}` — {count} чанков\n\n"

    await update.message.reply_text(message, parse_mode="MarkdownV2")




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
    session_id = str(update.effective_user.id)
    await update.message.reply_text(f"🆔 Твой session_id: `{session_id}`")


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
    new_session = str(uuid.uuid4())
    user_sessions[user_id] = new_session
    await update.message.reply_text(f"✅ Создан новый диалог.\nТекущий session_id: `{new_session}`")


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

    await update.message.reply_text(message, parse_mode="MarkdownV2")


def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("delete", delete))  
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("session_id", session_id_cmd))
    app.add_handler(CommandHandler("newchat", newchat))
    app.add_handler(CommandHandler("switch", switch))
    app.add_handler(CommandHandler("sessions", sessions))



    # Обработка сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Обработка загружаемых файлов
    

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
