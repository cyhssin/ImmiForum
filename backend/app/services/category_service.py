from uuid import UUID

from fastapi import HTTPException, status

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db):
        self.category_repo = CategoryRepository(db)

    def list_categories(self) -> list[Category]:
        return self.category_repo.list()

    def create(self, data: CategoryCreate) -> Category:
        name = data.name.strip()
        if self.category_repo.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists",
            )
        return self.category_repo.create(
            Category(name=name, description=data.description)
        )

    def update(self, category_id: UUID, data: CategoryUpdate) -> Category:
        category = self._get_or_404(category_id)
        changes = data.model_dump(exclude_unset=True)

        if "name" in changes:
            name = changes["name"].strip()
            existing = self.category_repo.get_by_name(name)
            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category already exists",
                )
            category.name = name
        if "description" in changes:
            category.description = changes["description"]

        return self.category_repo.update(category)

    def delete(self, category_id: UUID) -> None:
        category = self._get_or_404(category_id)
        # Questions survive with category_id = NULL (FK ON DELETE SET NULL)
        self.category_repo.delete(category)

    def _get_or_404(self, category_id: UUID) -> Category:
        category = self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        return category