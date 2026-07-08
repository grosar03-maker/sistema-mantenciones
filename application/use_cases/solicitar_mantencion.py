from datetime import date, datetime

from domain.entities.cliente import Cliente
from domain.entities.orden_mantencion import OrdenMantencion
from domain.entities.modelo import Modelo
from domain.entities.catalogo_repuestos import CatalogoRepuestos
from domain.value_objects.tipo_mantencion import TipoMantencion
from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_cliente import RepositorioCliente
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion
from application.ports.repositorio_catalogo_repuestos import RepositorioCatalogoRepuestos
from application.ports.servicio_notificacion import ServicioNotificacion


class SolicitarMantencion:

    def __init__(
        self,
        repo_cliente: RepositorioCliente,
        repo_orden: RepositorioOrdenMantencion,
        repo_catalogo: RepositorioCatalogoRepuestos,
        notificador: ServicioNotificacion,
    ) -> None:
        self._repo_cliente = repo_cliente
        self._repo_orden = repo_orden
        self._repo_catalogo = repo_catalogo
        self._notificador = notificador

    def ejecutar(
        self,
        cliente_id: str,
        modelo: Modelo,
        numero_serie_cliente: str,
        tipo: TipoMantencion,
        fecha_programada: date | None = None,
        nota_cliente: str = "",
    ) -> OrdenMantencion:
        cliente = self._repo_cliente.obtener_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")

        catalogo = self._repo_catalogo.obtener_por_modelo_y_mantencion(
            modelo, tipo
        )
        repuestos = catalogo.repuestos if catalogo else ()

        orden = OrdenMantencion(
            cliente=cliente,
            modelo=modelo,
            numero_serie_cliente=numero_serie_cliente,
            tipo_mantencion=tipo,
            fecha_solicitud=datetime.now(),
            estado=EstadoOrden.PENDIENTE,
            repuestos=repuestos,
            fecha_programada=fecha_programada,
            nota_cliente=nota_cliente,
        )

        self._repo_orden.guardar(orden)
        self._notificador.notificar_confirmacion_cliente(orden)
        self._notificador.notificar_nueva_orden_mecanicos(orden)

        return orden
