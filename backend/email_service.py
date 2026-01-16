"""
Email service for sending assessment results
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

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
            return False, "SENDER_EMAIL not configured"
        if not self.sender_password:
            return False, "SENDER_PASSWORD not configured"
        return True, "Configuration valid"
    
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Repository Assessment Results</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Repository Assessment Complete</h1>
            <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 14px;">Your {platform} repository analysis is ready</p>
        </div>
        
        <!-- Score Section -->
        <div style="background-color: white; padding: 40px 30px; text-align: center; border-left: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb;">
            <div style="display: inline-block; padding: 30px 50px; background-color: {score_color}; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <h2 style="color: white; margin: 0; font-size: 56px; font-weight: bold;">{score:.1f}</h2>
                <p style="color: white; margin: 8px 0 0 0; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">out of 100</p>
            </div>
            <p style="color: #374151; margin: 20px 0 0 0; font-size: 18px; font-weight: 600;">{score_label}</p>
        </div>
        
        <!-- Key Metrics -->
        <div style="background-color: white; padding: 30px; border-left: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb;">
            <div style="display: inline-block; padding: 12px 24px; background-color: {badge_color}; border-radius: 8px; margin-bottom: 20px;">
                <p style="color: {badge_text}; margin: 0; font-size: 14px; font-weight: bold;">Assessment Status: {score_label}</p>
            </div>
            <h3 style="margin: 0 0 20px 0; color: #111827; font-size: 20px; font-weight: bold; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Executive Summary</h3>
            <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid {score_color};">
                {formatted_summary}
            </div>
        </div>
        
        <!-- CTA Button -->
        <div style="background-color: white; padding: 30px; text-align: center; border-left: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb; border-radius: 0 0 10px 10px;">
            <a href="{share_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 15px 40px; border-radius: 8px; font-weight: bold; font-size: 16px;">View Full Report</a>
            <p style="color: #9ca3af; font-size: 12px; margin: 15px 0 0 0;">This link will expire in 48 hours</p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 20px 0; color: #9ca3af; font-size: 12px;">
            <p style="margin: 5px 0;">Repository Scorer - DevSecOps Assessment Platform</p>
            <p style="margin: 5px 0;">You can share this report with your team using the link above</p>
        </div>
    </div>
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
            
            # Create share URL
            share_url = f"{self.base_url}/shared/{share_token}"
            
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
