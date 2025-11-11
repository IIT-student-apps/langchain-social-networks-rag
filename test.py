# test.py
import os
import sys
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path (если нужно, но обычно не требуется)
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Текущая директория: {os.getcwd()}")
print(f"Корень проекта: {project_root}")
print(f"Файлы в корне: {os.listdir('.')[:10]}...")  # Первые 10 файлов

# Загружаем .env
load_dotenv()

# Проверяем переменные VK
required_vars = ["VK_PEER_ID", "VK_OWNER_ID", "VK_POST_ID", "VK_ACCESS_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Отсутствуют переменные в .env: {', '.join(missing_vars)}")
    print("Заполни .env и перезапусти.")
    exit(1)
print("✅ Переменные VK найдены")

# Тест импорта vkapi (прямо)
try:
    import vkapi
    print("✅ Импорт vkapi.py успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта vkapi: {e}")
    exit(1)

# Тест импорта tools
try:
    from tools.vk_tools import collect_chat_history, collect_comments
    print("✅ Импорт tools.vk_tools успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта tools: {e}")
    # Дополнительная диагностика
    print(f"Содержимое tools/: {os.listdir('tools') if os.path.exists('tools') else 'Папка tools не найдена'}")
    exit(1)

# Тест выполнения тулов (с коротким выводом)
print("\n=== ТЕСТ ЧАТА ===")
try:
    result = collect_chat_history.invoke({"max_messages": 3})
    print(f"Чат (первые 200 символов): {str(result)[:200]}...")
except Exception as e:
    print(f"Ошибка чата: {e}")

print("\n=== ТЕСТ КОММЕНТАРИЕВ ===")
try:
    result = collect_comments.invoke({"max_comments": 3})
    print(f"Комментарии (первые 200 символов): {str(result)[:200]}...")
except Exception as e:
    print(f"Ошибка комментариев: {e}")