import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from config.api_config import APIConfig

class EmailService:
    def __init__(self):
        self.smtp_server = APIConfig.SMTP_SERVER
        self.port = APIConfig.SMTP_PORT
        self.email = APIConfig.EMAIL_ADDRESS
        self.password = APIConfig.EMAIL_PASSWORD
        self.is_configured = bool(self.email and self.password)
    
    def send_application(self, to_email: str, subject: str, body: str, applicant_name: str) -> bool:
        """Send job application email"""
        if not self.is_configured:
            print("   ⚠️  Email not configured - simulating send")
            return self._simulate_email_send(to_email, subject, applicant_name)
        
        try:
            message = MimeMultipart()
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
            
            message.attach(MimeText(formatted_body, 'plain'))
            
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
    
    def _simulate_email_send(self, to_email: str, subject: str, applicant_name: str) -> bool:
        """Simulate email sending for demo purposes"""
        print(f"   📧 [SIMULATED] Email to: {to_email}")
        print(f"   📝 Subject: {subject}")
        print(f"   👤 Applicant: {applicant_name}")
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
