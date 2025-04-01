# langchain-social-networks-rag

## Установка

 Для начала стоит установить ollama и LLM для проекта:
 
```
chmod +x install_ollama_and_yandex.sh
./install_ollama_and_yandex.sh
```
Процесс займёт какое-то время

Дальше идёт установка основных библиотек:

```
chmod +x setup.sh
./setup.sh
```

После этого запускается fastapi:
```
chmod +x runfastapi.sh
./runfastapi.sh
```

## Работа с программой
Вкладка терминала с fastapi должна оставаться открытой. После этого можно открыть новую вкладку и писать следующее в зависимости от цели:
1. Проверка чата:

```
curl -X 'POST' 'http://127.0.0.1:8000/chat' \
     -H 'Content-Type: application/json' \
     -d '{"question": "Привет, как дела?", "session_id": "", "model": "denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest"}'
```
2. Загрузка своего файла:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/upload-doc' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@твой_файл.pdf'
```
Если успешно загрузился файл, ответ будет таким:
```
{
  "message": "File твой_файл.pdf has been successfully uploaded and indexed.",
  "file_id": 1
}
```

4. Проверка списка загруженных файлов:
```
curl -X 'GET' 'http://127.0.0.1:8000/list-docs'
```
5. Удалить загруженный файл:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/delete-doc' \
  -H 'Content-Type: application/json' \
  -d '{
    "file_id": 1
  }'
```

