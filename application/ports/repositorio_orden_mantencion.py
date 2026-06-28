from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.orden_mantencion import OrdenMantencion
from domain.value_objects.estado_orden import EstadoOrden


class RepositorioOrdenMantencion(ABC):

    @abstractmethod
    def guardar(self, orden: OrdenMantencion) -> None: ...

    @abstractmethod
    def obtener_por_id(self, orden_id: UUID) -> OrdenMantencion | None: ...

    @abstractmethod
    def listar_por_estado(self, estado: EstadoOrden) -> list[OrdenMantencion]: ...

    @abstractmethod
    def listar_por_cliente(self, cliente_id: UUID) -> list[OrdenMantencion]: ...

    @abstractmethod
    def listar_por_mecanico(self, mecanico_id: UUID) -> list[OrdenMantencion]: ...
