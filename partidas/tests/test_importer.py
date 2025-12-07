from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile
from partidas.models import PartidaArancelaria, Rol, Usuario, ImportLog


class ImporterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.rol = Rol.objects.create(nombre='Administrador', descripcion_permisos='full')
        self.user = Usuario.objects.create_user(username='admin', password='pass1234', rol=self.rol)
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='admin', password='pass1234')

    def _build_excel(self):
        wb = Workbook()
        ws = wb.active
        headers = ['Capítulo', 'Partida', 'Código', 'Descripción']
        ws.append(headers)
        ws.append(['01', '0101', 'CODE1', 'Descripción uno'])
        ws.append(['01', '0102', 'CODE2', 'Descripción dos'])
        # fila con error (sin descripcion)
        ws.append(['02', '0201', 'CODE3', ''])

        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        return bio

    def test_preview_and_confirm_import(self):
        bio = self._build_excel()
        uploaded = SimpleUploadedFile('test.xlsx', bio.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # POST to preview
        resp = self.client.post(reverse('importar_excel'), {'archivo': uploaded})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vista previa de importación')
        # session should have temp path
        session = self.client.session
        self.assertIn('import_tmp_path', session)
        tmp_path = session['import_tmp_path']
        # Confirm import
        resp2 = self.client.post(reverse('importar_excel'), {'confirm': '1', 'update_existing': '1'})
        # after confirm should redirect to panel_partidas
        self.assertEqual(resp2.status_code, 302)
        # check PartidaArancelaria created (two valid rows)
        self.assertTrue(PartidaArancelaria.objects.filter(codigo='CODE1').exists())
        self.assertTrue(PartidaArancelaria.objects.filter(codigo='CODE2').exists())
        # CODE3 had empty descripcion so should be omitted
        self.assertFalse(PartidaArancelaria.objects.filter(codigo='CODE3').exists())
        # ImportLog created
        logs = ImportLog.objects.filter(usuario=self.user)
        self.assertTrue(logs.exists())
        log = logs.first()
        self.assertEqual(log.importadas, 2)
