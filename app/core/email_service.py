import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

def get_styled_html_template(candidate_name: str, subject: str, message_body: str, cta_text: str = None, cta_link: str = None) -> str:
    """Generates a professional, responsive HTML email matching TalentLens AI styling."""
    
    cta_button_html = ""
    if cta_text and cta_link:
        cta_button_html = f'''
        <div style="margin: 28px 0; text-align: center;">
            <a href="{cta_link}" target="_blank" style="background-color: #4f46e5; color: #ffffff; padding: 12px 24px; font-weight: bold; border-radius: 8px; text-decoration: none; display: inline-block; box-shadow: 0 4px 6px rgba(79, 70, 229, 0.15);">
                {cta_text}
            </a>
        </div>
        '''
        
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;">
        <tr>
            <td align="center" style="padding: 40px 16px;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025); border: 1px solid #e2e8f0; overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); padding: 32px 24px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">TalentLens <span style="color: #93c5fd;">AI</span></h1>
                            <p style="margin: 4px 0 0 0; color: #bfdbfe; font-size: 13px; font-weight: 500;">Smart Talent Acquisition Screenings</p>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 32px; background-color: #ffffff;">
                            <p style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #0f172a;">Hi {candidate_name},</p>
                            <p style="margin: 0 0 24px 0; font-size: 14px; line-height: 1.6; color: #334155;">{message_body}</p>
                            {cta_button_html}
                            <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 32px 0 20px 0;">
                            <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #64748b; font-style: italic;">
                                Note: This email is sent automatically from our screening engine. Please do not reply directly to this notification.
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td align="center" style="background-color: #f8fafc; padding: 24px; border-top: 1px solid #f1f5f9;">
                            <p style="margin: 0; font-size: 11px; color: #94a3b8; font-weight: 500;">
                                &copy; 2026 TalentLens AI. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''

def send_candidate_email(to_email: str, candidate_name: str, score: float, interview_threshold: float, rejection_threshold: float) -> str:
    """
    Sends a beautifully structured HTML email dynamically tailored to the candidate score.
    Returns None if successful, or raises an Exception with the failure reason.
    """
    
    # 1. Determine template context & thresholds
    if score >= interview_threshold:
        subject = "Congratulations! Next Steps for Your Application"
        message = (
            "We have reviewed your application and are pleased to inform you that "
            "your profile strongly aligns with what we are looking for. "
            "We would love to move forward and invite you for a screening interview. "
            "Please use the link below to schedule a time that works best for you. "
            "We look forward to connecting with you!"
        )
        cta_text = "Schedule Your Interview"
        cta_link = "https://calendly.com"
    elif score < rejection_threshold:
        subject = "Update on Your Application"
        message = (
            "Thank you so much for taking the time to apply and for your interest in this opportunity. "
            "After carefully reviewing all applications, we have decided to move forward with other candidates "
            "whose experience more closely matches our current requirements. "
            "This was a competitive process and we genuinely appreciate the effort you put into your application. "
            "We encourage you to keep an eye on future openings and wish you all the very best in your career journey."
        )
        cta_text = None
        cta_link = None
    else:
        subject = "Your Application Is Under Review"
        message = (
            "Thank you for submitting your application. We wanted to let you know that "
            "we have received your resume and our hiring team is currently reviewing all applications. "
            "Your profile is being considered and we will be in touch with the next steps shortly. "
            "We appreciate your patience and thank you for your interest in joining our team."
        )
        cta_text = None
        cta_link = None
        
    html_content = get_styled_html_template(
        candidate_name=candidate_name,
        subject=subject,
        message_body=message,
        cta_text=cta_text,
        cta_link=cta_link
    )
    
    # 2. Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = to_email
    
    part_html = MIMEText(html_content, "html")
    msg.attach(part_html)
    
    # 3. Deliver via SMTP (supports Mailtrap or other SMTP relays)
    # If credentials are not set or MOCK_EMAIL is enabled, mock a send for visual feedback
    if settings.MOCK_EMAIL or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(f"[SMTP MOCK] Would send email to {to_email} with subject: {subject}")
        # Append to mock_emails.html in workspace for visual local preview
        try:
            import os
            header = f"<div style='background: #e2e8f0; padding: 10px; font-weight: bold; border-radius: 8px; margin-bottom: 10px; font-family: sans-serif; font-size: 13px;'>[MOCK EMAIL LOG] To: {to_email} | Subject: {subject}</div>"
            with open("mock_emails.html", "a", encoding="utf-8") as f:
                f.write(f"\n{header}\n")
                f.write(html_content)
                f.write("\n<hr style='border: 0; border-top: 4px dashed #4f46e5; margin: 40px 0;'>\n")
        except Exception as e:
            logger.error(f"Failed to write mock email to file: {e}")
        return
        
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, to_email, msg.as_string())
        logger.info(f"Email successfully sent to {to_email}")
