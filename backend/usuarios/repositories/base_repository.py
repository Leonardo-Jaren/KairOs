from typing import TypeVar, Generic, List, Optional
from django.db.models import Model

T = TypeVar('T',bound=Model)

class BaseRepository(Generic[T]):
    "Repositorio base"
    
    def __init__(self, model: type[T]):
        self.model = model
        
    def get_all(self) -> List[T]:
        return self.model.objects.all()
    
    def get_by_id(self, id: int) -> Optional[T]:
        return self.model.objects.filter(pk=id).first()
    
    def delete(self, instance: T) -> None:
        instance.delete()