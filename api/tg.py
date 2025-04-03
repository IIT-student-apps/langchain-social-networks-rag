import logging
import requests
import os
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain_utils import get_rag_chain
from chroma_utils import index_document_to_chroma as index_document  # Функция для индексирования файла в ChromaDB


# Настройки
TELEGRAM_TOKEN = "7898053052:AAHsk1T7QlW50GLK2pPXc0ZJ0UvoF3eBfhk"
DOWNLOAD_FOLDER = "/home/renat/KP/rag/RAG/rag_files"

# Загружаем RAG-модель
rag_chain = get_rag_chain()

# Логирование
logging.basicConfig(level=logging.INFO)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение"""
    await update.message.reply_text("Привет! Загрузи документ или задай вопрос, и я помогу!")

async def chat(update: Update, context: CallbackContext):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text

    # Запрашиваем ответ через RAG
    response = rag_chain.invoke({"input": user_text, "chat_history": []})

    await update.message.reply_text(response["answer"])

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


def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # Обрабатываем документы

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
