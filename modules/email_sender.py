import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(remetente, senha, destinatario, assunto, corpo_email, modo_teste=True, destinatario_teste=None, servidor=None):
    """
    Envia um e-mail usando SMTP do Gmail.
    Se modo_teste=True, envia apenas para destinatario_teste.
    """
    if modo_teste and destinatario_teste:
        destinatario_real = destinatario
        destinatario = destinatario_teste
        assunto = f"[TESTE] {assunto} (original: {destinatario_real})"

    # Criar o objeto MIMEText com o corpo do email
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_email, 'html'))

    try:
        if servidor is None:
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(remetente, senha)
            close_server = True
        else:
            close_server = False

        servidor.send_message(msg)

        if close_server:
            servidor.quit()
        return True, f"Email enviado para {destinatario}"
    except Exception as e:
        return False, f"Erro ao enviar para {destinatario}: {e}" 