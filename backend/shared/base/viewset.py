from typing import Any

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .service import BaseService
from ..utils import parse_boolean, parse_integer


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseViewSet(viewsets.ModelViewSet):
    service: BaseService = None
    serializer_class = None
    pagination_class = BasePagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        return self.serializer_class

    def get_collection_response(self, queryset) -> Response:
        """Serializa una colección aplicando la paginación estándar."""
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def parse_boolean_query(value: str | None) -> bool | None:
        return parse_boolean(value)

    @staticmethod
    def parse_integer_query(value: str | None) -> int | None:
        return parse_integer(value)

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.service.get_all()
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        try:
            instance = self.service.get_by_id(kwargs['pk'])
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data)
        output = self.get_serializer(instance)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        try:
            instance = self.service.get_by_id(kwargs['pk'])
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data)
        output = self.get_serializer(updated)
        return Response(output.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        try:
            self.service.delete(kwargs['pk'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
