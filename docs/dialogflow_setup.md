# Configurar Dialogflow para SISARM Search (Guía rápida en español)

Este documento explica los pasos para activar Dialogflow y conectar la IA de asistencia al chat de la aplicación.

IMPORTANTE: el proyecto ya incluye un cliente básico en `partidas/dialogflow_client.py` y la vista `api_chat_help` en `partidas/views.py` está preparada para usar Dialogflow si las variables de entorno y credenciales están configuradas.

---

1) Crear proyecto en Google Cloud

- Ve a https://console.cloud.google.com/ y crea (o selecciona) un proyecto.
- Habilita facturación para el proyecto (Dialogflow requiere facturación para ciertos planes/funcionalidades).

2) Habilitar APIs necesarias

- Habilita la API de Dialogflow (Dialogflow API):
  - Console -> APIs & Services -> Library -> buscar "Dialogflow" -> Enable
- Si vas a usar Dialogflow CX / modelos generativos (a veces referidos como "Chatbot4" en planes comerciales), también habilita Dialogflow CX API y consulta la documentación de Google para el producto generativo (puede requerir acceso adicional o activación de funciones).

3) Crear cuenta de servicio y descargar key JSON

- Console -> IAM & Admin -> Service accounts -> Create Service Account.
- Asigna un nombre (ej. sisarm-dialogflow-sa) y rol: al menos `Dialogflow API Client` o `Editor` durante pruebas. Para producción, restringe permisos.
- Crea una clave (JSON) y descárgala.
- Coloca el archivo JSON en la carpeta del proyecto: credentials/dialogflow-key.json (crea la carpeta credentials si no existe).

4) Configurar variables de entorno en tu máquina (Windows)

- Opciones:
  - Usar el archivo set_env.bat ya incluido: edítalo y reemplaza tu-project-id-aqui por tu PROJECT_ID de GCP. Asegúrate que el JSON se llame dialogflow-key.json y esté en credentials\.
    - Doble click sobre set_env.bat o desde CMD: call set_env.bat.
  - En PowerShell, puedes ejecutar las siguientes líneas (cambia las rutas por las tuyas):

    $env:DIALOGFLOW_PROJECT_ID = "mi-project-id"
    $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\ruta\a\mi\proyecto\credentials\dialogflow-key.json"

5) Instalar dependencias Python

- El proyecto ya contiene google-cloud-dialogflow en requirements.txt. Instala el entorno virtual y paquetes, por ejemplo:

    .\env\Scripts\Activate.ps1
    pip install -r requirements.txt

6) Probar desde la línea de comandos (test rápido)

- Hay un script de prueba en la raíz llamado test_dialogflow.py. Ejecuta:

    python test_dialogflow.py

Si todo está correcto verás una respuesta del agente. Si obtienes errores revisa que:
- GOOGLE_APPLICATION_CREDENTIALS apunte al JSON correcto
- DIALOGFLOW_PROJECT_ID coincida con tu proyecto
- La librería google-cloud-dialogflow está instalada

7) Probar desde la aplicación web

- Inicia Django:

    python manage.py runserver

- Abre la página del Asistente Virtual en la aplicación (ruta /chat/ si corresponde). Envía un mensaje y el frontend se comunica con api_chat_help.

8) Sobre "Chatbot4" / modelos generativos (opcional)

- Si por "Chatbot4" te refieres a las nuevas capacidades generativas de Dialogflow (modelos avanzados / Dialogflow CX), ten en cuenta:
  - Requiere usar la API de Dialogflow CX (paquete google-cloud-dialogflow-cx) y un flujo distinto (sessions/agents en CX).
  - Puede requerir habilitar funciones pagas en Google Cloud (plan generativo) y permisos especiales.
  - Cambios en el código: partidas/dialogflow_client.py debería adaptarse a dialogflowcx.SessionsClient() y a la estructura de requests para modelos generativos.

Si quieres que implemente la integración con Dialogflow CX Generative Models (Chatbot4), dime y la implemento: modificaré dialogflow_client.py, añadiré una ruta de fallbacks y te daré un snippet de configuración.

9) Seguridad y producción

- No subas tus credenciales JSON a repositorios.
- En producción, configura las variables de entorno en el host (Azure, GCP VM, o servicio) de forma segura.
- Limita los permisos de la cuenta de servicio a lo estrictamente necesario.

---

Si quieres, puedo:

- Actualizar set_env.bat automáticamente (ya lo hice con valores de ejemplo).
- Probar (local) el test_dialogflow.py por ti (requiere tus credenciales, no puedo hacerlo sin el JSON).
- Implementar la migración a Dialogflow CX generative si confirmas que quieres el plan "Chatbot4" (necesitaré que me confirmes si es CX/generative o algún otro producto de Dialogflow).

Fin de la guía.
