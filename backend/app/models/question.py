import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table: Question <-> Tag (many-to-many)
question_tags = Table(
    "question_tags",
    Base.metadata,
    Column("question_id", UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    body = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="open", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="questions")
    category = relationship("Category", back_populates="questions")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions")
    comments = relationship("Comment", back_populates="question", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="question", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="question", cascade="all, delete-orphan")
