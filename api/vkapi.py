import requests
import json
import conversation
import os
from dotenv import load_dotenv

def get_vk_chat_history(peer_id, access_token):
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/messages.getHistory"
    query_params = {
        "v": "5.251",
        "client_id": "6287487"
    }

    # Данные для тела запроса 
    form_data = {
        "peer_id": peer_id,
        "start_cmid": 813723,
        "count": 90,
        "offset": -24,
        "extended": 1,
        "group_id": 0,
        "fwd_extended": 1,
        "fields": "id,first_name,last_name",
        "access_token": access_token
    }

    # Заголовки из запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
        "Referer": "https://vk.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            params=query_params,
            data=form_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе для peer_id {peer_id}: {str(e)}")
        return None

load_dotenv()
# Пример использования
ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
#CHAT_ID = os.getenv("VK_PEER_ID")
#токен вк(можно найти открыв код страницы с диалогом в браузере->network->ищем access_token в самом низу)
#ACCESS_TOKEN = "vk1.a.GsZMjsrWVoll_DfyS3YnmR2tQzqOSYPZ3BHYREgIvHoHKRfWxExKA3y8uMXpZMtJUxiy4-osGo4vsppnMAUyZ0VZ1bsSglMH40ezSuq11mr948nDLUnpfn4kMw5g6dlosmVa7tEpRg1grVM54iRC-7tRtamQgNR2PiYLkZoQHChT93drLVQYO6zqwvOuTZwmvacqqGmqAGK2r8tXM_-YHw"  
#айди диалога(можно найти открыв код страницы с диалогом в браузере->network->ищем peer_id)
CHAT_ID = os.getenv("VK_PEER_ID")

def get_vk_post_reactions(domain, access_token):
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/wall.get"

    # Данные для тела запроса 
    form_data = {
        "domain": domain, #Короткий адрес пользователя или сообщества.
        "offset": 0,
        "count": 32,
        "filter": "owner",
        "extended": 0,
        "fields": "id,owner_id,date,comments,likes,reposts,views",
        "access_token": access_token,
        "v": "5.251",
    }

    # Заголовки из запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
        "Referer": "https://vk.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            data=form_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе для domain {domain}: {str(e)}")
        return None

def get_vk_subscriptions(user_id, access_token):
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/groups.get"

    # Данные для тела запроса 
    form_data = {
        "v": "5.251",
        "user_id": user_id, #Идентификатор пользователя, информацию о сообществах которого требуется получить.
        "count": 30,
        "extended": 1,
        "offset": 0,
        "filter": "groups",
        "fields": "description,members_count,name",
        "access_token": access_token
    }

    # Заголовки из запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
        "Referer": "https://vk.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            data=form_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе для user_id {user_id}: {str(e)}")
        return None

def get_vk_q_and_a(owner_id, post_id, access_token):
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/wall.getComments"
    # Данные для тела запроса 
    form_data = {
        "owner_id": owner_id, #Идентификатор владельца страницы (пользователь или сообщество).
        "post_id": post_id, #Идентификатор записи на стене.
        "count": 100,
        "extended": 1,
        "need_likes": 1, 
        "sort": "desc",
        "fields": "name",
        "access_token": access_token,
        "v": "5.251",
    }

    # Заголовки из запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
        "Referer": "https://vk.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            data=form_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе для owner_id {owner_id}: {str(e)}")
        return None

def get_vk_newsfeed(owner_id, access_token):
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/newsfeed.getRecommended"
    query_params = {
        "v": "5.251"
    }

    # Данные для тела запроса 
    form_data = {
        "fields": "name",
        "access_token": access_token
    }

    # Заголовки из запроса
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
        "Referer": "https://vk.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            url,
            params=query_params,
            data=form_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе для owner_id {owner_id}: {str(e)}")
        return None



chat = None
result = get_vk_chat_history(CHAT_ID, ACCESS_TOKEN)
#print(result)

#chat = conversation.parse_vk_messages(result)
#prompt = None
#print(chat)

#if chat:
#    prompt = conversation.conversation_to_prompt(chat, "Перескажи данный диалог")

#print(prompt)