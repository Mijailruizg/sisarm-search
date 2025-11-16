from django.core.mail import send_mail, EmailMessage, get_connection
import os
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Prueba la conexión SMTP directamente con el servidor."""
    print("\n=== Probando conexión SMTP directa ===")
    try:
        server = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        port = int(os.getenv("EMAIL_PORT", 587))
        user = os.getenv("EMAIL_HOST_USER")
        pwd = os.getenv("EMAIL_HOST_PASSWORD")
        
        print(f"Conectando a {server}:{port}...")
        smtp = smtplib.SMTP(server, port, timeout=20)
        smtp.set_debuglevel(1)
        print("Conexión establecida")
        
        print("Iniciando EHLO...")
        smtp.ehlo()
        if os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes"):
            print("Iniciando TLS...")
            smtp.starttls()
            smtp.ehlo()
        
        print("Intentando login...")
        smtp.login(user, pwd)
        print("Login exitoso")
        
        # Crear mensaje de prueba
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = user
        msg['Subject'] = "Prueba de conexión SMTP"
        body = "Este es un mensaje de prueba enviado directamente vía SMTP"
        msg.attach(MIMEText(body, 'plain'))
        
        print("Enviando mensaje de prueba...")
        smtp.send_message(msg)
        print("Mensaje enviado correctamente")
        
        smtp.quit()
        print("Conexión cerrada")
        return True
    except Exception as e:
        print(f"Error en prueba SMTP: {str(e)}")
        traceback.print_exc()
        return False

def test_django_email():
    """Prueba el envío de correo usando Django."""
    print("\n=== Probando envío de correo con Django ===")
    try:
        to_email = os.getenv("EMAIL_HOST_USER")  # Enviar al mismo correo de prueba
        subject = "Prueba de envío desde Django SISARM"
        body = "Este es un correo de prueba enviado desde Django. Si lo recibes, la configuración es correcta."
        from_email = os.getenv("DEFAULT_FROM_EMAIL", os.getenv("EMAIL_HOST_USER"))
        
        print(f"Configuración actual:")
        print(f"HOST: {os.getenv('EMAIL_HOST')}")
        print(f"PORT: {os.getenv('EMAIL_PORT')}")
        print(f"USER: {os.getenv('EMAIL_HOST_USER')}")
        print(f"FROM: {from_email}")
        print(f"TO: {to_email}")
        
        # Probar con send_mail
        print("\nProbando send_mail...")
        result = send_mail(
            subject,
            body,
            from_email,
            [to_email],
            fail_silently=False
        )
        print(f"send_mail result: {result}")
        
        # Probar con EmailMessage
        print("\nProbando EmailMessage...")
        connection = get_connection()
        email = EmailMessage(
            subject,
            body,
            from_email,
            [to_email],
            connection=connection
        )
        email.send(fail_silently=False)
        print("EmailMessage enviado correctamente")
        
        return True
    except Exception as e:
        print(f"Error en prueba Django: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de correo...")
    smtp_ok = test_smtp_connection()
    django_ok = test_django_email()
    
    print("\n=== Resumen de pruebas ===")
    print(f"Conexión SMTP: {'✓ OK' if smtp_ok else '✗ Error'}")
    print(f"Envío Django: {'✓ OK' if django_ok else '✗ Error'}")