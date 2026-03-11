"""VK API Data Models - Consolidated data structures for VK entities"""
import datetime
from typing import List


# ==================== MESSAGES / CONVERSATION ====================

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
    """Parse VK API chat messages into Conversation object"""
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
    """Convert Conversation to LLM prompt"""
    messages_text = "\n".join(
        [f"{msg.author_first_name} {msg.author_last_name}: {msg.text}" for msg in conversation.messages]
    )
    return f"Вот переписка:\n{messages_text}\n\n{question}"


# ==================== COMMENTS ====================

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
    """Parse VK API comments into CommentThread object"""
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
    """Convert CommentThread to LLM prompt"""
    comments_text = "\n\n".join(
        f"[{comment.author_name}]\n"
        f"{comment.text}\n"
        f"Лайков: {comment.likes}"
        for comment in thread.comments
    )
    return f"Обсуждение поста:\n\n{comments_text}\n\n{question}"


# ==================== POSTS ====================

class Post:
    def __init__(self, owner_id: int, post_id: int, text: str, 
                 likes: int, comments: int, reposts: int, views: int):
        self.owner_id = owner_id
        self.post_id = post_id
        self.text = text
        self.likes = likes
        self.comments = comments
        self.reposts = reposts
        self.views = views


class PostList:
    def __init__(self, posts: List[Post]):
        self.posts = posts


def parse_vk_posts(vk_json: dict, post_number: int = -1) -> PostList:
    """Parse VK API posts into PostList object"""
    posts_data = vk_json.get("response", {}).get("items", [])
    posts = []
    
    for post in posts_data:
        postText = ""

        if post.get("text", "") != "":
            postText = post.get("text", "")
        elif len(post.get("header", {}).get("descriptions", [])) != 0:
            postText = post.get("header", {}).get("descriptions", [])[0].get("text", {}).get("text", "")

        postObj = Post(
            owner_id=post.get("owner_id", 0),
            post_id=post.get("id", 0),
            text=postText,
            likes=post.get("likes", {}).get("count", 0),
            comments=post.get("comments", {}).get("count", 0),
            reposts=post.get("reposts", {}).get("count", 0),
            views=post.get("views", {}).get("count", 0)
        )

        if postObj.text == "":
            continue

        posts.append(postObj)
    
    return PostList(posts[:post_number] if post_number > 0 else posts)


def posts_to_prompt(post_list: PostList, question: str) -> str:
    """Convert PostList to LLM prompt"""
    posts_text = "\n\n".join(
        f"[Пост {post.post_id}]\n"
        f"{post.text}\n"
        f"Лайки: {post.likes} | Комментарии: {post.comments} | Репосты: {post.reposts} | Просмотры: {post.views}"
        for post in post_list.posts
    )
    return f"Информация о постах:\n\n{posts_text}\n\n{question}"


# ==================== SUBSCRIPTIONS ====================

class Group:
    def __init__(self, group_id: int, name: str, description: str, 
                 members_count: int):
        self.id = group_id
        self.name = name
        self.description = description
        self.members_count = members_count


class SubscriptionList:
    def __init__(self, groups: List[Group]):
        self.groups = groups


def parse_vk_subscriptions(vk_json: dict, group_number: int = -1) -> SubscriptionList:
    """Parse VK API subscriptions into SubscriptionList object"""
    groups_data = vk_json.get("response", {}).get("items", [])
    groups = []
    
    for group in groups_data:
        groups.append(Group(
            group_id=group.get("id", 0),
            name=group.get("name", ""),
            description=group.get("description", "")[:100] + "..." if group.get("description") else "",
            members_count=group.get("members_count", 0),
        ))
    
    return SubscriptionList(groups[:group_number] if group_number > 0 else groups)


def subscriptions_to_prompt(sub_list: SubscriptionList, question: str) -> str:
    """Convert SubscriptionList to LLM prompt"""
    subs_text = "\n\n".join(
        f"[Сообщество {group.name}]\n"
        f"Участников: {group.members_count}\n" 
        f"Описание: {group.description}\n"
        for group in sub_list.groups
    )
    return f"Список подписок:\n\n{subs_text}\n\n{question}"
