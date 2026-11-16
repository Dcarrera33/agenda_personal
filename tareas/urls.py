from django.urls import path

from . import views

app_name = 'tareas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/<int:anio>/<int:mes>/', views.calendario, name='calendario_mes'),
    path('tarea/nueva/', views.crear, name='crear'),
    path('tarea/<int:pk>/editar/', views.editar, name='editar'),
    path('tarea/<int:pk>/borrar/', views.borrar, name='borrar'),
    path('tarea/<int:pk>/completar/', views.alternar_tarea, name='alternar_tarea'),
    path('objetivo/<int:pk>/completar/', views.alternar_objetivo, name='alternar_objetivo'),
]
