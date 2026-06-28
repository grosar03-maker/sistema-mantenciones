from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Mecanico:
    nombre: str
    email: str
    especialidad: str
    id: UUID = field(default_factory=uuid4)
