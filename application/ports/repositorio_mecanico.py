from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.mecanico import Mecanico


class RepositorioMecanico(ABC):

    @abstractmethod
    def obtener_por_id(self, mecanico_id: UUID) -> Mecanico | None: ...

    @abstractmethod
    def listar_todos(self) -> list[Mecanico]: ...
