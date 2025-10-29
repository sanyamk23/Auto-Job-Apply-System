import smtplib
import os
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config.api_config import APIConfig


class EmailService:
    def __init__(self):
        self.smtp_server = APIConfig.SMTP_SERVER
        self.port = APIConfig.SMTP_PORT
        self.email = APIConfig.EMAIL_ADDRESS
        self.password = APIConfig.EMAIL_PASSWORD
        self.is_configured = bool(self.email and self.password)

    def send_application(self, to_email: str, subject: str, body: str, applicant_name: str, attachments: Optional[List[str]] = None) -> bool:
        """Send job application email. Attachments is an optional list of file paths."""
        if not self.is_configured:
            print("   ⚠️  Email not configured - simulating send")
            return self._simulate_email_send(to_email, subject, applicant_name, attachments)

        try:
            message = MIMEMultipart()
            message['From'] = self.email
            message['To'] = to_email
            message['Subject'] = subject

            # Format email body
            formatted_body = f"""
{body}

---
Sent via Job Recommendation System
Applicant: {applicant_name}
"""

            message.attach(MIMEText(formatted_body, 'plain'))

            # Attach files if provided
            if attachments:
                for path in attachments:
                    try:
                        if not os.path.exists(path):
                            print(f"   ⚠️  Attachment not found: {path} (skipping)")
                            continue

                        part = MIMEBase('application', 'octet-stream')
                        with open(path, 'rb') as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
                        message.attach(part)
                        print(f"   📎 Attached: {os.path.basename(path)}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to attach {path}: {e}")

            # Send email
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(message)

            print(f"   ✅ Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"   ❌ Email sending failed: {e}")
            return False

    def _simulate_email_send(self, to_email: str, subject: str, applicant_name: str, attachments: Optional[List[str]] = None) -> bool:
        """Simulate email sending for demo purposes. Prints attachments if any."""
        print(f"   📧 [SIMULATED] Email to: {to_email}")
        print(f"   📝 Subject: {subject}")
        print(f"   👤 Applicant: {applicant_name}")
        if attachments:
            for path in attachments:
                print(f"   📎 [SIMULATED] Attachment: {os.path.basename(path)} ({path})")
        print("   ✅ Email simulation successful")
        return True

    def test_connection(self) -> bool:
        """Test email connection"""
        if not self.is_configured:
            return False

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"Email connection test failed: {e}")
            return False
