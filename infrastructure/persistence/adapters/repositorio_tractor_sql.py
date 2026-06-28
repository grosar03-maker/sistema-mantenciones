from uuid import UUID

from domain.entities.tractor import Tractor as TractorDomain
from domain.entities.modelo import Modelo as ModeloDomain
from application.ports.repositorio_tractor import RepositorioTractor
from infrastructure.models import Tractor as TractorORM
from infrastructure.models import ModeloTractor as ModeloORM
from infrastructure.models import Cliente as ClienteORM


class RepositorioTractorSQL(RepositorioTractor):

    def guardar(self, tractor: TractorDomain) -> None:
        TractorORM.objects.update_or_create(
            id=tractor.id,
            defaults={
                "numero_serie": tractor.numero_serie,
                "modelo_id": tractor.modelo.id,
                "propietario_id": tractor.propietario.id,
            },
        )

    def obtener_por_id(self, tractor_id: UUID) -> TractorDomain | None:
        try:
            orm = TractorORM.objects.select_related("modelo", "propietario").get(id=tractor_id)
            return self._a_dominio(orm)
        except TractorORM.DoesNotExist:
            return None

    def obtener_por_numero_serie(self, numero_serie: str) -> TractorDomain | None:
        try:
            orm = TractorORM.objects.select_related("modelo", "propietario").get(
                numero_serie=numero_serie
            )
            return self._a_dominio(orm)
        except TractorORM.DoesNotExist:
            return None

    def obtener_modelo_por_numero_serie(self, numero_serie: str) -> ModeloDomain | None:
        try:
            orm = TractorORM.objects.select_related("modelo").get(
                numero_serie=numero_serie
            )
            return ModeloDomain(
                id=orm.modelo.id,
                nombre=orm.modelo.nombre,
                marca=orm.modelo.marca,
            )
        except TractorORM.DoesNotExist:
            return None

    def _a_dominio(self, orm: TractorORM) -> TractorDomain:
        from domain.entities.cliente import Cliente as ClienteDomain

        return TractorDomain(
            id=orm.id,
            numero_serie=orm.numero_serie,
            modelo=ModeloDomain(
                id=orm.modelo.id,
                nombre=orm.modelo.nombre,
                marca=orm.modelo.marca,
            ),
            propietario=ClienteDomain(
                id=orm.propietario.id,
                nombre=orm.propietario.nombre,
                email=orm.propietario.email,
                telefono=orm.propietario.telefono,
            ),
        )
