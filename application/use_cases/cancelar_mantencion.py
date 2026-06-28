from uuid import UUID

from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion


class CancelarMantencion:

    def __init__(
        self,
        repo_orden: RepositorioOrdenMantencion,
    ) -> None:
        self._repo_orden = repo_orden

    def ejecutar(
        self,
        orden_id: UUID,
    ) -> None:
        orden = self._repo_orden.obtener_por_id(orden_id)
        if not orden:
            raise ValueError("Orden de mantención no encontrada")

        if orden.estado in (EstadoOrden.COMPLETADA, EstadoOrden.CANCELADA):
            raise ValueError(
                "No se puede cancelar una orden ya completada o cancelada"
            )

        orden.estado = EstadoOrden.CANCELADA
        self._repo_orden.guardar(orden)
