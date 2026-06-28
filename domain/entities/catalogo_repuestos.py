from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.entities.modelo import Modelo
from domain.entities.repuesto import Repuesto
from domain.value_objects.tipo_mantencion import TipoMantencion


@dataclass(frozen=True)
class CatalogoRepuestos:
    modelo: Modelo
    tipo_mantencion: TipoMantencion
    repuestos: tuple[Repuesto, ...]
    id: UUID = field(default_factory=uuid4)
