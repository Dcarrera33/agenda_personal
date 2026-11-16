from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Objetivo, Tarea


class AgendaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('yo', password='clave-segura-123')
        self.client.login(username='yo', password='clave-segura-123')
        self.hoy = timezone.localdate()

    def crear_tarea(self, **datos):
        valores = {'titulo': 'Prueba', 'prioridad': 2, 'fecha_limite': self.hoy}
        valores.update(datos)
        return Tarea.objects.create(usuario=self.usuario, **valores)

    def test_hace_falta_iniciar_sesion(self):
        self.client.logout()
        r = self.client.get(reverse('tareas:lista'))
        self.assertRedirects(r, reverse('login') + '?next=/')

    def test_crear_tarea_con_objetivos(self):
        datos = {
            'titulo': 'Estudiar examen',
            'descripcion': '',
            'prioridad': 3,
            'fecha_limite': (self.hoy + timedelta(days=5)).isoformat(),
            'objetivos-TOTAL_FORMS': 3,
            'objetivos-INITIAL_FORMS': 0,
            'objetivos-MIN_NUM_FORMS': 0,
            'objetivos-MAX_NUM_FORMS': 1000,
            'objetivos-0-texto': 'Tema 1',
            'objetivos-1-texto': 'Tema 2',
            'objetivos-2-texto': '',
        }
        r = self.client.post(reverse('tareas:crear'), datos)
        self.assertRedirects(r, reverse('tareas:lista'))
        tarea = Tarea.objects.get()
        self.assertEqual(tarea.usuario, self.usuario)
        self.assertEqual([o.texto for o in tarea.objetivos.all()], ['Tema 1', 'Tema 2'])

    def test_lista_ordenada_y_progreso(self):
        lejana = self.crear_tarea(titulo='Lejana', prioridad=3, fecha_limite=self.hoy + timedelta(days=10))
        cercana = self.crear_tarea(titulo='Cercana', prioridad=1, fecha_limite=self.hoy + timedelta(days=1))
        Objetivo.objects.create(tarea=cercana, texto='a', completado=True)
        Objetivo.objects.create(tarea=cercana, texto='b')

        r = self.client.get(reverse('tareas:lista'))
        self.assertEqual(list(r.context['tareas']), [cercana, lejana])
        self.assertContains(r, '50% de los objetivos')

        r = self.client.get(reverse('tareas:lista') + '?orden=prioridad')
        self.assertEqual(list(r.context['tareas']), [lejana, cercana])

    def test_marcar_tarea_y_objetivo(self):
        tarea = self.crear_tarea()
        objetivo = Objetivo.objects.create(tarea=tarea, texto='a')

        self.client.post(reverse('tareas:alternar_objetivo', args=[objetivo.pk]))
        objetivo.refresh_from_db()
        self.assertTrue(objetivo.completado)

        self.client.post(reverse('tareas:alternar_tarea', args=[tarea.pk]))
        tarea.refresh_from_db()
        self.assertTrue(tarea.completada)
        r = self.client.get(reverse('tareas:lista'))
        self.assertNotIn(tarea, r.context['tareas'])

    def test_calendario_muestra_tareas_del_mes(self):
        self.crear_tarea(titulo='Dentista')
        r = self.client.get(reverse('tareas:calendario'))
        self.assertContains(r, 'Dentista')
        r = self.client.get(reverse('tareas:calendario_mes', args=[2026, 1]))
        self.assertEqual(r.status_code, 200)

    def test_paginas_de_formulario(self):
        tarea = self.crear_tarea()
        Objetivo.objects.create(tarea=tarea, texto='a')
        r = self.client.get(reverse('tareas:crear') + '?fecha=2026-12-24')
        self.assertContains(r, 'value="2026-12-24"')
        self.assertEqual(self.client.get(reverse('tareas:editar', args=[tarea.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('tareas:borrar', args=[tarea.pk])).status_code, 200)

    def test_no_se_ven_tareas_de_otros(self):
        otro = User.objects.create_user('otro', password='x')
        ajena = Tarea.objects.create(usuario=otro, titulo='Secreta', fecha_limite=self.hoy)
        self.assertNotContains(self.client.get(reverse('tareas:lista')), 'Secreta')
        self.assertEqual(self.client.get(reverse('tareas:editar', args=[ajena.pk])).status_code, 404)
