import calendar
from collections import defaultdict
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ObjetivoFormSet, TareaForm
from .models import Objetivo, Tarea


def _volver(request, por_defecto='tareas:lista'):
    """Redirige a la página de la que venía el usuario (si es segura)."""
    destino = request.POST.get('next') or request.GET.get('next')
    if destino and url_has_allowed_host_and_scheme(destino, {request.get_host()}):
        return redirect(destino)
    return redirect(por_defecto)


# ---------- Tareas activas ----------

ORDENES = {
    'fecha': ['fecha_limite', '-prioridad'],
    'prioridad': ['-prioridad', 'fecha_limite'],
}


@login_required
def lista(request):
    orden = request.GET.get('orden', 'fecha')
    if orden not in ORDENES:
        orden = 'fecha'

    tareas = (
        request.user.tareas.filter(completada=False)
        .order_by(*ORDENES[orden])
        .prefetch_related('objetivos')
    )
    completadas = (
        request.user.tareas.filter(completada=True)
        .order_by('-fecha_limite')
        .prefetch_related('objetivos')
    )
    return render(request, 'tareas/lista.html', {
        'tareas': tareas,
        'completadas': completadas,
        'orden': orden,
        'hoy': timezone.localdate(),
    })


# ---------- Calendario ----------

@login_required
def calendario(request, anio=None, mes=None):
    hoy = timezone.localdate()
    anio = anio or hoy.year
    mes = mes or hoy.month
    if not 1 <= mes <= 12:
        return redirect('tareas:calendario')

    semanas = calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes)
    inicio, fin = semanas[0][0], semanas[-1][-1]

    tareas_por_dia = defaultdict(list)
    for tarea in request.user.tareas.filter(fecha_limite__range=(inicio, fin)).order_by(
        'completada', '-prioridad'
    ):
        tareas_por_dia[tarea.fecha_limite].append(tarea)

    dias = [
        [
            {
                'fecha': dia,
                'del_mes': dia.month == mes,
                'es_hoy': dia == hoy,
                'tareas': tareas_por_dia.get(dia, []),
            }
            for dia in semana
        ]
        for semana in semanas
    ]

    anterior = date(anio - 1, 12, 1) if mes == 1 else date(anio, mes - 1, 1)
    siguiente = date(anio + 1, 1, 1) if mes == 12 else date(anio, mes + 1, 1)

    return render(request, 'tareas/calendario.html', {
        'semanas': dias,
        'mes_actual': date(anio, mes, 1),
        'anterior': anterior,
        'siguiente': siguiente,
        'nombres_dias': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
    })


# ---------- Crear / editar / borrar ----------

def _guardar_tarea(request, tarea, plantilla_titulo):
    form = TareaForm(request.POST or None, instance=tarea)
    formset = ObjetivoFormSet(request.POST or None, instance=tarea, prefix='objetivos')

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            tarea = form.save(commit=False)
            tarea.usuario = request.user
            tarea.save()
            formset.instance = tarea
            objetivos = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            siguiente_orden = tarea.objetivos.count() + 1
            for obj in objetivos:
                if not obj.orden:
                    obj.orden = siguiente_orden
                    siguiente_orden += 1
                obj.save()
        messages.success(request, f'Tarea «{tarea.titulo}» guardada.')
        return _volver(request)

    return render(request, 'tareas/formulario.html', {
        'form': form,
        'formset': formset,
        'titulo_pagina': plantilla_titulo,
        'tarea': tarea if tarea.pk else None,
    })


@login_required
def crear(request):
    tarea = Tarea(usuario=request.user)
    # Si venimos del calendario, la fecha ya viene rellenada
    fecha = request.GET.get('fecha')
    if fecha and request.method == 'GET':
        try:
            tarea.fecha_limite = date.fromisoformat(fecha)
        except ValueError:
            pass
    return _guardar_tarea(request, tarea, 'Nueva tarea')


@login_required
def editar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    return _guardar_tarea(request, tarea, 'Editar tarea')


@login_required
def borrar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    if request.method == 'POST':
        tarea.delete()
        messages.info(request, f'Tarea «{tarea.titulo}» eliminada.')
        return redirect('tareas:lista')
    return render(request, 'tareas/confirmar_borrar.html', {'tarea': tarea})


# ---------- Acciones rápidas (marcar / desmarcar) ----------

@login_required
@require_POST
def alternar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    tarea.completada = not tarea.completada
    tarea.save(update_fields=['completada'])
    if tarea.completada:
        messages.success(request, f'¡Tarea «{tarea.titulo}» completada!')
    return _volver(request)


@login_required
@require_POST
def alternar_objetivo(request, pk):
    objetivo = get_object_or_404(Objetivo, pk=pk, tarea__usuario=request.user)
    objetivo.completado = not objetivo.completado
    objetivo.save(update_fields=['completado'])
    return _volver(request)
