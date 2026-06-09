import sys
import os
from datetime import datetime

# Add root folder to python path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import load_config
from src.email_sender.smtp_sender import SMTPSender

def run_smtp_diagnostic():
    print("=== SMTP Email System Diagnostic ===")
    
    # 1. Load config
    try:
        config = load_config()
        print(f"Loaded credentials for: {config.smtp_email}")
        print(f"SMTP Server: {config.smtp_server}:{config.smtp_port}")
        print(f"Recipient: {config.recipient_email}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Please check your .env file.")
        sys.exit(1)

    # 2. Setup sender
    sender = SMTPSender(config)

    # 3. Create test bodies
    subject = f"Diagnostic Test Email - ItsStoryDay - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; background-color: #f7fafc; padding: 20px; }}
            .card {{ background-color: #ffffff; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0; }}
            h1 {{ color: #2b6cb0; }}
            p {{ color: #4a5568; line-height: 1.5; }}
            .time {{ font-style: italic; color: #718096; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>ItsStoryDay Diagnostic Email</h1>
            <p>If you are reading this, your SMTP configuration is <strong>correctly working</strong> and your email app password is valid.</p>
            <p class="time">Sent on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    text_body = (
        f"ItsStoryDay Diagnostic Email\n\n"
        f"If you are reading this, your SMTP configuration is correctly working and your email app password is valid.\n\n"
        f"Sent on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    # 4. Dispatch
    try:
        print("Sending test email...")
        sender.send_email(subject, html_body, text_body)
        print("\n🎉 SUCCESS! The diagnostic email was sent successfully.")
        print("Please check the inbox of your recipient email address.")
    except Exception as e:
        print(f"\n❌ FAILED: SMTP Connection failed.")
        print(f"Error details: {e}")
        print("\nTroubleshooting tips:")
        print("1. If using Gmail, make sure you are using a 16-character App Password, NOT your standard Google account password.")
        print("2. Ensure 2-Step Verification is enabled on your Gmail account.")
        print("3. Check that your network connection allows SMTP traffic on port 587 or 465.")
        sys.exit(1)

if __name__ == "__main__":
    run_smtp_diagnostic()
