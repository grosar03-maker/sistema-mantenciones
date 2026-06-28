from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.entities.modelo import Modelo
from domain.entities.cliente import Cliente


@dataclass
class Tractor:
    numero_serie: str
    modelo: Modelo
    propietario: Cliente
    id: UUID = field(default_factory=uuid4)
