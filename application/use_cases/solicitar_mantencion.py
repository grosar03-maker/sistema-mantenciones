from datetime import date, datetime

from domain.entities.cliente import Cliente
from domain.entities.orden_mantencion import OrdenMantencion
from domain.entities.tractor import Tractor
from domain.entities.catalogo_repuestos import CatalogoRepuestos
from domain.value_objects.tipo_mantencion import TipoMantencion
from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_cliente import RepositorioCliente
from application.ports.repositorio_tractor import RepositorioTractor
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion
from application.ports.repositorio_catalogo_repuestos import RepositorioCatalogoRepuestos
from application.ports.servicio_notificacion import ServicioNotificacion


class SolicitarMantencion:

    def __init__(
        self,
        repo_cliente: RepositorioCliente,
        repo_tractor: RepositorioTractor,
        repo_orden: RepositorioOrdenMantencion,
        repo_catalogo: RepositorioCatalogoRepuestos,
        notificador: ServicioNotificacion,
    ) -> None:
        self._repo_cliente = repo_cliente
        self._repo_tractor = repo_tractor
        self._repo_orden = repo_orden
        self._repo_catalogo = repo_catalogo
        self._notificador = notificador

    def ejecutar(
        self,
        cliente_id: str,
        numero_serie: str,
        tipo: TipoMantencion,
        fecha_programada: date | None = None,
        nota_cliente: str = "",
    ) -> OrdenMantencion:
        cliente = self._repo_cliente.obtener_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")

        tractor = self._repo_tractor.obtener_por_numero_serie(numero_serie)
        if not tractor:
            raise ValueError("Tractor no encontrado para el número de serie ingresado")

        catalogo = self._repo_catalogo.obtener_por_modelo_y_mantencion(
            tractor.modelo, tipo
        )
        repuestos = catalogo.repuestos if catalogo else ()

        orden = OrdenMantencion(
            cliente=cliente,
            tractor=tractor,
            tipo_mantencion=tipo,
            fecha_solicitud=datetime.now(),
            estado=EstadoOrden.PENDIENTE,
            repuestos=repuestos,
            fecha_programada=fecha_programada,
            nota_cliente=nota_cliente,
        )

        self._repo_orden.guardar(orden)
        self._notificador.notificar_confirmacion_cliente(orden)

        return orden
