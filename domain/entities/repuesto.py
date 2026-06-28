from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Repuesto:
    codigo: str
    nombre: str
    tipo: str
    id: UUID = field(default_factory=uuid4)
