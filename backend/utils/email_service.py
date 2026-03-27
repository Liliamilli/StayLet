"""
Email service for Staylet using Resend.
"""
import os
import asyncio
import logging
import resend
from typing import Optional, List

logger = logging.getLogger(__name__)

# Configure Resend
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
APP_NAME = "Staylet"

# Initialize Resend client
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def is_email_configured() -> bool:
    """Check if email service is properly configured."""
    return bool(RESEND_API_KEY)


async def send_email(
    to: str | List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> dict:
    """
    Send an email using Resend.
    
    Args:
        to: Recipient email address(es)
        subject: Email subject
        html_content: HTML body
        text_content: Optional plain text body
    
    Returns:
        dict with status and email_id
    """
    if not is_email_configured():
        logger.warning("Email service not configured - RESEND_API_KEY missing")
        return {"status": "skipped", "message": "Email service not configured"}
    
    recipients = [to] if isinstance(to, str) else to
    
    params = {
        "from": f"{APP_NAME} <{SENDER_EMAIL}>",
        "to": recipients,
        "subject": subject,
        "html": html_content
    }
    
    if text_content:
        params["text"] = text_content
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent successfully to {recipients}")
        return {
            "status": "success",
            "message": f"Email sent to {', '.join(recipients)}",
            "email_id": email.get("id")
        }
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {"status": "error", "message": str(e)}


# Email Templates

def get_password_reset_email(reset_link: str, user_name: str = "there") -> tuple[str, str]:
    """Generate password reset email content."""
    subject = f"Reset your {APP_NAME} password"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <tr>
                <td style="background-color: #ffffff; border-radius: 12px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <!-- Logo/Header -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                                <span style="font-size: 24px; font-weight: 700; color: #1e293b;">Staylet</span>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Content -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px;">
                                <h1 style="margin: 0 0 16px 0; font-size: 24px; font-weight: 600; color: #1e293b;">
                                    Reset your password
                                </h1>
                                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.6; color: #64748b;">
                                    Hi {user_name},<br><br>
                                    We received a request to reset your password. Click the button below to create a new password:
                                </p>
                                
                                <!-- Button -->
                                <table cellpadding="0" cellspacing="0" style="margin: 32px 0;">
                                    <tr>
                                        <td style="background-color: #2563eb; border-radius: 8px;">
                                            <a href="{reset_link}" style="display: inline-block; padding: 14px 32px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                                Reset Password
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin: 0 0 16px 0; font-size: 14px; line-height: 1.6; color: #94a3b8;">
                                    This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                                </p>
                                
                                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #94a3b8;">
                                    Or copy and paste this link: <br>
                                    <a href="{reset_link}" style="color: #2563eb; word-break: break-all;">{reset_link}</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Footer -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px; border-top: 1px solid #e2e8f0; margin-top: 32px;">
                                <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center;">
                                    © {APP_NAME} - UK Short-Term Let Compliance Made Simple
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, html


def get_expiry_reminder_email(
    user_name: str,
    expiring_items: List[dict],
    dashboard_link: str
) -> tuple[str, str]:
    """Generate expiry reminder email content."""
    count = len(expiring_items)
    subject = f"[Staylet] {count} compliance {'item' if count == 1 else 'items'} expiring soon"
    
    items_html = ""
    for item in expiring_items[:5]:  # Max 5 items
        days = item.get('days_until', 0)
        days_text = f"in {days} days" if days > 0 else "TODAY" if days == 0 else f"{abs(days)} days overdue"
        status_color = "#dc2626" if days <= 0 else "#f59e0b" if days <= 14 else "#2563eb"
        
        items_html += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <span style="font-weight: 600; color: #1e293b;">{item.get('title', 'Unknown')}</span><br>
                            <span style="font-size: 14px; color: #64748b;">{item.get('property_name', 'Unknown Property')}</span>
                        </td>
                        <td style="text-align: right;">
                            <span style="font-size: 14px; font-weight: 500; color: {status_color};">{days_text}</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <tr>
                <td style="background-color: #ffffff; border-radius: 12px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <!-- Logo/Header -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                                <span style="font-size: 24px; font-weight: 700; color: #1e293b;">Staylet</span>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Content -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px;">
                                <h1 style="margin: 0 0 16px 0; font-size: 24px; font-weight: 600; color: #1e293b;">
                                    Compliance items need attention
                                </h1>
                                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.6; color: #64748b;">
                                    Hi {user_name},<br><br>
                                    You have {count} compliance {'item' if count == 1 else 'items'} that {'needs' if count == 1 else 'need'} your attention:
                                </p>
                                
                                <!-- Items List -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px;">
                                    {items_html}
                                </table>
                                
                                <!-- Button -->
                                <table cellpadding="0" cellspacing="0" style="margin: 32px 0;">
                                    <tr>
                                        <td style="background-color: #2563eb; border-radius: 8px;">
                                            <a href="{dashboard_link}" style="display: inline-block; padding: 14px 32px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                                View Dashboard
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Footer -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px; border-top: 1px solid #e2e8f0; margin-top: 32px;">
                                <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center;">
                                    © {APP_NAME} - UK Short-Term Let Compliance Made Simple<br>
                                    <a href="#" style="color: #64748b;">Manage notification preferences</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, html


def get_welcome_email(user_name: str, dashboard_link: str) -> tuple[str, str]:
    """Generate welcome email content."""
    subject = f"Welcome to {APP_NAME}!"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <tr>
                <td style="background-color: #ffffff; border-radius: 12px; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <!-- Logo/Header -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-bottom: 24px; border-bottom: 1px solid #e2e8f0;">
                                <span style="font-size: 24px; font-weight: 700; color: #1e293b;">Staylet</span>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Content -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px;">
                                <h1 style="margin: 0 0 16px 0; font-size: 24px; font-weight: 600; color: #1e293b;">
                                    Welcome to Staylet!
                                </h1>
                                <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 1.6; color: #64748b;">
                                    Hi {user_name},<br><br>
                                    Thank you for signing up! You're now ready to take control of your short-term let compliance.
                                </p>
                                
                                <h2 style="margin: 24px 0 16px 0; font-size: 18px; font-weight: 600; color: #1e293b;">
                                    Get started in 3 steps:
                                </h2>
                                
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <span style="display: inline-block; width: 28px; height: 28px; background-color: #dbeafe; color: #2563eb; font-weight: 600; text-align: center; line-height: 28px; border-radius: 50%; margin-right: 12px;">1</span>
                                            <span style="color: #1e293b;">Add your first property</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <span style="display: inline-block; width: 28px; height: 28px; background-color: #dbeafe; color: #2563eb; font-weight: 600; text-align: center; line-height: 28px; border-radius: 50%; margin-right: 12px;">2</span>
                                            <span style="color: #1e293b;">Upload your compliance certificates</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <span style="display: inline-block; width: 28px; height: 28px; background-color: #dbeafe; color: #2563eb; font-weight: 600; text-align: center; line-height: 28px; border-radius: 50%; margin-right: 12px;">3</span>
                                            <span style="color: #1e293b;">Let Staylet handle the reminders</span>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Button -->
                                <table cellpadding="0" cellspacing="0" style="margin: 32px 0;">
                                    <tr>
                                        <td style="background-color: #2563eb; border-radius: 8px;">
                                            <a href="{dashboard_link}" style="display: inline-block; padding: 14px 32px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none;">
                                                Go to Dashboard
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #94a3b8;">
                                    Need help? Reply to this email or visit our Help Center.
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Footer -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding-top: 32px; border-top: 1px solid #e2e8f0; margin-top: 32px;">
                                <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center;">
                                    © {APP_NAME} - UK Short-Term Let Compliance Made Simple
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, html
