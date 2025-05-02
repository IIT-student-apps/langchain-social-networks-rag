"""
import asyncio
from playwright.async_api import async_playwright

# Конфигурационные параметры
TOKEN = '.'

async def get_vk_token():
    global TOKEN
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Обработчик для перехвата запросов
        def check_request(request):
            global TOKEN

            try:
                json = request.post_data_json
                if "access_token" in json:
                    TOKEN = json['access_token']
            except:
                pass

        page.on('requestfinished', check_request)

        # Формируем URL для авторизации
        auth_url = 'https://vk.com/'

        await page.goto(auth_url)

        await page.wait_for_url('https://vk.com/feed')

        #await page.get_by_test_id("search_global_tab_friends").get_by_text("Друзья").click(timeout=60000)

        token = ''
        while True:
            if(token != TOKEN):
                print(TOKEN)
                token = TOKEN
            
            await page.wait_for_timeout(30000)
            await page.goto('https://vk.com/feed')

        context.close()
        browser.close()

asyncio.run(get_vk_token())
"""

import asyncio
from playwright.async_api import async_playwright
import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

async def get_vk_token():
    token_found = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        def check_request(request):
            nonlocal token_found
            try:
                data = request.post_data_json
                if "access_token" in data:
                    token_found = data["access_token"]
            except:
                pass

        page.on("requestfinished", check_request)

        print("🌐 Открылся браузер. Авторизуйся во ВКонтакте...")
        await page.goto("https://vk.com")

        print("🔑 Пожалуйста, войдите в VK. После входа нажмите Enter в консоли...")
        input("⏳ Ожидание входа. Нажмите Enter, когда будете на странице /feed → ")

        # Ждём появления токена
        while not token_found:
            await page.wait_for_timeout(5000)
            await page.goto("https://vk.com/feed")

        print(f"\n✅ Найден access_token:\n{token_found}")

        # Обновляем или создаём .env
        update_env_file("VK_ACCESS_TOKEN", token_found)
        print("💾 Токен сохранён в .env")

        await context.close()
        await browser.close()
        return token_found

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
