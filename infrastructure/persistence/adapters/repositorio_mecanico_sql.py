from uuid import UUID

from domain.entities.mecanico import Mecanico as MecanicoDomain
from application.ports.repositorio_mecanico import RepositorioMecanico
from infrastructure.models import Mecanico as MecanicoORM


class RepositorioMecanicoSQL(RepositorioMecanico):

    def obtener_por_id(self, mecanico_id: UUID) -> MecanicoDomain | None:
        try:
            orm = MecanicoORM.objects.get(id=mecanico_id)
            return self._a_dominio(orm)
        except MecanicoORM.DoesNotExist:
            return None

    def listar_todos(self) -> list[MecanicoDomain]:
        return [self._a_dominio(orm) for orm in MecanicoORM.objects.all()]

    def _a_dominio(self, orm: MecanicoORM) -> MecanicoDomain:
        return MecanicoDomain(
            id=orm.id,
            nombre=orm.nombre,
            email=orm.email,
            especialidad=orm.especialidad,
        )
