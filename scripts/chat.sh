#!/bin/bash

read -p ">> " prompt
response=$(curl -s -X 'POST' 'http://127.0.0.1:8000/chat' \
     -H 'Content-Type: application/json' \
     -d "{\"question\": \"$prompt\", \"session_id\": \"\", \"model\": \"denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest\"}")

echo "$response" | jq -r '.answer'  # jq нужен для форматирования вывода

