"""Core modules - configuration, utilities, and models"""
from .config import ACTIVE_MODEL, LLM_CONFIGS
from .llm_factory import get_llm
from .models import (
    Message, Conversation, parse_vk_messages, conversation_to_prompt,
    Comment, CommentThread, parse_vk_comments, comments_to_prompt,
    Post, PostList, parse_vk_posts, posts_to_prompt,
    Group, SubscriptionList, parse_vk_subscriptions, subscriptions_to_prompt
)

__all__ = [
    "ACTIVE_MODEL", "LLM_CONFIGS", "get_llm",
    "Message", "Conversation", "parse_vk_messages", "conversation_to_prompt",
    "Comment", "CommentThread", "parse_vk_comments", "comments_to_prompt",
    "Post", "PostList", "parse_vk_posts", "posts_to_prompt",
    "Group", "SubscriptionList", "parse_vk_subscriptions", "subscriptions_to_prompt"
]
