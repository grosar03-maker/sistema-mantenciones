from uuid import UUID

from domain.entities.cliente import Cliente as ClienteDomain
from application.ports.repositorio_cliente import RepositorioCliente
from infrastructure.models import Cliente as ClienteORM


class RepositorioClienteSQL(RepositorioCliente):

    def guardar(self, cliente: ClienteDomain) -> None:
        ClienteORM.objects.update_or_create(
            id=cliente.id,
            defaults={
                "nombre": cliente.nombre,
                "email": cliente.email,
                "telefono": cliente.telefono,
            },
        )

    def obtener_por_id(self, cliente_id: UUID) -> ClienteDomain | None:
        try:
            orm = ClienteORM.objects.get(id=cliente_id)
            return self._a_dominio(orm)
        except ClienteORM.DoesNotExist:
            return None

    def obtener_por_email(self, email: str) -> ClienteDomain | None:
        try:
            orm = ClienteORM.objects.get(email=email)
            return self._a_dominio(orm)
        except ClienteORM.DoesNotExist:
            return None

    def _a_dominio(self, orm: ClienteORM) -> ClienteDomain:
        return ClienteDomain(
            id=orm.id,
            nombre=orm.nombre,
            email=orm.email,
            telefono=orm.telefono,
        )
