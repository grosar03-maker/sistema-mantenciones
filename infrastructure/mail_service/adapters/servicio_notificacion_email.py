from django.conf import settings
from django.core.mail import send_mail

from domain.entities.orden_mantencion import OrdenMantencion
from application.ports.servicio_notificacion import ServicioNotificacion
from infrastructure.models import Mecanico


TIPOS_MANTENCION_DISPLAY = {
    "mant_300h": "300 Horas",
    "mant_600h": "600 Horas",
    "mant_900h": "900 Horas",
    "mant_1200h": "1200 Horas",
    "reparacion_general": "Reparación General",
}

ESTADOS_DISPLAY = {
    "pendiente": "Pendiente",
    "asignada": "Asignada",
    "en_progreso": "En Progreso",
    "completada": "Completada",
    "cancelada": "Cancelada",
}


class ServicioNotificacionEmail(ServicioNotificacion):

    def _nombre_modelo(self, orden: OrdenMantencion) -> str:
        if orden.modelo:
            return f"{orden.modelo.marca} {orden.modelo.nombre}"
        if orden.tractor and orden.tractor.modelo:
            return f"{orden.tractor.modelo.marca} {orden.tractor.modelo.nombre}"
        return "No especificado"

    def _numero_serie(self, orden: OrdenMantencion) -> str:
        if orden.numero_serie_cliente:
            return orden.numero_serie_cliente
        if orden.tractor:
            return orden.tractor.numero_serie
        return "No especificado"

    def _tipo_display(self, orden: OrdenMantencion) -> str:
        raw = orden.tipo_mantencion.value if hasattr(orden.tipo_mantencion, "value") else orden.tipo_mantencion
        return TIPOS_MANTENCION_DISPLAY.get(raw, raw)

    def _estado_display(self, orden: OrdenMantencion) -> str:
        raw = orden.estado.value if hasattr(orden.estado, "value") else orden.estado
        return ESTADOS_DISPLAY.get(raw, raw)

    def _html_wrapper(self, title: str, body: str) -> str:
        return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:'Segoe UI',system-ui,-apple-system,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:24px 16px">
<table role="presentation" width="100%" style="max-width:560px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
<tr><td style="background-color:#CC0000;padding:32px;text-align:center">
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto">
<tr>
<td style="background-color:rgba(255,255,255,0.15);border-radius:12px;padding:6px 14px;font-size:22px;font-weight:800;color:#ffffff;letter-spacing:1px">CM</td>
</tr>
<tr>
<td style="padding-top:10px">
<h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700;letter-spacing:-0.3px">Case Mantenciones</h1>
</td>
</tr>
</table>
</td></tr>
<tr><td style="padding:32px">
<h2 style="margin:0 0 16px;font-size:18px;color:#0F172A;font-weight:600">{title}</h2>
{body}
</td></tr>
<tr><td style="background-color:#F8FAFC;padding:20px 32px;border-top:1px solid #E2E8F0;text-align:center">
<p style="margin:0 0 4px;font-size:13px;color:#64748B">© 2025 Case Mantenciones</p>
<p style="margin:0;font-size:12px;color:#94A3B8">Sistema de Gestión de Mantenciones</p>
</td></tr>
</table>
<p style="margin:16px 0 0;font-size:11px;color:#94A3B8;text-align:center">Este es un correo automático, por favor no responda directamente.</p>
</td></tr>
</table>
</body>
</html>"""

    def _detail_row(self, label: str, value: str) -> str:
        return f"""\
<tr>
<td style="padding:10px 0;border-bottom:1px solid #F1F5F9">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="font-size:13px;color:#64748B;width:40%;padding-right:12px">{label}</td>
<td style="font-size:14px;color:#0F172A;font-weight:500">{value}</td>
</tr>
</table>
</td>
</tr>"""

    def _detail_table(self, rows: str) -> str:
        return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F8FAFC;border-radius:12px;padding:8px 16px;margin:16px 0">
{rows}
</table>"""

    def _btn(self, url: str, text: str) -> str:
        return f"""\
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:20px 0">
<tr>
<td align="center" style="background-color:#CC0000;border-radius:12px;padding:12px 32px">
<a href="{url}" style="color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;display:inline-block">{text}</a>
</td>
</tr>
</table>"""

    def notificar_confirmacion_cliente(self, orden: OrdenMantencion) -> None:
        asunto = f"Confirmación de Orden de Mantención — {self._nombre_modelo(orden)}"
        rows = self._detail_row("Equipo", self._nombre_modelo(orden))
        rows += self._detail_row("N° Serie", self._numero_serie(orden))
        rows += self._detail_row("Tipo de Mantención", self._tipo_display(orden))
        rows += self._detail_row("Estado", self._estado_display(orden))
        body = f"""\
<p style="margin:0 0 20px;font-size:15px;color:#0F172A;line-height:1.5">Estimado(a) <strong>{orden.cliente.nombre}</strong>,</p>
<p style="margin:0 0 4px;font-size:14px;color:#64748B;line-height:1.5">Su orden de mantención ha sido registrada exitosamente.</p>
{self._detail_table(rows)}
<p style="margin:16px 0 0;font-size:14px;color:#64748B;line-height:1.5">Pronto uno de nuestros mecánicos se pondrá en contacto para coordinar los detalles.</p>
<p style="margin:16px 0 0;font-size:14px;color:#0F172A;line-height:1.5">Saludos cordiales,</p>
<p style="margin:0;font-size:14px;color:#0F172A;font-weight:600">Equipo Case Mantenciones</p>"""
        html = self._html_wrapper("Solicitud Confirmada ✓", body)
        send_mail(
            subject=asunto,
            message="",
            html_message=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.cliente.email],
            fail_silently=False,
        )

    def notificar_detalle_mecanico(self, orden: OrdenMantencion) -> None:
        if not orden.mecanico_asignado:
            return
        asunto = f"Nueva Orden Asignada — {self._numero_serie(orden)}"
        repuestos_html = ""
        if orden.repuestos:
            items = "".join(
                f'<tr><td style="padding:6px 0;font-size:13px;color:#0F172A;border-bottom:1px solid #F1F5F9">'
                f'<span style="display:inline-block;background:#E2E8F0;color:#475569;font-size:11px;padding:2px 8px;border-radius:4px;margin-right:8px;font-family:monospace">{r.codigo}</span>'
                f'{r.nombre} <span style="color:#94A3B8;font-size:12px">({r.tipo})</span>'
                f"</td></tr>"
                for r in orden.repuestos
            )
            repuestos_html = f"""\
<p style="margin:16px 0 8px;font-size:13px;font-weight:600;color:#0F172A">Repuestos requeridos:</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F8FAFC;border-radius:12px;padding:8px 16px">
{items}
</table>"""
        rows = self._detail_row("Cliente", orden.cliente.nombre)
        rows += self._detail_row("Contacto", f"{orden.cliente.telefono} &bull; {orden.cliente.email}")
        rows += self._detail_row("Equipo", self._nombre_modelo(orden))
        rows += self._detail_row("N° Serie", self._numero_serie(orden))
        rows += self._detail_row("Tipo de Mantención", self._tipo_display(orden))
        rows += self._detail_row("Fecha Solicitud", orden.fecha_solicitud.strftime("%d/%m/%Y %H:%M"))
        body = f"""\
<p style="margin:0 0 4px;font-size:14px;color:#64748B;line-height:1.5">Se le ha asignado una nueva orden de mantención.</p>
{self._detail_table(rows)}
{repuestos_html}
{self._btn("https://opencloud.host/mecanico/ordenes/", "Ir al Portal Mecánico")}
<p style="margin:0;font-size:14px;color:#0F172A;font-weight:600">Case Mantenciones</p>"""
        html = self._html_wrapper("Nueva Orden Asignada 🔧", body)
        send_mail(
            subject=asunto,
            message="",
            html_message=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.mecanico_asignado.email],
            fail_silently=False,
        )

    def notificar_reprogramacion_cliente(self, orden: OrdenMantencion, fecha_anterior: str, fecha_nueva: str) -> None:
        asunto = f"Reprogramación de Orden — {self._nombre_modelo(orden)}"
        rows = self._detail_row("Equipo", self._nombre_modelo(orden))
        rows += self._detail_row("N° Serie", self._numero_serie(orden))
        rows += self._detail_row("Tipo de Mantención", self._tipo_display(orden))
        rows += self._detail_row("Fecha Anterior", fecha_anterior)
        rows += self._detail_row("Nueva Fecha", fecha_nueva)
        body = f"""\
<p style="margin:0 0 20px;font-size:15px;color:#0F172A;line-height:1.5">Estimado(a) <strong>{orden.cliente.nombre}</strong>,</p>
<p style="margin:0 0 4px;font-size:14px;color:#64748B;line-height:1.5">Le informamos que la fecha de su orden de mantención ha sido reprogramada.</p>
{self._detail_table(rows)}
<p style="margin:16px 0 0;font-size:14px;color:#64748B;line-height:1.5">Disculpe las molestias ocasionadas.</p>
<p style="margin:16px 0 0;font-size:14px;color:#0F172A;line-height:1.5">Saludos cordiales,</p>
<p style="margin:0;font-size:14px;color:#0F172A;font-weight:600">Equipo Case Mantenciones</p>"""
        html = self._html_wrapper("Fecha Reprogramada 📅", body)
        send_mail(
            subject=asunto,
            message="",
            html_message=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.cliente.email],
            fail_silently=False,
        )

    def notificar_nueva_orden_mecanicos(self, orden: OrdenMantencion) -> None:
        emails = list(Mecanico.objects.values_list("email", flat=True))
        if not emails:
            return
        asunto = f"Nueva Orden de Mantención — {self._nombre_modelo(orden)}"
        rows = self._detail_row("Cliente", orden.cliente.nombre)
        rows += self._detail_row("Contacto", f"{orden.cliente.telefono} &bull; {orden.cliente.email}")
        rows += self._detail_row("Equipo", self._nombre_modelo(orden))
        rows += self._detail_row("N° Serie", self._numero_serie(orden))
        rows += self._detail_row("Tipo de Mantención", self._tipo_display(orden))
        rows += self._detail_row("Fecha Solicitud", orden.fecha_solicitud.strftime("%d/%m/%Y %H:%M"))
        body = f"""\
<p style="margin:0 0 4px;font-size:14px;color:#64748B;line-height:1.5">Se ha registrado una nueva orden de mantención en el sistema.</p>
{self._detail_table(rows)}
{self._btn("https://opencloud.host/mecanico/ordenes/", "Ir al Portal Mecánico")}
<p style="margin:0;font-size:14px;color:#0F172A;font-weight:600">Case Mantenciones</p>"""
        html = self._html_wrapper("Nueva Orden Registrada 🚜", body)
        send_mail(
            subject=asunto,
            message="",
            html_message=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )
