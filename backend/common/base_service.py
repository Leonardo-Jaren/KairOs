from typing import Any

from django.db.models import QuerySet

from .base_repository import BaseRepository


class BaseService:
    repository: BaseRepository = None

    def get_all(self) -> QuerySet:
        return self.repository.get_all()

    def get_by_id(self, id: int) -> Any:
        instance = self.repository.get_by_id(id)
        if instance is None:
            raise self._not_found_error(id)
        return instance

    def create(self, data: dict) -> Any:
        return self.repository.create(**data)

    def update(self, id: int, data: dict) -> Any:
        instance = self.get_by_id(id)
        return self.repository.update(instance, **data)

    def delete(self, id: int) -> None:
        instance = self.get_by_id(id)
        self.repository.delete(instance)

    def _not_found_error(self, id: int):
        from django.core.exceptions import ValidationError
        return ValidationError(f"Object with id {id} not found.")
