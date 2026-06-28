from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.catalogo_repuestos import CatalogoRepuestos
from domain.entities.modelo import Modelo
from domain.value_objects.tipo_mantencion import TipoMantencion


class RepositorioCatalogoRepuestos(ABC):

    @abstractmethod
    def guardar(self, catalogo: CatalogoRepuestos) -> None: ...

    @abstractmethod
    def obtener_por_modelo_y_mantencion(
        self, modelo: Modelo, tipo_mantencion: TipoMantencion
    ) -> CatalogoRepuestos | None: ...

    @abstractmethod
    def listar_por_modelo(self, modelo_id: UUID) -> list[CatalogoRepuestos]: ...
