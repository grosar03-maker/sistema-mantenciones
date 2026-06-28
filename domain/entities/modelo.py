from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Modelo:
    nombre: str
    marca: str = "Case"
    id: UUID = field(default_factory=uuid4)
