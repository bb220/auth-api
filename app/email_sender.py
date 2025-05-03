import os

if os.getenv("RAILWAY_ENVIRONMENT") is None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # e.g., your verified SendGrid sender email
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN")

def send_reset_email(to_email: str, reset_link: str):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="Password Reset Request",
        html_content=f"""
            <p>To reset your password, click the link below:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 15 minutes.</p>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Password reset email sent to {to_email}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_verification_email(to_email: str, token: str):
    verification_link = f"{FRONTEND_DOMAIN}/verify-email?token={token}"

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="Verify Your Email",
        html_content=f"""
        <p>Welcome! Please verify your email by clicking the link below:</p>
        <a href="{verification_link}">Verify Email</a>
        <p>This link will expire in 1 hour.</p>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Verification email sent to {to_email}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending verification email: {e}")