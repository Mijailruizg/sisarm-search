from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import tempfile
import shutil
import os

from datetime import date, timedelta

from partidas.models import (
    Rol, Usuario, PartidaArancelaria, PartidaReferencia,
    Busqueda, ExportLog, HistoriaActividad, LicenciaTemporal
)


class FeatureTests(TestCase):
    def setUp(self):
        # crear roles y usuarios
        self.rol_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador', defaults={'descripcion_permisos': 'admin'}
        )
        self.admin_user = Usuario.objects.create_user(username='admin', password='adminpass')
        self.admin_user.rol = self.rol_admin
        self.admin_user.is_staff = True
        # marcar superuser para garantizar acceso en tests (el decorador permite superuser)
        self.admin_user.is_superuser = True
        self.admin_user.save()

        self.normal_user = Usuario.objects.create_user(username='user1', password='userpass')

        # crear licencias temporales para evitar redirecciones de middleware en tests
        hoy = date.today()
        LicenciaTemporal.objects.create(usuario=self.admin_user, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30), estado=True)
        LicenciaTemporal.objects.create(usuario=self.normal_user, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30), estado=True)

        # crear una partida
        self.partida = PartidaArancelaria.objects.create(
            capitulo='01', partida='0101', subpartida='010101', codigo='010101',
            descripcion='Prueba', gravamen='12.5', entidad_emite='Estado', referencia_legal='Disposición 123/2020'
        )

    def test_partida_referencia_file_saved_and_accessible(self):
        tmpdir = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmpdir):
                # crear archivo simulado
                content = b"%PDF-1.4 prueba"
                uploaded = SimpleUploadedFile('doc.pdf', content, content_type='application/pdf')
                ref = PartidaReferencia.objects.create(partida=self.partida, titulo='Doc prueba', texto='texto', archivo=uploaded)
                # comprobar que el archivo existe físicamente
                file_path = os.path.join(settings.MEDIA_ROOT, ref.archivo.name)
                self.assertTrue(os.path.exists(file_path), f"El archivo esperado no existe en {file_path}")
        finally:
            shutil.rmtree(tmpdir)

    def test_solicitar_ayuda_documento_creates_historia(self):
        # crear referencia sin archivo
        ref = PartidaReferencia.objects.create(partida=self.partida, titulo='Sin doc', texto='texto')
        c = Client()
        logged = c.login(username='user1', password='userpass')
        self.assertTrue(logged, 'No se pudo logear el usuario en el test')
        url = reverse('solicitar_ayuda_documento', args=[ref.id])
        resp = c.get(url, follow=True)
        # debe redirigir al detalle y terminar en status 200
        self.assertEqual(resp.status_code, 200)
        # comprobar que se creó HistoriaActividad
        existe = HistoriaActividad.objects.filter(usuario=self.normal_user, accion__icontains=str(ref.id)).exists()
        self.assertTrue(existe, 'No se creó HistoriaActividad tras solicitar ayuda')

    def test_admin_busquedas_export_creates_exportlog(self):
        # crear varias búsquedas
        Busqueda.objects.create(usuario=self.normal_user, termino_buscado='foo', tipo_busqueda='Texto', resultados='0')
        Busqueda.objects.create(usuario=self.normal_user, termino_buscado='bar', tipo_busqueda='Texto', resultados='0')

        c = Client()
        logged = c.login(username='admin', password='adminpass')
        self.assertTrue(logged)

        url = reverse('admin_busquedas') + '?export=csv&usuario=user1'
        resp = c.get(url)
        # respuesta CSV
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])
        # comprobar ExportLog
        self.assertTrue(ExportLog.objects.filter(usuario=self.admin_user, accion='export_busquedas_csv').exists())
