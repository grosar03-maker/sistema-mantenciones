from enum import Enum


class TipoMantencion(Enum):
    MANT_300_HORAS = "mant_300h"
    MANT_600_HORAS = "mant_600h"
    MANT_900_HORAS = "mant_900h"
    MANT_1200_HORAS = "mant_1200h"
    REPARACION_GENERAL = "reparacion_general"

    @property
    def intervalo_horas(self) -> int | None:
        return {
            TipoMantencion.MANT_300_HORAS: 300,
            TipoMantencion.MANT_600_HORAS: 600,
            TipoMantencion.MANT_900_HORAS: 900,
            TipoMantencion.MANT_1200_HORAS: 1200,
            TipoMantencion.REPARACION_GENERAL: None,
        }[self]
