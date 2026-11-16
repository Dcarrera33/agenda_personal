# Agenda personal

Agenda hecha con Django con dos secciones:

- **Tareas activas**: tareas pendientes ordenadas por fecha límite o por prioridad (baja, media, alta), con su lista de objetivos y barra de progreso.
- **Calendario**: vista mensual con todas las tareas en su fecha límite, coloreadas por prioridad.

## Probar en local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # tu usuario para entrar
python manage.py runserver
```

Abre http://127.0.0.1:8000

## Subir a PythonAnywhere (Python 3.12)

1. **Sube el código** (por GitHub con `git clone` desde una consola Bash de PythonAnywhere, o subiendo un .zip en la pestaña *Files*). Por ejemplo, en `/home/TU_USUARIO/agenda`.

2. **Crea el entorno virtual e instala Django** (consola Bash):
   ```bash
   cd ~/agenda
   mkvirtualenv agenda --python=python3.12
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

3. **Crea la web** en la pestaña *Web* → *Add a new web app* → *Manual configuration* → *Python 3.12*.

4. En la pestaña *Web*, configura:
   - **Source code**: `/home/TU_USUARIO/agenda`
   - **Virtualenv**: `/home/TU_USUARIO/.virtualenvs/agenda`
   - **Static files**: URL `/static/` → Directory `/home/TU_USUARIO/agenda/staticfiles`

5. **Edita el archivo WSGI** (enlace en la pestaña *Web*), borra todo y pon:
   ```python
   import os
   import sys

   path = '/home/TU_USUARIO/agenda'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
   os.environ['DJANGO_DEBUG'] = '0'
   os.environ['DJANGO_SECRET_KEY'] = 'PEGA-AQUI-UNA-CLAVE-LARGA-Y-ALEATORIA'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
   Para generar la clave: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

6. Pulsa **Reload** y entra en `https://TU_USUARIO.pythonanywhere.com`.

### Actualizar después de hacer cambios

```bash
cd ~/agenda
git pull                      # o vuelve a subir los archivos
workon agenda
python manage.py migrate
python manage.py collectstatic --noinput
```
Y pulsa **Reload** en la pestaña *Web*.
