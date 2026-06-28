import json
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods

from infrastructure.models import Cliente, OrdenMantencion

from application.use_cases.solicitar_mantencion import SolicitarMantencion
from domain.value_objects.tipo_mantencion import TipoMantencion
from infrastructure.persistence.adapters.repositorio_cliente_sql import RepositorioClienteSQL
from infrastructure.persistence.adapters.repositorio_tractor_sql import RepositorioTractorSQL
from infrastructure.persistence.adapters.repositorio_orden_mantencion_sql import RepositorioOrdenMantencionSQL
from infrastructure.persistence.adapters.repositorio_catalogo_repuestos_sql import RepositorioCatalogoRepuestosSQL
from infrastructure.mail_service.adapters.servicio_notificacion_email import ServicioNotificacionEmail


@require_http_methods(["GET", "POST"])
def registro_cliente(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip().lower()
        telefono = request.POST.get("telefono", "").strip()
        password = request.POST.get("password", "")

        if not all([nombre, email, telefono, password]):
            return render(request, "registro_cliente.html", {
                "error": "Todos los campos son obligatorios",
            })

        if len(password) < 6:
            return render(request, "registro_cliente.html", {
                "error": "La contraseña debe tener al menos 6 caracteres",
            })

        if User.objects.filter(username=email).exists():
            return render(request, "registro_cliente.html", {
                "error": "Ya existe una cuenta con este correo electrónico",
            })

        if Cliente.objects.filter(email=email).exists():
            return render(request, "registro_cliente.html", {
                "error": "Ya existe un cliente registrado con este correo",
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        grupo_clientes, _ = Group.objects.get_or_create(name="clientes")
        user.groups.add(grupo_clientes)
        user.save()

        Cliente.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
        )

        login(request, user)
        return redirect("solicitar_mantencion")

    return render(request, "registro_cliente.html")


@login_required
@require_http_methods(["GET", "POST"])
def solicitar_mantencion(request):
    try:
        cliente_obj = Cliente.objects.get(email=request.user.email)
    except Cliente.DoesNotExist:
        return render(request, "cliente/solicitar_mantencion.html", {
            "error": "No tiene un perfil de cliente asociado a su cuenta",
            "tipos": TipoMantencion,
        })

    if request.method == "POST":
        numero_serie = request.POST.get("numero_serie")
        tipo_str = request.POST.get("tipo_mantencion")
        fecha_str = request.POST.get("fecha_programada")
        nota_cliente = request.POST.get("nota_cliente", "")

        fecha_programada = None
        if fecha_str:
            fecha_programada = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        tipo = TipoMantencion(tipo_str)

        caso_uso = SolicitarMantencion(
            repo_cliente=RepositorioClienteSQL(),
            repo_tractor=RepositorioTractorSQL(),
            repo_orden=RepositorioOrdenMantencionSQL(),
            repo_catalogo=RepositorioCatalogoRepuestosSQL(),
            notificador=ServicioNotificacionEmail(),
        )

        try:
            orden = caso_uso.ejecutar(str(cliente_obj.id), numero_serie, tipo, fecha_programada, nota_cliente)
            imagenes = request.FILES.getlist("imagenes")
            for img in imagenes:
                from infrastructure.models import ImagenOrden
                ImagenOrden.objects.create(orden_id=orden.id, imagen=img)
            return redirect("solicitud_exitosa", orden_id=orden.id)
        except ValueError as e:
            return render(request, "cliente/solicitar_mantencion.html", {
                "error": str(e),
                "tipos": TipoMantencion,
            })

    return render(request, "cliente/solicitar_mantencion.html", {
        "tipos": TipoMantencion,
    })


@login_required
def solicitud_exitosa(request, orden_id):
    orden = get_object_or_404(
        OrdenMantencion.objects.select_related("cliente", "tractor__modelo"),
        id=orden_id,
    )
    return render(request, "cliente/solicitud_exitosa.html", {
        "email_cliente": request.user.email,
        "modelo_tractor": orden.tractor.modelo.nombre,
        "numero_serie": orden.tractor.numero_serie,
        "tipo_mantencion": orden.get_tipo_mantencion_display(),
        "fecha_programada": orden.fecha_programada,
    })


@login_required
def dias_disponibles_api(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    if not year or not month:
        return JsonResponse({"error": "Faltan parámetros year y month"}, status=400)

    from datetime import date
    fecha_inicio = date(int(year), int(month), 1)
    if int(month) == 12:
        fecha_fin = date(int(year) + 1, 1, 1)
    else:
        fecha_fin = date(int(year), int(month) + 1, 1)

    ocupados = set(
        OrdenMantencion.objects
        .filter(fecha_programada__gte=fecha_inicio, fecha_programada__lt=fecha_fin)
        .exclude(estado__in=("cancelada", "completada"))
        .values_list("fecha_programada", flat=True)
        .distinct()
    )

    return JsonResponse({
        "ocupados": [str(d) for d in ocupados],
    })


@login_required
def dashboard_cliente(request):
    try:
        cliente_obj = Cliente.objects.get(email=request.user.email)
    except Cliente.DoesNotExist:
        return render(request, "cliente/dashboard.html", {
            "error": "No tiene un perfil de cliente asociado a su cuenta",
        })

    ordenes = OrdenMantencion.objects.filter(
        cliente=cliente_obj
    ).select_related(
        "tractor__modelo", "mecanico_asignado"
    ).prefetch_related("imagenes").order_by("-fecha_solicitud")

    return render(request, "cliente/dashboard.html", {
        "cliente": cliente_obj,
        "ordenes": ordenes,
    })


@login_required
def buscar_tractor_api(request):
    numero_serie = request.GET.get("q", "").strip()
    if not numero_serie:
        return JsonResponse({"encontrado": False, "error": "Ingrese un número de serie"})

    repo = RepositorioTractorSQL()
    modelo = repo.obtener_modelo_por_numero_serie(numero_serie)

    if not modelo:
        return JsonResponse({"encontrado": False, "error": "Tractor no encontrado"})

    tractor = repo.obtener_por_numero_serie(numero_serie)

    return JsonResponse({
        "encontrado": True,
        "modelo": modelo.nombre,
        "marca": modelo.marca,
        "cliente_id": str(tractor.propietario.id) if tractor else None,
        "tractor_id": str(tractor.id) if tractor else None,
    })
