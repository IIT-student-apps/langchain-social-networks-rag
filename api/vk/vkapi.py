import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ID Пользователя по короткому имени
def get_vk_profile(access_token, screen_name):
    #print(screen_name)
    try:
        response = requests.get(
            "https://api.vk.com/method/users.get",
            params={"access_token": access_token, "user_ids": screen_name, "v": "5.199"}
        ).json()
    #print(response)

        return response["response"][0]
    except Exception as e:
        print(f"Ошибка при запросе для {screen_name}: {str(e)}")
        return None

def get_all_vk_chat(access_token):
    # Если понадобится обыскать все чаты

    dialogs = requests.get(
        "https://api.vk.com/method/messages.getConversations",
        params={"access_token": access_token, "v": "5.199"}
    ).json()

    print("Диалоги:", dialogs["response"][0])


def get_vk_chat(access_token,user_id):

    try:
        response = requests.get(
            "https://api.vk.com/method/messages.getHistory",
            params={"access_token": access_token, "peer_id": user_id, "count": 50, "v": "5.199"},
        ).json()

        return response
    except Exception as e:
        print(f"Ошибка при загрузке чата с  peer_id {user_id}: {str(e)}")
        return None



# Данные пользователя
def get_self_vk_profile(access_token):
    
    try:
        response = requests.get(
            "https://api.vk.com/method/users.get",
            params={"access_token": access_token, "v": "5.199"}
        ).json()

        return response["response"][0]
    except Exception as e:
        print(f"Ошибка получения профиля по токену доступа {access_token}: {str(e)}")
        return None

# НИЖЕ СТАРЫЙ КОД



















#НЕ МОЁ ЭДИШН
# Метод для пересказа диалога
def get_vk_chat_history(peer_id, access_token):
    load_dotenv(override=True)
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/messages.getHistory"
    query_params = {
        "v": "5.251",
        "client_id": os.getenv("VK_CLIENT_ID")
    }

    # Данные для тела запроса 
    form_data = {
        "peer_id": os.getenv("VK_PEER_ID"),
        "start_cmid": os.getenv("VK_START_CMID"),
        "count": int(os.getenv("VK_COUNT", 10)),
        "offset": -1,
        "extended": 1,
        "group_id": 0,
        "fwd_extended": 1,
        "fields": "id,first_name,last_name",
        "access_token": os.getenv("VK_ACCESS_TOKEN")
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


# Метод для получения постов, которые вызвали наибольшую реакцию
def get_vk_post_reactions(owner_id, access_token):
    load_dotenv(override=True)
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/wall.get"

    # Данные для тела запроса 
    form_data = { 
        "domain": os.getenv("VK_OWNER_ID"), #Короткий адрес пользователя или сообщества. 
        "offset": 0, 
        "count": int(os.getenv("VK_COUNT", 10)), 
        "filter": "all", 
        "extended": 0, 
        "fields": "id,owner_id,date,comments,likes,reposts,views", 
        "access_token": os.getenv("VK_ACCESS_TOKEN"), 
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
        print(f"Ошибка при запросе для domain {owner_id}: {str(e)}")
        return None

# Метод для описания личности пользователя по его подпискам на сообщества
def get_vk_subscriptions(user_id, access_token):
    load_dotenv(override=True)
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/groups.get"

    # Данные для тела запроса 
    form_data = {
        "v": "5.251",
        "user_id": os.getenv("VK_USER_ID"), #Идентификатор пользователя, информацию о сообществах которого требуется получить.
        "count": int(os.getenv("VK_COUNT", 10)),
        "extended": 1,
        "offset": 0,
        "filter": "groups",
        "fields": "description,members_count,name",
        "access_token": os.getenv("VK_ACCESS_TOKEN")
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

# Метод для получения часто задаваемых вопросов под конкретным постом
def get_vk_q_and_a(owner_id, post_id, access_token):
    load_dotenv(override=True)
    # URL и параметры строки запроса
    url = "https://api.vk.com/method/wall.getComments"
    # Данные для тела запроса 
    form_data = {
        "owner_id": os.getenv("VK_OWNER_ID"), #Идентификатор владельца страницы (пользователь или сообщество).
        "post_id": os.getenv("VK_POST_ID"), #Идентификатор записи на стене.
        "count": int(os.getenv("VK_COUNT", 10)),
        "extended": 1,
        "need_likes": 1, 
        "sort": "desc",
        "fields": "name",
        "access_token": os.getenv("VK_ACCESS_TOKEN"),
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


chat = None
result = get_vk_chat_history(os.getenv("VK_PEER_ID"), os.getenv("VK_ACCESS_TOKEN"))
