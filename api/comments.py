import datetime
from typing import List


class Comment:
    def __init__(self, author_id: int, author_name: str, 
                 text: str, likes: int):
        self.author_id = author_id
        self.author_name = author_name
        self.text = text
        self.likes = likes

class CommentThread:
    def __init__(self, comments: List[Comment]):
        self.comments = comments

def parse_vk_comments(vk_json: dict, comment_number: int = -1) -> CommentThread:
    comments_data = vk_json.get("response", {}).get("items", [])
    profiles = {p["id"]: f"{p.get('first_name', '')} {p.get('last_name', '')}" 
                for p in vk_json.get("response", {}).get("profiles", [])}
    groups = {g["id"]: g["name"] for g in vk_json.get("response", {}).get("groups", [])}
    
    comments = []
    for comment in comments_data:
        author_id = comment.get("from_id", 0)
        author_name = groups[abs(author_id)] if author_id < 0 else profiles.get(author_id, "Unknown")
        
        comments.append(Comment(
            author_id=author_id,
            author_name=author_name,
            text=comment.get("text", ""),
            likes=comment.get("likes", {}).get("count", 0),
        ))
    
    return CommentThread(comments[:comment_number] if comment_number > 0 else comments)

def comments_to_prompt(thread: CommentThread, question: str) -> str:
    comments_text = "\n\n".join(
        f"[{comment.author_name}]\n"
        f"{comment.text}\n"
        f"Лайков: {comment.likes}"
        for comment in thread.comments
    )
    return f"Обсуждение поста:\n\n{comments_text}\n\n{question}"