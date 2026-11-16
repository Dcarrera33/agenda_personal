from django.contrib import admin

from .models import Objetivo, Tarea


class ObjetivoInline(admin.TabularInline):
    model = Objetivo
    extra = 1


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'prioridad', 'fecha_limite', 'completada', 'usuario']
    list_filter = ['prioridad', 'completada']
    search_fields = ['titulo']
    inlines = [ObjetivoInline]
