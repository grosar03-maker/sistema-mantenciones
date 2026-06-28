from uuid import UUID

from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion


class CompletarMantencion:

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

        if orden.estado != EstadoOrden.EN_PROGRESO:
            raise ValueError(
                "Solo se pueden completar órdenes en progreso"
            )

        orden.estado = EstadoOrden.COMPLETADA
        self._repo_orden.guardar(orden)
