import asyncio
from playwright.async_api import async_playwright
import os
from pathlib import Path


import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
from pathlib import Path


ENV_FILE = "D:\RAG\langchain-social-networks-rag\.env"

# Обновление/создание переменной в .env
def update_env_file(key, value):
    updated = False
    lines = []

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break

    if not updated:
        lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ Токен обновлён и записан в .env: {value[:12]}...")

# Основной процесс
async def get_vk_token():
    current_token = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Перехват запроса
        def check_request(request):
            nonlocal current_token
            try:
                json = request.post_data_json
                if "access_token" in json:
                    new_token = json["access_token"]
                    if new_token != current_token:
                        current_token = new_token
                        update_env_file("VK_ACCESS_TOKEN", current_token)
            except:
                pass

        page.on("requestfinished", check_request)

        print("🌐 Открылся браузер. Авторизуйтесь во ВКонтакте.")
        await page.goto("https://vk.com")

        # Цикл слежения за обновлениями
        while True:
            await page.wait_for_timeout(300000)
            await page.goto("https://vk.com/feed")

        await context.close()
        await browser.close()

# Запуск
if __name__ == "__main__":
    asyncio.run(get_vk_token())