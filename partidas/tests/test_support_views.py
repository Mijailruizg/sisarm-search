from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from partidas.models import SolicitudSoporte


class SupportViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass1234', email='tester@example.com')
        self.client = Client()
        # Crear licencia temporal para evitar redirecciones del middleware en pruebas
        from partidas.models import LicenciaTemporal
        from datetime import date, timedelta
        LicenciaTemporal.objects.create(usuario=self.user, fecha_inicio=date.today(), fecha_fin=date.today()+timedelta(days=30), estado=True)

    def login(self):
        self.client.login(username='tester', password='pass1234')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_soporte_submit_creates_solicitud_and_marks_sent_on_success(self):
        self.login()
        url = reverse('soporte_submit')
        data = {'nombre': 'Tester Nombre', 'email': 'tester@example.com', 'subject': 'Prueba', 'message': 'Necesito ayuda.'}
        resp = self.client.post(url, data, follow=True)
        # debe haberse creado una SolicitudSoporte
        s = SolicitudSoporte.objects.filter(correo__icontains='tester@example.com').first()
        self.assertIsNotNone(s, 'SolicitudSoporte no creada')
        # con backend locmem, send_mail no falla, por lo que estado debe ser 'sent'
        # la vista marca estado 'sent' tras enviar
        s.refresh_from_db()
        self.assertEqual(s.estado, 'sent')

    def test_soporte_submit_requires_email_and_message(self):
        # Usar un usuario SIN email para verificar que la vista exige correo en el formulario
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_no_email = User.objects.create_user(username='noemail', password='pass1234', email='')
        # crear licencia temporal para este usuario también
        from partidas.models import LicenciaTemporal
        from datetime import date, timedelta
        LicenciaTemporal.objects.create(usuario=user_no_email, fecha_inicio=date.today(), fecha_fin=date.today()+timedelta(days=30), estado=True)
        self.client.login(username='noemail', password='pass1234')
        url = reverse('soporte_submit')
        # sin email (ni en formulario ni en usuario)
        resp = self.client.post(url, {'subject': 'x', 'message': 'm'}, follow=True)
        self.assertFalse(SolicitudSoporte.objects.exists())
        # volver a usuario original para no afectar otras pruebas
        self.client.logout()
        self.login()

    @patch('partidas.views.send_mail')
    def test_soporte_submit_marks_error_on_email_failure(self, mock_send):
        # simular excepción al enviar email
        mock_send.side_effect = Exception('SMTP failure')
        self.login()
        url = reverse('soporte_submit')
        data = {'nombre': 'Tester Nombre', 'email': 'tester@example.com', 'subject': 'Prueba error', 'message': 'Mensaje que hará fallar'}
        resp = self.client.post(url, data, follow=True)
        s = SolicitudSoporte.objects.filter(asunto__icontains='Prueba error').first()
        self.assertIsNotNone(s)
        s.refresh_from_db()
        self.assertEqual(s.estado, 'error')
        self.assertIn('SMTP failure', (s.error_message or ''))

    def test_solicitar_renovacion_public_creates_solicitud_for_anonymous(self):
        # Vista pública: un usuario anónimo debe poder abrir el formulario y enviar una solicitud
        url = reverse('solicitar_renovacion')
        # GET should return 200
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # POST as anonymous
        data = {'nombre': 'Anon Nombre', 'email': 'anon@example.com', 'subject': 'Renovar licencia', 'message': 'Solicito renovación'}
        resp2 = self.client.post(url, data, follow=True)
        # Debe haberse creado la solicitud
        s = SolicitudSoporte.objects.filter(correo__icontains='anon@example.com').first()
        self.assertIsNotNone(s)
        s.refresh_from_db()
        # Aunque el envío por email puede fallar en local, el registro debe existir y contener el nombre enviado
        self.assertIn(s.estado, ['pending', 'sent', 'error'])
        self.assertEqual(s.nombre, 'Anon Nombre')
