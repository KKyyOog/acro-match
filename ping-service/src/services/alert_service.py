import smtplib
from email.mime.text import MIMEText

class AlertService:
    def __init__(self, sender_email, sender_password, smtp_server, smtp_port):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, recipient_email, subject, message):
        """
        メール通知を送信する。
        """
        try:
            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
                print(f"Debug: Email sent to {recipient_email} with subject '{subject}'")
        except Exception as e:
            print(f"Debug: Failed to send email -> {e}")