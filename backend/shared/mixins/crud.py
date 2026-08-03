from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


class SoftDeleteMixin:
    """Añade eliminación lógica a un BaseRepository con campos is_deleted/updated_by."""

    def soft_delete(self, instance, actor) -> None:
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])


class ActorCRUDMixin:
    """Sobreescribe create/update/destroy para pasar actor=request.user al servicio."""

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(self.get_serializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
