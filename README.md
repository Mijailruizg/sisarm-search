# SISARM Search

Sistema de búsqueda de partidas arancelarias con integración de Dialogflow y análisis estadístico.

## Descripción

SISARM Search es una aplicación Django que permite buscar y gestionar partidas arancelarias. Incluye funcionalidades como:

- Búsqueda avanzada de partidas arancelarias
- Integración con Google Dialogflow para chat inteligente
- Estadísticas de búsqueda y análisis de datos
- Gestión de licencias temporales
- Sistema de notificaciones
- Importación de datos desde Excel

## Requisitos Previos

- Python 3.8+
- pip
- Git

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sisarm-search.git
cd sisarm-search
```

### 2. Crear entorno virtual

```bash
python -m venv env
```

### 3. Activar el entorno virtual

**Windows:**
```bash
env\Scripts\activate
```

**Linux/Mac:**
```bash
source env/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://localhost:8000`

## Estructura del Proyecto

```
sisarm-search/
├── partidas/              # Aplicación principal de Django
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Vistas
│   ├── forms.py          # Formularios
│   ├── urls.py           # URLs
│   ├── admin.py          # Configuración admin
│   └── templates/        # Plantillas HTML
├── sisarm_search/        # Configuración del proyecto
│   ├── settings.py       # Configuración
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # WSGI
├── static/               # Archivos estáticos (CSS, JS)
├── templates/            # Plantillas base
├── credentials/          # Credenciales (no incluidas en git)
├── docs/                 # Documentación
├── manage.py             # Comando de gestión Django
└── requirements.txt      # Dependencias Python
```

## Configuración de Dialogflow

Para usar la integración con Dialogflow, necesitas:

1. Crear un proyecto en Google Cloud
2. Habilitar Dialogflow API
3. Descargar las credenciales JSON
4. Colocar el archivo en la carpeta `credentials/`
5. Configurar la ruta en `settings.py`

Ver más detalles en `docs/dialogflow_setup.md`

## Testing

Ejecutar los tests:

```bash
python manage.py test partidas.tests
```

O ejecutar archivos de test específicos:

```bash
python test_features.py
python test_email.py
python test_dialogflow.py
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## Autor

Tu nombre o nombre de tu empresa

## Soporte

Para problemas, preguntas o sugerencias, por favor abre un issue en el repositorio.
