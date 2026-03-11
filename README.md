# RAG Social Networks Intelligence Platform 🤖

**Многоагентная система анализа документов и социальных сетей (ВК) с использованием LangChain, LangGraph и современных LLM моделей.**

---

## 📋 Описание

Приложение объединяет:
- **Document RAG** — поиск в загруженных документах (PDF, DOCX, HTML) с AI-контекстом
- **Social Media Analytics** — анализ постов, комментариев, чатов и профилей ВК
- **Multi-Agent System** — специализированные агенты для разных типов анализа
- **Множественные интерфейсы** — REST API, Streamlit UI, Telegram Bot, CLI

### Основные возможности:
✅ Загрузка и индексирование документов (Chroma Vector DB)  
✅ Q&A по загруженным файлам с сохранением контекста диалога  
✅ Анализ постов и метрик ВК (лайки, просмотры, комментарии)  
✅ Анализ обсуждений под постами  
✅ Анализ чатов и истории сообщений  
✅ Анализ профилей и подписок  
✅ Поддержка локальных моделей (Ollama) и облачных API (Groq, OpenAI)  
✅ Асинхронная обработка и параллельное выполнение агентов

---

## 🏗️ Архитектура

```
User Query
    ↓
┌─────────────────────────────────────────────────┐
│         Multi-Agent Orchestrator                │
│  Анализирует запрос и выбирает нужных агентов  │
└────────────────┬────────────────────────────────┘
    ↓            ↓            ↓            ↓
 ┌──────┐   ┌─────────┐  ┌──────────┐  ┌────────────┐
 │ Post │   │ Comment │  │ Profile  │  │   Chat     │
 │Agent │   │ Agent   │  │ Agent    │  │ Agent      │
 └───┬──┘   └────┬────┘  └────┬─────┘  └─────┬──────┘
     │           │           │              │
     └───────────┴───────────┴──────────────┘
            ↓
    ┌──────────────────────────────┐
    │   VK API Tools               │
    │ (сбор данных из ВК)          │
    └──────────────────────────────┘

Document RAG Pipeline:
Document Upload → Chroma Indexing → Vector DB → LLM QA Chain
```

---

## 📁 Структура проекта

```
langchain-social-networks-rag/
├── src/                              # Исходный код приложения
│   ├── core/                         # Основные модули и утилиты
│   │   ├── __init__.py
│   │   ├── config.py                 # Конфигурация LLM моделей
│   │   ├── llm_factory.py            # Фабрика для создания LLM
│   │   ├── models.py                 # VK API data models (consolidated)
│   │   │   ├── Message, Conversation # Сообщения чата
│   │   │   ├── Comment, CommentThread # Комментарии под постами
│   │   │   ├── Post, PostList        # Посты с реакциями
│   │   │   └── Group, SubscriptionList # Подписки пользователя
│   │   ├── db_utils.py               # SQLite операции (логи, история)
│   │   ├── chroma_utils.py           # Операции с Chroma Vector DB
│   │   ├── langchain_utils.py        # RAG цепочка (retriever + LLM)
│   │   └── pydantic_models.py        # API Pydantic схемы
│   │
│   ├── integrations/                 # Интеграции с внешними сервисами
│   │   ├── __init__.py
│   │   ├── vk_client.py              # VK API клиент (прямые вызовы)
│   │   └── telegram_bot.py           # Telegram Bot интерфейс
│   │
│   ├── agents/                       # Специализированные агенты анализа
│   │   ├── __init__.py
│   │   ├── post_analyst.py           # Анализ постов и реакций
│   │   ├── comment_analyst.py        # Анализ комментариев
│   │   ├── profile_analyst.py        # Анализ профилей и подписок
│   │   └── chat_analyst.py           # Анализ чатов
│   │
│   ├── tools/                        # Инструменты для агентов
│   │   ├── __init__.py
│   │   ├── vk_tools.py               # VK API инструменты (7 tools)
│   │   └── llm_tools.py              # LLM анализ инструменты (8 tools)
│   │
│   ├── graph/                        # LangGraph оркестрация
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Выбор агентов по запросу
│   │   └── workflow.py               # Multi-agent State Machine
│   │
│   ├── app/                          # Streamlit веб-интерфейс
│   │   ├── __init__.py
│   │   ├── streamlit_app.py          # Основное приложение
│   │   ├── chat_interface.py         # Компонент чата
│   │   ├── sidebar.py                # Боковое меню
│   │   └── api_utils.py              # Утилиты для API
│   │
│   ├── api/                          # FastAPI REST API
│   │   ├── __init__.py
│   │   └── server.py                 # API endpoints (chat, upload-doc, list-docs, delete-doc)
│   │
│   └── __init__.py
│
├── data/                             # Данные (не коммитятся)
│   ├── chroma_db/                    # Chroma Vector DB (embeddings)
│   └── rag_files/                    # Загруженные документы (PDF, DOCX, HTML)
│
├── database/                         # База данных
│   └── rag_app.db                    # SQLite (логи, история, метаданные)
│
├── scripts/                          # Вспомогательные скрипты
│   └── token_grabber.py              # VK токен автоматизация (Playwright)
│
├── .env                              # Переменные окружения (не коммитятся)
├── .gitignore
├── config.py                         # ⚠️ Устарело - используйте src/core/config.py
├── requirements.txt                  # Python зависимости
├── main.py                           # 🎯 CLI entry point (интерактивный чат)
├── README.md                         # Этот файл
└── tg.py                             # ⚠️ Устарело - используйте src/integrations/telegram_bot.py
```

### Иерархия импортов (от низкого к высокому уровню)

```
Layer 1: Core Utilities (No dependencies)
  ├── src/core/config.py
  ├── src/core/models.py
  ├── src/core/pydantic_models.py
  └── src/core/db_utils.py

Layer 2: LLM & Vector DB
  ├── src/core/llm_factory.py → config
  ├── src/core/chroma_utils.py
  └── src/core/langchain_utils.py

Layer 3: API Integrations
  └── src/integrations/vk_client.py → models

Layer 4: Tools & Wrappers
  ├── src/tools/vk_tools.py → vk_client + models
  └── src/tools/llm_tools.py → llm_factory

Layer 5: Agents
  └── src/agents/*.py → tools + llm_factory

Layer 6: Orchestration
  ├── src/graph/orchestrator.py → llm_factory
  └── src/graph/workflow.py → agents + orchestrator

Layer 7: Applications
  ├── src/api/server.py → core utils
  ├── src/app/*.py → (self-contained)
  ├── src/integrations/telegram_bot.py → all layers
  └── main.py → core utils
```

---

## ⚙️ Зависимости

### Основной стек:
- **LangChain** — оркестрация LLM и RAG
- **LangGraph** — workflow и мультиагентные системы
- **Chroma** — векторная база данных (embeddings)
- **Ollama** — локальные LLM модели
- **Groq API** — облачные модели (Qwen3, Kimi)
- **FastAPI + Uvicorn** — REST API
- **Streamlit** — веб-интерфейс
- **python-telegram-bot** — Telegram Bot

See `requirements.txt` для полного списка.

---

## 🚀 Установка и запуск

### Windows

#### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 2. Установка Ollama и моделей
```bash
pip install ollama

# Загрузить модель для embeddings
ollama pull denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m

# Или используйте другую модель, например:
ollama pull qwen3:8b
```

#### 4. Настройка переменных окружения
Создайте файл `.env` в корневой папке:
```env
# LLM API ключи
GROQ=your_groq_api_key
OPENAI_API_KEY=your_openai_key

# VK API
VK_ACCESS_TOKEN=your_vk_token
VK_CLIENT_ID=your_client_id
VK_USER_ID=your_user_id
VK_OWNER_ID=your_group_id (для анализа группы)
VK_POST_ID=specific_post_id (для анализа поста)
VK_PEER_ID=chat_peer_id (для анализа чата)
VK_COUNT=number_of_messages

# Telegram Bot
TELEGRAM_TOKEN=your_telegram_bot_token

# Database paths (optional)
DB_PATH=database/rag_app.db
CHROMA_DB_PATH=data/chroma_db
```

#### 5. Запуск FastAPI сервера
```bash
cd src/api
uvicorn server:app --reload
```
API доступен на `http://127.0.0.1:8000`

#### 6. Запуск интерфейса (выберите один)

**CLI интерактивный чат:**
```bash
python main.py
```

**Streamlit Web UI:**
```bash
streamlit run src/app/streamlit_app.py
```

**Telegram Bot:**
```bash
python src/integrations/telegram_bot.py
```

---

### Linux/Ubuntu

#### 1. Установка Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &  # В отдельной сессии
```

#### 2. Загрузка моделей
```bash
ollama pull denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m
```

#### 3. Установка зависимостей Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Настройка `.env` (см. Windows инструкции выше)

#### 5. Запуск FastAPI
```bash
cd src/api
uvicorn server:app --reload
```

#### 6. Запуск интерфейса (в отдельной сессии)
```bash
source venv/bin/activate
python3 main.py  # CLI
# или
streamlit run src/app/streamlit_app.py  # Web UI
# или
python3 src/integrations/telegram_bot.py  # Telegram Bot
```

---

## 📖 Использование

### REST API

#### Отправить запрос к RAG системе
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Анализируй пост и расскажи о реакциях",
    "session_id": "user123"
  }'
```

#### Загрузить документ
```bash
curl -X POST "http://127.0.0.1:8000/upload-doc" \
  -F "file=@my_document.pdf"
```

#### Посмотреть список загруженных документов
```bash
curl -X GET "http://127.0.0.1:8000/list-docs"
```

#### Удалить документ
```bash
curl -X DELETE "http://127.0.0.1:8000/delete-doc" \
  -H "Content-Type: application/json" \
  -d '{"file_id": 1}'
```

### Telegram Bot Команды

| Команда | Описание |
|---------|---------|
| Отправить файл | Загрузить PDF/DOCX в базу знаний |
| `/list` | Показать список загруженных файлов |
| `/delete <id>` | Удалить файл по индексу |
| `/history` | Показать историю диалога |
| `/reset` | Очистить историю |
| Обычное сообщение | Запрос к RAG системе |

### Streamlit UI

- **Боковое меню:** выбор модели, загрузка документов, управление файлами
- **Основной чат:** интерактивное взаимодействие с системой
- **История:** сохраняется в сессии

---

---

## 🔄 Миграция проекта (v0.1)

**Старая структура → Новая структура**

| Старо | Ново | Причина |
|-------|------|---------|
| `conversation.py` | `src/core/models.py` | Консолидация VK data models |
| `comments.py` | `src/core/models.py` | Консолидация VK data models |
| `posts.py` | `src/core/models.py` | Консолидация VK data models |
| `subscriptions.py` | `src/core/models.py` | Консолидация VK data models |
| `config.py` | `src/core/config.py` | Переместить в core |
| `llm_factory.py` | `src/core/llm_factory.py` | Переместить в core |
| `langchain_utils.py` | `src/core/langchain_utils.py` | Переместить в core |
| `chroma_utils.py` | `src/core/chroma_utils.py` | Переместить в core |
| `db_utils.py` | `src/core/db_utils.py` | Переместить в core |
| `pydantic_models.py` | `src/core/pydantic_models.py` | Переместить в core |
| `vkapi.py` | `src/integrations/vk_client.py` | Переместить в integrations |
| `tg.py` | `src/integrations/telegram_bot.py` | Переместить в integrations |
| `api/main.py` | `src/api/server.py` | Переместить в src/api |
| `agents/` | `src/agents/` | Переместить в src |
| `tools/` | `src/tools/` | Переместить в src |
| `graph/` | `src/graph/` | Переместить в src |
| `app/` | `src/app/` | Переместить в src |
| `chroma_db/` | `data/chroma_db/` | Разделить код и данные |
| `rag_files/` | `data/rag_files/` | Разделить код и данные |
| `rag_app.db` | `database/rag_app.db` | Разделить код и данные |
| `main.py` | `main.py` + `src/api/server.py` | Разделить CLI и API |
| `token_grabber.py` | `scripts/token_grabber.py` | Переместить вспомогательные скрипты |

### Преимущества новой структуры

✅ **Модульность** - Четкое разделение кода, интеграций и приложений  
✅ **Масштабируемость** - Легко добавлять новых агентов, инструментов, интеграций  
✅ **Maintainability** - Понятная иерархия импортов, меньше circular dependencies  
✅ **Data/Code separation** - Папка `data/` и `database/` изолированы  
✅ **CLI + API** - `main.py` для интерактивного использования, `server.py` для production  

---

## 🔧 Конфигурация

### `src/core/config.py` — Выбор LLM модели

```python
ACTIVE_MODEL = "groq_moonshotai"  # или "groq_qwen", "local_qwen3:8b"

LLM_CONFIGS = {
    "local_qwen3:8b": {
        "provider": "ollama",
        "model": "qwen3:8b",
        "base_url": "http://localhost:11434"
    },
    "groq_qwen": {
        "provider": "groq",
        "model": "qwen3-32b-vision"
    },
    "groq_moonshotai": {
        "provider": "groq",
        "model": "moonshot-ai/kimi-k2-instruct-0905"
    }
}
```

### `src/core/langchain_utils.py` — RAG параметры

```python
CHUNK_SIZE = 1000              # Размер чанка документа (токены)
CHUNK_OVERLAP = 200            # Перекрытие между чанками
EMBEDDING_MODEL = "ollama"     # Provider for embeddings
CHROMA_DB_PATH = "data/chroma_db"  # Vector DB path
```

---

## 🗄️ База данных

**SQLite** (`database/rag_app.db`):
- `application_logs` — логи запросов, ответы моделей, метаданные
- `document_store` — загруженные файлы и метаданные

**Chroma Vector DB** (`data/chroma_db/`):
- Хранит embeddings документов с метаданными (filename, file_id)
- Используется для поиска релевантных фрагментов по запросу

---

## 🔐 Безопасность

⚠️ **Важно:**
- Никогда не коммитьте `.env` файл в репозиторий
- Используйте токены с минимально необходимыми правами
- Для production используйте надежное хранилище секретов (AWS Secrets, HashiCorp Vault и т.д.)
- Валидируйте входные данные перед обработкой

---

## 🐛 Troubleshooting

**Проблема:** Ollama не запускается
```bash
# Windows: установите ollama с https://ollama.ai
# Linux: sudo systemctl start ollama
```

**Проблема:** GROQ API ошибка
```
Убедитесь, что GROQ переменная в .env корректна
```

**Проблема:** VK API ошибка
```
Проверьте VK_ACCESS_TOKEN и права доступа в VK приложении
```

**Проблема:** Chroma не находит документы
```bash
# Пересоздайте index
python -c "from chroma_utils import reset_chroma_db; reset_chroma_db()"
```

---

## 📚 Дополнительные ресурсы

- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Chroma Docs](https://docs.trychroma.com/)
- [Ollama](https://ollama.ai/)
- [VK API](https://dev.vk.com/)

---

## 📝 Лицензия

Проект находится в разработке.

---

**Последнее обновление:** март 2026
