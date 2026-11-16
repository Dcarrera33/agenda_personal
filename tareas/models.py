from django.conf import settings
from django.db import models
from django.utils import timezone


class Tarea(models.Model):
    class Prioridad(models.IntegerChoices):
        # El número sirve para ordenar: cuanto más alto, más importante
        BAJA = 1, 'Baja'
        MEDIA = 2, 'Media'
        ALTA = 3, 'Alta'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tareas'
    )
    titulo = models.CharField('título', max_length=200)
    descripcion = models.TextField('descripción', blank=True)
    prioridad = models.PositiveSmallIntegerField(
        choices=Prioridad.choices, default=Prioridad.MEDIA
    )
    fecha_limite = models.DateField('fecha límite')
    completada = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completada', 'fecha_limite', '-prioridad']

    def __str__(self):
        return self.titulo

    @property
    def vencida(self):
        return not self.completada and self.fecha_limite < timezone.localdate()

    @property
    def dias_restantes(self):
        return (self.fecha_limite - timezone.localdate()).days

    @property
    def texto_plazo(self):
        dias = self.dias_restantes
        if dias == 0:
            return 'Vence hoy'
        if dias == 1:
            return 'Vence mañana'
        if dias > 1:
            return f'Quedan {dias} días'
        if dias == -1:
            return 'Venció ayer'
        return f'Venció hace {-dias} días'

    @property
    def color_prioridad(self):
        return {1: 'success', 2: 'warning', 3: 'danger'}[self.prioridad]

    @property
    def progreso(self):
        """Porcentaje de objetivos cumplidos (0-100)."""
        objetivos = list(self.objetivos.all())
        if not objetivos:
            return 100 if self.completada else 0
        hechos = sum(1 for o in objetivos if o.completado)
        return round(hechos * 100 / len(objetivos))


class Objetivo(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='objetivos')
    texto = models.CharField(max_length=200)
    completado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return self.texto
