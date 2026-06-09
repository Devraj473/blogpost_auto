import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

from src.config import AppConfig
from src.logger import setup_logger

logger = setup_logger("smtp_sender")

class SMTPSender:
    """
    SMTP Email Sender for dispatched story announcements.
    Supports STARTTLS and SSL.
    """
    def __init__(self, config: AppConfig):
        self.config = config
        logger.info(f"SMTPSender initialized for server {self.config.smtp_server}:{self.config.smtp_port}")

    def send_email(self, subject: str, html_body: str, text_body: str) -> bool:
        """
        Sends an email with both HTML and plain text alternatives.
        """
        logger.info(f"Preparing to send email to {self.config.recipient_email}...")
        
        # Create message container
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.config.smtp_email
        msg["To"] = self.config.recipient_email

        # Attach text and html parts
        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        # Connect and send
        try:
            # Check port type
            if self.config.smtp_port == 465:
                logger.info("Connecting using SMTP_SSL (Port 465)...")
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, timeout=15)
            else:
                logger.info(f"Connecting using standard SMTP (Port {self.config.smtp_port})...")
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=15)
                # If standard, execute STARTTLS
                logger.info("Initializing STARTTLS...")
                server.ehlo()
                server.starttls()
                server.ehlo()

            # Login and send
            logger.info(f"Logging in as {self.config.smtp_email}...")
            server.login(self.config.smtp_email, self.config.smtp_password)
            
            logger.info("Sending mail payload...")
            server.sendmail(self.config.smtp_email, self.config.recipient_email, msg.as_string())
            
            server.quit()
            logger.info("Email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"SMTP Error: Failed to send email. Details: {e}")
            raise
