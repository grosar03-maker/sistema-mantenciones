from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Cliente:
    nombre: str
    email: str
    telefono: str
    id: UUID = field(default_factory=uuid4)
