from uuid import UUID

from domain.entities.mecanico import Mecanico
from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion
from application.ports.servicio_notificacion import ServicioNotificacion


class AsignarMecanico:

    def __init__(
        self,
        repo_orden: RepositorioOrdenMantencion,
        notificador: ServicioNotificacion,
    ) -> None:
        self._repo_orden = repo_orden
        self._notificador = notificador

    def ejecutar(
        self,
        orden_id: UUID,
        mecanico: Mecanico,
    ) -> None:
        orden = self._repo_orden.obtener_por_id(orden_id)
        if not orden:
            raise ValueError("Orden de mantención no encontrada")

        if orden.estado != EstadoOrden.PENDIENTE:
            raise ValueError(
                "Solo se pueden asignar órdenes en estado pendiente"
            )

        orden.mecanico_asignado = mecanico
        orden.estado = EstadoOrden.ASIGNADA

        self._repo_orden.guardar(orden)
        self._notificador.notificar_detalle_mecanico(orden)
