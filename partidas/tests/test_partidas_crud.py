from django.test import TestCase, Client
from django.urls import reverse
from partidas.models import PartidaArancelaria, Rol, Usuario, HistoriaActividad

class PartidasCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.rol = Rol.objects.create(nombre='Administrador', descripcion_permisos='full')
        self.user = Usuario.objects.create_user(username='admin2', password='pass1234', rol=self.rol)
        self.user.is_superuser = True
        self.user.save()

        from partidas.models import LicenciaTemporal
        from datetime import date, timedelta
        LicenciaTemporal.objects.create(
            usuario=self.user,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=6),
            estado=True
        )
        self.client.force_login(self.user)

    def test_create_edit_delete_partida_and_history(self):

        resp_inicio = self.client.get(reverse('inicio'))
        self.assertEqual(resp_inicio.status_code, 200, f"GET inicio failed with status {resp_inicio.status_code}")
        

        resp_get = self.client.get(reverse('crear_partida'))
        self.assertEqual(resp_get.status_code, 200, f"GET crear_partida failed with status {resp_get.status_code}")
        

        data = {
            'capitulo': '01',
            'partida': '0101',
            'subpartida': '01',
            'codigo': 'TST001',
            'descripcion': 'Prueba partida',
            'gravamen': '0',
            'ice_iehd': 'N/A',
            'unidad_medida': 'kg',
            'despacho_frontera': 'Si',
            'tipo_documento': 'Certificado',
            'entidad_emite': 'Aduanas',
            'disp_legal': 'Ley de Aduanas',
            'can_ace36_ace47_ven': 'N/A',
            'ace22_chi_prot': 'N/A',
            'ace66_mexico': 'N/A',
            'permisos': 'Ninguno',
            'subpartidas': 'N/A',
            'referencia_legal': 'N/A',
        }
        resp = self.client.post(reverse('crear_partida'), data, follow=True)

        self.assertEqual(resp.status_code, 200, f"POST crear_partida failed with status {resp.status_code}")
        p = PartidaArancelaria.objects.filter(codigo='TST001').first()

        if p is None:
            form = None
            try:
                form = resp.context.get('form')
            except Exception:
                form = None
            errs = form.errors.as_json() if form else 'no form in context'
            self.fail(f"Partida not created. Form errors: {errs}")

        h = HistoriaActividad.objects.filter(accion__icontains='crear partida').first()
        self.assertIsNotNone(h)


        resp2 = self.client.post(reverse('editar_partida', args=[p.pk]), {
            'capitulo': p.capitulo,
            'partida': p.partida,
            'subpartida': p.subpartida,
            'codigo': p.codigo,
            'descripcion': 'Editada',
            'gravamen': p.gravamen,
            'ice_iehd': p.ice_iehd,
            'unidad_medida': p.unidad_medida,
            'despacho_frontera': p.despacho_frontera,
            'tipo_documento': p.tipo_documento,
            'entidad_emite': p.entidad_emite,
            'disp_legal': p.disp_legal,
            'can_ace36_ace47_ven': p.can_ace36_ace47_ven,
            'ace22_chi_prot': p.ace22_chi_prot,
            'ace66_mexico': p.ace66_mexico,
            'permisos': p.permisos,
            'subpartidas': p.subpartidas,
            'referencia_legal': p.referencia_legal,
        })
        self.assertEqual(resp2.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.descripcion, 'Editada')
        h2 = HistoriaActividad.objects.filter(accion__icontains='editar partida').first()
        self.assertIsNotNone(h2)


        resp3 = self.client.post(reverse('eliminar_partida', args=[p.pk]))
        self.assertEqual(resp3.status_code, 302)
        self.assertFalse(PartidaArancelaria.objects.filter(codigo='TST001').exists())
        h3 = HistoriaActividad.objects.filter(accion__icontains='eliminar partida').first()
        self.assertIsNotNone(h3)
