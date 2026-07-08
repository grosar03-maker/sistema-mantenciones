from django.conf import settings
from django.core.mail import send_mail

from domain.entities.orden_mantencion import OrdenMantencion
from application.ports.servicio_notificacion import ServicioNotificacion
from infrastructure.models import Mecanico


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

    def notificar_confirmacion_cliente(self, orden: OrdenMantencion) -> None:
        asunto = f"Confirmación de Orden de Mantención - {self._nombre_modelo(orden)}"
        mensaje = self._plantilla_cliente(orden)
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.cliente.email],
            fail_silently=False,
        )

    def notificar_detalle_mecanico(self, orden: OrdenMantencion) -> None:
        if not orden.mecanico_asignado:
            return

        asunto = f"Nueva Orden Asignada - {self._numero_serie(orden)}"
        mensaje = self._plantilla_mecanico(orden)
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.mecanico_asignado.email],
            fail_silently=False,
        )

    def notificar_reprogramacion_cliente(self, orden: OrdenMantencion, fecha_anterior: str, fecha_nueva: str) -> None:
        tipo = orden.tipo_mantencion.value if hasattr(orden.tipo_mantencion, "value") else orden.tipo_mantencion
        asunto = f"Reprogramación de Orden - {self._nombre_modelo(orden)}"
        mensaje = (
            f"Estimado(a) {orden.cliente.nombre},\n\n"
            f"Le informamos que la fecha de su orden de mantención ha sido reprogramada.\n\n"
            f"Equipo: {self._nombre_modelo(orden)}\n"
            f"N° Serie: {self._numero_serie(orden)}\n"
            f"Tipo: {tipo}\n"
            f"Fecha anterior: {fecha_anterior}\n"
            f"Nueva fecha: {fecha_nueva}\n\n"
            f"Disculpe las molestias ocasionadas.\n\n"
            f"Saludos cordiales,\nEquipo Case Mantenciones"
        )
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[orden.cliente.email],
            fail_silently=False,
        )

    def notificar_nueva_orden_mecanicos(self, orden: OrdenMantencion) -> None:
        emails = list(Mecanico.objects.values_list("email", flat=True))
        if not emails:
            return

        tipo = orden.tipo_mantencion.value if hasattr(orden.tipo_mantencion, "value") else orden.tipo_mantencion
        asunto = f"Nueva Orden de Mantención - {self._nombre_modelo(orden)}"
        mensaje = (
            f"Se ha registrado una nueva orden de mantención.\n\n"
            f"Cliente: {orden.cliente.nombre}\n"
            f"Contacto: {orden.cliente.telefono} | {orden.cliente.email}\n"
            f"Equipo: {self._nombre_modelo(orden)}\n"
            f"N° Serie: {self._numero_serie(orden)}\n"
            f"Tipo: {tipo}\n"
            f"Fecha Solicitud: {orden.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Ingrese al portal mecánico para revisar y asignar la orden.\n\n"
            f"Case Mantenciones"
        )
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )

    def _plantilla_cliente(self, orden: OrdenMantencion) -> str:
        return (
            f"Estimado(a) {orden.cliente.nombre},\n\n"
            f"Su orden de mantención ha sido registrada exitosamente.\n\n"
            f"Equipo: {self._nombre_modelo(orden)}\n"
            f"N° Serie: {self._numero_serie(orden)}\n"
            f"Tipo: {orden.tipo_mantencion.value}\n"
            f"Estado: {orden.estado.value}\n\n"
            f"Saludos cordiales,\nEquipo Case Mantenciones"
        )

    def _plantilla_mecanico(self, orden: OrdenMantencion) -> str:
        repuestos = "\n".join(
            f"  - [{r.codigo}] {r.nombre} ({r.tipo})" for r in orden.repuestos
        )
        return (
            f"Se le ha asignado una nueva orden de mantención.\n\n"
            f"Cliente: {orden.cliente.nombre}\n"
            f"Contacto: {orden.cliente.telefono} | {orden.cliente.email}\n"
            f"Equipo: {self._nombre_modelo(orden)}\n"
            f"N° Serie: {self._numero_serie(orden)}\n"
            f"Tipo: {orden.tipo_mantencion.value}\n"
            f"Fecha Solicitud: {orden.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Repuestos requeridos:\n{repuestos}\n\n"
            f"Case Mantenciones"
        )
