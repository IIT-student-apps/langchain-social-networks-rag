#!/bin/bash

if [ -z "$1" ]; then
  echo "Использование: ./upload.sh <путь_к_файлу>"
  exit 1
fi

FILE=$1

if [ ! -f "$FILE" ]; then
  echo "Ошибка: файл '$FILE' не найден!"
  exit 1
fi

response=$(curl -s -X 'POST' \
  'http://127.0.0.1:8000/upload-doc' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@$FILE")

echo "Ответ сервера:"
echo "$response"

