#!/bin/bash

if [ -z "$1" ]; then
  echo "Использование: ./delete.sh <file_id>"
  exit 1
fi

FILE_ID=$1

response=$(curl -s -X 'POST' \
  'http://127.0.0.1:8000/delete-doc' \
  -H 'Content-Type: application/json' \
  -d "{\"file_id\": $FILE_ID}")

echo "Ответ сервера:"
echo "$response"

