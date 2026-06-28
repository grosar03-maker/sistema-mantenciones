from uuid import UUID

from domain.entities.orden_mantencion import OrdenMantencion
from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion


class ConsultarOrden:

    def __init__(
        self,
        repo_orden: RepositorioOrdenMantencion,
    ) -> None:
        self._repo_orden = repo_orden

    def por_id(self, orden_id: UUID) -> OrdenMantencion | None:
        return self._repo_orden.obtener_por_id(orden_id)

    def cola_de_trabajos(self) -> list[OrdenMantencion]:
        return self._repo_orden.listar_por_estado(EstadoOrden.ASIGNADA)

    def por_cliente(self, cliente_id: UUID) -> list[OrdenMantencion]:
        return self._repo_orden.listar_por_cliente(cliente_id)

    def por_mecanico(self, mecanico_id: UUID) -> list[OrdenMantencion]:
        return self._repo_orden.listar_por_mecanico(mecanico_id)
