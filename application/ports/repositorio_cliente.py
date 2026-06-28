from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.cliente import Cliente


class RepositorioCliente(ABC):

    @abstractmethod
    def guardar(self, cliente: Cliente) -> None: ...

    @abstractmethod
    def obtener_por_id(self, cliente_id: UUID) -> Cliente | None: ...

    @abstractmethod
    def obtener_por_email(self, email: str) -> Cliente | None: ...
