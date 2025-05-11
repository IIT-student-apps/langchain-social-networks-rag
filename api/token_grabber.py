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

        print("🌐 Открылся браузер. Авторизуйся во ВКонтакте (есть 60 секунд)...")
        await page.goto("https://vk.com")

        # Даём пользователю 60 секунд на авторизацию вручную
        await page.wait_for_timeout(60_000)

        print("⏳ Начинаем слушать токен...")

        # Попытки найти токен в течение 30 секунд (обновляя страницу каждые 5 сек)
        for _ in range(6):
            if token_found:
                break
            await page.goto("https://vk.com/feed")
            await page.wait_for_timeout(5000)

        if token_found:
            print(f"\n✅ Найден access_token:\n{token_found}")
            update_env_file("VK_ACCESS_TOKEN", token_found)
            print("💾 Токен сохранён в .env")
        else:
            print("❌ Токен не найден. Попробуй снова.")

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
