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
Вкладка терминала с fastapi должна оставаться открытой. После этого можно открыть новую вкладку и запустить следующие скрипты в зависимости от цели:
1. Общение с моделью:

```
./chat.sh
```
2. Загрузка своего файла:

```
./upload.sh мой_файл.pdf

```
Если успешно загрузился файл, ответ будет каким-то таким:
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
5. Удалить загруженный файл (c указанием индекса файла):
```
./delete.sh 1
```

