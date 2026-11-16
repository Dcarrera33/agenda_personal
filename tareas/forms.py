from django import forms

from .models import Objetivo, Tarea


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'prioridad', 'fecha_limite']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'
            ),
        }


ObjetivoFormSet = forms.inlineformset_factory(
    Tarea,
    Objetivo,
    fields=['texto', 'completado'],
    extra=3,
    can_delete=True,
    widgets={
        'texto': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Nuevo objetivo…'}
        ),
        'completado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    },
)
