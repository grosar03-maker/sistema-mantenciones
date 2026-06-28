from abc import ABC, abstractmethod

from domain.entities.orden_mantencion import OrdenMantencion


class ServicioNotificacion(ABC):

    @abstractmethod
    def notificar_confirmacion_cliente(self, orden: OrdenMantencion) -> None: ...

    @abstractmethod
    def notificar_detalle_mecanico(self, orden: OrdenMantencion) -> None: ...

    @abstractmethod
    def notificar_reprogramacion_cliente(self, orden: OrdenMantencion, fecha_anterior: str, fecha_nueva: str) -> None: ...
