from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import date, datetime

from domain.entities.cliente import Cliente
from domain.entities.tractor import Tractor
from domain.entities.modelo import Modelo
from domain.entities.mecanico import Mecanico
from domain.entities.repuesto import Repuesto
from domain.value_objects.tipo_mantencion import TipoMantencion
from domain.value_objects.estado_orden import EstadoOrden


@dataclass
class OrdenMantencion:
    cliente: Cliente
    tipo_mantencion: TipoMantencion
    fecha_solicitud: datetime
    tractor: Tractor | None = None
    modelo: Modelo | None = None
    numero_serie_cliente: str = ""
    estado: EstadoOrden = EstadoOrden.PENDIENTE
    mecanico_asignado: Mecanico | None = None
    repuestos: tuple[Repuesto, ...] = ()
    fecha_programada: date | None = None
    nota_cliente: str = ""
    id: UUID = field(default_factory=uuid4)
