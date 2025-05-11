import datetime
from typing import List


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
    posts_text = "\n\n".join(
        f"[Пост {post.post_id}]\n"
        f"{post.text}\n"
        f"Лайки: {post.likes} | Комментарии: {post.comments} | Репосты: {post.reposts} | Просмотры: {post.views}"
        for post in post_list.posts
    )
    return f"Информация о постах:\n\n{posts_text}\n\n{question}"
        
