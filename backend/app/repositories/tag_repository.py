from typing import Optional

from sqlalchemy.orm import Session

from app.models.tag import Tag

class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.name == name).first()

    def list(self) -> list[Tag]:
        return self.db.query(Tag).order_by(Tag.name.asc()).all()

    def get_or_create(self, name: str) -> Tag:
        """Get or create a tag. flush() only assigns the id — commit happens
        in QuestionRepository.create/update, same transaction."""
        tag = self.get_by_name(name)
        if tag is None:
            tag = Tag(name=name)
            self.db.add(tag)
            self.db.flush()
        return tag