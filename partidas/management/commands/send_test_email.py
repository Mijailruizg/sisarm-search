from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys


class Command(BaseCommand):
    help = "Envía un correo de prueba usando la configuración de EMAIL_* en .env/settings."

    def add_arguments(self, parser):
        parser.add_argument('--to', '-t', dest='to', default=None,
                            help='Correo destino. Por defecto EMAIL_HOST_USER')
        parser.add_argument('--subject', '-s', dest='subject', default='Prueba SISARM',
                            help='Asunto')
        parser.add_argument('--message', '-m', dest='message', default='Mensaje de prueba enviado desde management command.',
                            help='Cuerpo')

    def handle(self, *args, **options):
        to = options['to'] or getattr(settings, 'EMAIL_HOST_USER', None)
        if not to:
            self.stderr.write('No hay destinatario definido. Usa --to o configura EMAIL_HOST_USER en settings/.env')
            sys.exit(1)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', f"SISARM <{getattr(settings,'EMAIL_HOST_USER','')}>")

        self.stdout.write(f"Enviando correo de prueba a: {to}")
        try:
            result = send_mail(options['subject'], options['message'], from_email, [to], fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f"send_mail returned: {result}"))
        except Exception:
            import traceback
            self.stderr.write('Error al enviar:')
            traceback.print_exc()
            sys.exit(1)
