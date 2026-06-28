from uuid import UUID

from domain.entities.catalogo_repuestos import CatalogoRepuestos as CatalogoDomain
from domain.entities.modelo import Modelo as ModeloDomain
from domain.entities.repuesto import Repuesto as RepuestoDomain
from domain.value_objects.tipo_mantencion import TipoMantencion
from application.ports.repositorio_catalogo_repuestos import RepositorioCatalogoRepuestos
from infrastructure.models import CatalogoRepuestos as CatalogoORM
from infrastructure.models import Repuesto as RepuestoORM


class RepositorioCatalogoRepuestosSQL(RepositorioCatalogoRepuestos):

    def guardar(self, catalogo: CatalogoDomain) -> None:
        orm, _ = CatalogoORM.objects.update_or_create(
            id=catalogo.id,
            defaults={
                "modelo_id": catalogo.modelo.id,
                "tipo_mantencion": catalogo.tipo_mantencion.value,
            },
        )
        if catalogo.repuestos:
            orm.repuestos.set([r.id for r in catalogo.repuestos])

    def obtener_por_modelo_y_mantencion(
        self, modelo: ModeloDomain, tipo_mantencion: TipoMantencion
    ) -> CatalogoDomain | None:
        try:
            orm = CatalogoORM.objects.prefetch_related("repuestos").get(
                modelo_id=modelo.id,
                tipo_mantencion=tipo_mantencion.value,
            )
            return self._a_dominio(orm)
        except CatalogoORM.DoesNotExist:
            return None

    def listar_por_modelo(self, modelo_id: UUID) -> list[CatalogoDomain]:
        orms = CatalogoORM.objects.prefetch_related("repuestos").filter(
            modelo_id=modelo_id
        )
        return [self._a_dominio(o) for o in orms]

    def _a_dominio(self, orm: CatalogoORM) -> CatalogoDomain:
        repuestos = tuple(
            RepuestoDomain(
                id=r.id,
                codigo=r.codigo,
                nombre=r.nombre,
                tipo=r.tipo,
            )
            for r in orm.repuestos.all()
        )
        return CatalogoDomain(
            id=orm.id,
            modelo=ModeloDomain(
                id=orm.modelo.id,
                nombre=orm.modelo.nombre,
                marca=orm.modelo.marca,
            ),
            tipo_mantencion=TipoMantencion(orm.tipo_mantencion),
            repuestos=repuestos,
        )
