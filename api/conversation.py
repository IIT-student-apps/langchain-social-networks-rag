import json
from typing import List

class Message:
    def __init__(self, author_id: int, author_first_name: str, author_last_name: str, text: str):
        self.author_id = author_id
        self.author_first_name = author_first_name
        self.author_last_name = author_last_name
        self.text = text
    
    def __repr__(self):
        return f"Message({self.author_id}, {self.author_first_name} {self.author_last_name}, '{self.text}')"

class Conversation:
    def __init__(self, messages: List[Message]):
        self.messages = messages
    
    def __repr__(self):
        return f"Conversation({len(self.messages)} messages)"


def parse_vk_messages(vk_json: dict, msg_number: int = -1) -> Conversation:
    messages_data = vk_json.get("response", {}).get("items", [])
    profiles = {p["id"]: (p["first_name"], p["last_name"]) for p in vk_json.get("response", {}).get("profiles", [])}
    
    messages = []
    for msg in messages_data:
        author_id = msg["from_id"]
        author_name = profiles.get(author_id, ("Unknown", "Unknown"))
        
        if msg["text"]:  # Пропускаем сообщения без текста
            messages.append(Message(author_id, author_name[0], author_name[1], msg["text"]))
    
    if msg_number > 0:
        messages = messages[-msg_number:]
    
    return Conversation(list(reversed(messages)))


def conversation_to_prompt(conversation: Conversation, question: str) -> str:
    messages_text = "\n".join(
        [f"{msg.author_first_name} {msg.author_last_name}: {msg.text}" for msg in conversation.messages]
    )
    return f"Вот переписка:\n{messages_text}\n\n{question}"