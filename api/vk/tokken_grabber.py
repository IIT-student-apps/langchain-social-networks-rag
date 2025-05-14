from playwright.async_api import async_playwright
import logging

import os
from pathlib import Path

#ENV_FILE = Path(__file__).resolve().parents[1] / ".env"  #<----------------------------

# Глобальное состояние
class TokenState:
    def __init__(self):
        self.token = None
        self.task = None
        self.browser = None
        self.page = None
        self.running = False

state = TokenState()

async def token_updater():
    global state
    
    try:
        async with async_playwright() as p:
            state.browser = await p.chromium.launch(headless=False)
            context = await state.browser.new_context()
            state.page = await context.new_page()


            def check_request(request):
                try:
                    if request.method == "POST" and "access_token" in (request.post_data or ""):
                        state.token = request.post_data_json.get('access_token')

                        #update_env_file("VK_ACCESS_TOKEN", state.token) #<---------------------------- Пока не использую

                        logging.info(f"Токен обновлен: {state.token}")
                except Exception as e:
                    logging.error(f"Ошибка при обработке запроса: {e}")

            state.page.on('requestfinished', check_request)
            
            await state.page.goto('https://vk.com/')
            await state.page.wait_for_url('https://vk.com/feed')

            while state.running:
                try:
                    await state.page.wait_for_timeout(30000)
                    await state.page.reload()
                except Exception as e:
                    logging.error(f"Ошибка в основном цикле: {e}")
                    break

    except Exception as e:
        logging.error(f"Ошибка в фоновой задаче: {e}")
    finally:
        if state.browser:
            await state.browser.close()
        state.running = False
        state.task = None
        state.browser = None
        state.page = None




# def update_env_file(key, value):  #<----------------------------
#     updated = False
#     lines = []

#     if os.path.exists(ENV_FILE):
#         with open(ENV_FILE, "r", encoding="utf-8") as f:
#             lines = f.readlines()

#         for i, line in enumerate(lines):
#             if line.startswith(f"{key}="):
#                 lines[i] = f"{key}={value}\n"
#                 updated = True
#                 break

#     if not updated:
#         lines.append(f"{key}={value}\n")

#     with open(ENV_FILE, "w", encoding="utf-8") as f:
#         f.writelines(lines)