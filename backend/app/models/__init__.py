# app/models/__init__.py
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.question import Question, question_tags
from app.models.comment import Comment
from app.models.like import Like
from app.models.bookmark import Bookmark
from app.models.follow import Follow

__all__ = [
    "Role",
    "User",
    "Category",
    "Tag",
    "Question",
    "question_tags",
    "Comment",
    "Like",
    "Bookmark",
    "Follow",
]
