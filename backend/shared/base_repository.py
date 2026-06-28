from django.db.models import Model, QuerySet


class BaseRepository:
    model: type[Model] = None

    def get_all(self) -> QuerySet:
        return self.model.objects.all()

    def get_by_id(self, id: int) -> Model | None:
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs) -> Model:
        return self.model.objects.create(**kwargs)

    def update(self, instance: Model, **kwargs) -> Model:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance: Model) -> None:
        instance.delete()

    def filter(self, **filters) -> QuerySet:
        return self.model.objects.filter(**filters)

    def exists(self, **filters) -> bool:
        return self.model.objects.filter(**filters).exists()

    def count(self) -> int:
        return self.model.objects.count()
