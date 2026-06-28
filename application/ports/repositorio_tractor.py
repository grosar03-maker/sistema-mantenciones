from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.tractor import Tractor
from domain.entities.modelo import Modelo


class RepositorioTractor(ABC):

    @abstractmethod
    def guardar(self, tractor: Tractor) -> None: ...

    @abstractmethod
    def obtener_por_id(self, tractor_id: UUID) -> Tractor | None: ...

    @abstractmethod
    def obtener_por_numero_serie(self, numero_serie: str) -> Tractor | None: ...

    @abstractmethod
    def obtener_modelo_por_numero_serie(self, numero_serie: str) -> Modelo | None: ...
