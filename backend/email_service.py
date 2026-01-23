"""
Email service for sending assessment results
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import base64
import urllib.parse

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending assessment result emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.base_url = os.getenv("BASE_URL", "http://localhost:5173")
        
    def _validate_config(self) -> tuple[bool, str]:
        """Validate email configuration"""
        if not self.sender_email:
            return False, (
                "SENDER_EMAIL not configured in .env file. "
                "Please set SENDER_EMAIL=your-email@gmail.com"
            )
        if not self.sender_password:
            return False, (
                "SENDER_PASSWORD not configured in .env file. "
                "For Gmail, you need an App Password:\n"
                "1. Go to Google Account > Security > 2-Step Verification (enable it)\n"
                "2. Go to Security > App passwords\n"
                "3. Generate an app password for 'Mail'\n"
                "4. Set SENDER_PASSWORD=your-16-char-password in .env"
            )
        return True, "Configuration valid"
    
    def _encode_email(self, email: str) -> str:
        """Encode email address for URL parameter"""
        encoded = base64.urlsafe_b64encode(email.encode()).decode()
        return urllib.parse.quote(encoded)
    
    def _format_summary_to_html(self, summary: str) -> str:
        """Convert markdown-style summary to clean HTML"""
        # Split into paragraphs
        paragraphs = summary.split('\n\n')
        html_parts = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            lines = paragraph.split('\n')
            bullet_items = []
            regular_text = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    # Remove bullet marker and clean up
                    clean_line = line[1:].strip()
                    # Convert markdown bold **text** to HTML
                    clean_line = clean_line.replace('**', '')
                    bullet_items.append(clean_line)
                elif line:
                    # Remove markdown formatting
                    clean_line = line.replace('**', '')
                    regular_text.append(clean_line)
            
            # Add regular text as paragraph
            if regular_text:
                text = ' '.join(regular_text)
                html_parts.append(f'<p style="color: #4b5563; line-height: 1.6; margin: 12px 0; font-size: 14px;">{text}</p>')
            
            # Add bullet points as list
            if bullet_items:
                list_html = '<ul style="margin: 12px 0; padding-left: 20px;">'
                for item in bullet_items:
                    list_html += f'<li style="color: #4b5563; line-height: 1.6; margin: 6px 0; font-size: 14px;">{item}</li>'
                list_html += '</ul>'
                html_parts.append(list_html)
        
        return ''.join(html_parts)
    
    def _create_email_template(
        self, 
        platform: str,
        score: float,
        ai_summary: str,
        share_url: str
    ) -> str:
        """Create HTML email template"""
        
        # Format the full summary as HTML
        formatted_summary = self._format_summary_to_html(ai_summary)
        
        # Color based on score
        if score >= 80:
            score_color = "#22c55e"  # green
            score_label = "Excellent"
            badge_color = "#dcfce7"
            badge_text = "#166534"
        elif score >= 60:
            score_color = "#eab308"  # yellow
            score_label = "Good"
            badge_color = "#fef9c3"
            badge_text = "#854d0e"
        elif score >= 40:
            score_color = "#f97316"  # orange
            score_label = "Needs Improvement"
            badge_color = "#fed7aa"
            badge_text = "#9a3412"
        else:
            score_color = "#ef4444"  # red
            score_label = "Critical"
            badge_color = "#fee2e2"
            badge_text = "#991b1b"
        
        html = f"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Your Repository Assessment Results</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f3f4f6; margin: 0; padding: 0;">
        <tr>
            <td align="center" style="padding: 20px 15px;">
                <!-- Main Container -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="max-width: 600px; width: 100%;">
                    
                    <!-- Header -->
                    <tr>
                        <td align="center" style="background-color: #667eea; padding: 30px 20px;">
                            <h1 style="color: #ffffff; margin: 0; padding: 0; font-size: 28px; font-weight: bold; font-family: Arial, sans-serif; line-height: 1.2;">Repository Assessment Complete</h1>
                            <p style="color: #e0e7ff; margin: 10px 0 0 0; padding: 0; font-size: 14px; font-family: Arial, sans-serif;">Your {platform} repository analysis is ready</p>
                        </td>
                    </tr>
                    
                    <!-- Score Section -->
                    <tr>
                        <td align="center" style="background-color: #ffffff; padding: 40px 20px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="200" style="background-color: {score_color}; border-radius: 12px;">
                                <tr>
                                    <td align="center" style="padding: 30px 20px;">
                                        <h2 style="color: #ffffff; margin: 0; padding: 0; font-size: 56px; font-weight: bold; font-family: Arial, sans-serif; line-height: 1;">{score:.1f}</h2>
                                        <p style="color: #ffffff; margin: 8px 0 0 0; padding: 0; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; font-family: Arial, sans-serif;">OUT OF 100</p>
                                    </td>
                                </tr>
                            </table>
                            <p style="color: #374151; margin: 20px 0 0 0; padding: 0; font-size: 18px; font-weight: 600; font-family: Arial, sans-serif;">{score_label}</p>
                        </td>
                    </tr>
                    
                    <!-- Executive Summary -->
                    <tr>
                        <td style="background-color: #ffffff; padding: 30px 20px;">
                            <!-- Status Badge -->
                            <table border="0" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="background-color: {badge_color}; padding: 12px 24px; border-radius: 6px;">
                                        <p style="color: {badge_text}; margin: 0; padding: 0; font-size: 14px; font-weight: bold; font-family: Arial, sans-serif;">Assessment Status: {score_label}</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <h3 style="margin: 0 0 15px 0; padding: 0 0 10px 0; color: #111827; font-size: 20px; font-weight: bold; font-family: Arial, sans-serif; border-bottom: 2px solid #e5e7eb;">Executive Summary</h3>
                            
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9fafb; border-left: 4px solid {score_color};">
                                <tr>
                                    <td style="padding: 20px;">
                                        {formatted_summary}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td align="center" style="background-color: #ffffff; padding: 40px 20px 30px;">
                            <!-- Divider Line -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 25px;">
                                <tr>
                                    <td style="border-bottom: 2px solid #e5e7eb;"></td>
                                </tr>
                            </table>
                            
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding: 25px 30px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; border: 2px solid #e2e8f0;">
                                        <h3 style="margin: 0 0 12px 0; padding: 0; color: #1e293b; font-size: 18px; font-weight: 600; font-family: Arial, sans-serif;">Ready to Dive Deeper?</h3>
                                        <p style="margin: 0 0 20px 0; padding: 0; color: #64748b; font-size: 14px; line-height: 1.5; font-family: Arial, sans-serif;">Access your comprehensive assessment report with detailed analysis, recommendations, and actionable insights.</p>
                                        
                                        <!-- View Full Report Link -->
                                        <table border="0" cellpadding="0" cellspacing="0" style="margin-bottom: 15px;">
                                            <tr>
                                                <td align="center" style="padding: 18px 50px; border: 3px solid #667eea; border-radius: 8px; background-color: #ffffff;">
                                                    <a href="{share_url}" target="_blank" style="display: inline-block; color: #667eea; text-decoration: none; font-weight: bold; font-size: 18px; font-family: Arial, sans-serif; letter-spacing: 0.5px;">VIEW FULL REPORT →</a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Expiry Notice -->
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="background-color: #fef3c7; padding: 10px 20px; border-radius: 6px; border-left: 4px solid #f59e0b;">
                                                    <p style="color: #92400e; font-size: 12px; margin: 0; padding: 0; font-family: Arial, sans-serif; font-weight: 600;"> This secure link expires in 48 hours</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Contact Support Section -->
                    <tr>
                        <td align="center" style="background-color: #ffffff; padding: 20px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #667eea; border-radius: 8px;">
                                <tr>
                                    <td align="center" style="padding: 25px 20px;">
                                        <h3 style="margin: 0 0 10px 0; padding: 0; color: #ffffff; font-size: 20px; font-weight: bold; font-family: Arial, sans-serif;">Need More Assistance?</h3>
                                        <p style="margin: 0 0 15px 0; padding: 0; color: #e0e7ff; font-size: 14px; font-family: Arial, sans-serif;">Our DevOps team is here to help you</p>
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td align="center" style="background-color: #ffffff; border-radius: 25px;">
                                                    <a href="mailto:devops@ecanarys.com" style="display: inline-block; color: #667eea; text-decoration: none; padding: 12px 30px; font-weight: bold; font-size: 15px; font-family: Arial, sans-serif; border-radius: 25px;">📧 devops@ecanarys.com</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td align="center" style="padding: 20px; background-color: #f3f4f6;">
                            <p style="margin: 5px 0; padding: 0; color: #9ca3af; font-size: 12px; font-family: Arial, sans-serif;">Repository Scorer - DevSecOps Assessment Platform</p>
                            <p style="margin: 5px 0; padding: 0; color: #9ca3af; font-size: 12px; font-family: Arial, sans-serif;">You can share this report with your team using the link above</p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        return html
    
    async def send_assessment_email(
        self,
        recipient_email: str,
        platform: str,
        score: float,
        ai_summary: str,
        share_token: str
    ) -> tuple[bool, str]:
        """
        Send assessment results email
        
        Args:
            recipient_email: Email address to send to
            platform: Platform name (GitHub/GitLab/Bitbucket)
            score: Overall score (0-100)
            ai_summary: AI-generated summary text
            share_token: Unique token for shareable link
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate configuration
            is_valid, error_msg = self._validate_config()
            if not is_valid:
                logger.error(f"Email configuration error: {error_msg}")
                return False, f"Email configuration error: {error_msg}"
            
            # Create share URL with encoded email for click tracking
            encoded_email = self._encode_email(recipient_email)
            share_url = f"{self.base_url}/shared/{share_token}?email={encoded_email}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Your {platform} Repository Assessment Results - Score: {score:.1f}/100"
            msg['From'] = self.sender_email or ""  # Already validated above, won't be None
            msg['To'] = recipient_email
            
            # Create HTML content
            html_content = self._create_email_template(
                platform=platform,
                score=score,
                ai_summary=ai_summary,
                share_url=share_url
            )
            
            # Create plain text fallback
            text_content = f"""
Your {platform} Repository Assessment Results

Overall Score: {score:.1f}/100

Executive Summary:
{ai_summary[:300]}...

View your full report here:
{share_url}

This link will expire in 48 hours.

---
Repository Scorer - DevSecOps Assessment Platform
            """
            
            # Attach both parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                # These are guaranteed to be non-None due to validation above
                assert self.sender_email is not None and self.sender_password is not None
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Assessment email sent successfully to {recipient_email}")
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False, "Email authentication failed. Please check sender credentials."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {str(e)}")
            return False, f"Failed to send email: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False, f"Unexpected error: {str(e)}"


# Global instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
