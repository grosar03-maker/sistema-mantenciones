from uuid import UUID
from datetime import date

from domain.entities.orden_mantencion import OrdenMantencion as OrdenDomain
from domain.entities.cliente import Cliente as ClienteDomain
from domain.entities.tractor import Tractor as TractorDomain
from domain.entities.mecanico import Mecanico as MecanicoDomain
from domain.entities.modelo import Modelo as ModeloDomain
from domain.entities.repuesto import Repuesto as RepuestoDomain
from domain.value_objects.tipo_mantencion import TipoMantencion
from domain.value_objects.estado_orden import EstadoOrden
from application.ports.repositorio_orden_mantencion import RepositorioOrdenMantencion
from infrastructure.models import OrdenMantencion as OrdenORM
from infrastructure.models import Repuesto as RepuestoORM


class RepositorioOrdenMantencionSQL(RepositorioOrdenMantencion):

    def guardar(self, orden: OrdenDomain) -> None:
        orm, _ = OrdenORM.objects.update_or_create(
            id=orden.id,
            defaults={
                "cliente_id": orden.cliente.id,
                "tractor_id": orden.tractor.id,
                "mecanico_asignado_id": orden.mecanico_asignado.id if orden.mecanico_asignado else None,
                "tipo_mantencion": orden.tipo_mantencion.value,
                "estado": orden.estado.value,
                "fecha_solicitud": orden.fecha_solicitud,
                "fecha_programada": orden.fecha_programada,
                "nota_cliente": orden.nota_cliente,
            },
        )
        if orden.repuestos:
            orm.repuestos.set([r.id for r in orden.repuestos])

    def obtener_por_id(self, orden_id: UUID) -> OrdenDomain | None:
        try:
            orm = (
                OrdenORM.objects
                .select_related("cliente", "tractor__modelo", "tractor__propietario", "mecanico_asignado")
                .prefetch_related("repuestos")
                .get(id=orden_id)
            )
            return self._a_dominio(orm)
        except OrdenORM.DoesNotExist:
            return None

    def listar_por_estado(self, estado: EstadoOrden) -> list[OrdenDomain]:
        orms = (
            OrdenORM.objects
            .select_related("cliente", "tractor__modelo", "tractor__propietario")
            .prefetch_related("repuestos")
            .filter(estado=estado.value)
        )
        return [self._a_dominio(o) for o in orms]

    def listar_por_cliente(self, cliente_id: UUID) -> list[OrdenDomain]:
        orms = (
            OrdenORM.objects
            .select_related("cliente", "tractor__modelo", "tractor__propietario")
            .prefetch_related("repuestos")
            .filter(cliente_id=cliente_id)
        )
        return [self._a_dominio(o) for o in orms]

    def listar_por_mecanico(self, mecanico_id: UUID) -> list[OrdenDomain]:
        orms = (
            OrdenORM.objects
            .select_related("cliente", "tractor__modelo", "tractor__propietario", "mecanico_asignado")
            .prefetch_related("repuestos")
            .filter(mecanico_asignado_id=mecanico_id)
        )
        return [self._a_dominio(o) for o in orms]

    def _a_dominio(self, orm: OrdenORM) -> OrdenDomain:
        repuestos = tuple(
            RepuestoDomain(
                id=r.id,
                codigo=r.codigo,
                nombre=r.nombre,
                tipo=r.tipo,
            )
            for r in orm.repuestos.all()
        )

        return OrdenDomain(
            id=orm.id,
            cliente=ClienteDomain(
                id=orm.cliente.id,
                nombre=orm.cliente.nombre,
                email=orm.cliente.email,
                telefono=orm.cliente.telefono,
            ),
            tractor=TractorDomain(
                id=orm.tractor.id,
                numero_serie=orm.tractor.numero_serie,
                modelo=ModeloDomain(
                    id=orm.tractor.modelo.id,
                    nombre=orm.tractor.modelo.nombre,
                    marca=orm.tractor.modelo.marca,
                ),
                propietario=ClienteDomain(
                    id=orm.tractor.propietario.id,
                    nombre=orm.tractor.propietario.nombre,
                    email=orm.tractor.propietario.email,
                    telefono=orm.tractor.propietario.telefono,
                ),
            ),
            tipo_mantencion=TipoMantencion(orm.tipo_mantencion),
            fecha_solicitud=orm.fecha_solicitud,
            fecha_programada=orm.fecha_programada,
            nota_cliente=orm.nota_cliente or "",
            estado=EstadoOrden(orm.estado),
            mecanico_asignado=(
                MecanicoDomain(
                    id=orm.mecanico_asignado.id,
                    nombre=orm.mecanico_asignado.nombre,
                    email=orm.mecanico_asignado.email,
                    especialidad=orm.mecanico_asignado.especialidad,
                )
                if orm.mecanico_asignado
                else None
            ),
            repuestos=repuestos,
        )
