"""
Unified messaging service for email and WhatsApp integration.
Handles both SendGrid (email) and Twilio (WhatsApp/SMS) to avoid service collisions.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import requests

logger = logging.getLogger(__name__)


class MessageService:
    """Unified service for sending messages via multiple channels."""

    @staticmethod
    def send_email(
        subject: str,
        recipient: str,
        body: str,
        html_message: str = None,
        sender_name: str = "Portfolio",
        tags: list = None,
    ) -> dict:
        """
        Send email via SendGrid.

        Args:
            subject: Email subject
            recipient: Recipient email address
            body: Plain text body
            html_message: (Optional) HTML version of message
            sender_name: Sender name for display
            tags: (Optional) SendGrid tags for tracking/categorization

        Returns:
            dict with status, message_id, and error details
        """
        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid API key not configured")
            return {
                "success": False,
                "error": "Email service not configured",
                "channel": "email",
            }

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient} with subject: {subject}")
            return {
                "success": True,
                "channel": "email",
                "recipient": recipient,
                "message": "Email sent successfully",
            }
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return {
                "success": False,
                "channel": "email",
                "error": str(e),
            }

    @staticmethod
    def send_email_with_attachments(
        subject: str,
        recipient: str,
        body: str,
        attachment_paths: list,
    ) -> dict:
        """Send an email with file attachments via configured email backend."""
        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid API key not configured")
            return {
                "success": False,
                "error": "Email service not configured",
                "channel": "email",
            }

        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            for path in attachment_paths:
                email.attach_file(path)
            email.send(fail_silently=False)
            logger.info(f"Email with attachments sent to {recipient}: {subject}")
            return {
                "success": True,
                "channel": "email",
                "recipient": recipient,
                "message": "Email with attachments sent successfully",
            }
        except Exception as e:
            logger.error(f"Failed to send attachment email to {recipient}: {str(e)}")
            return {
                "success": False,
                "channel": "email",
                "error": str(e),
            }

    @staticmethod
    def send_whatsapp(
        to_number: str, message: str, media_url: str = None
    ) -> dict:
        """
        Send WhatsApp message via Twilio.

        Args:
            to_number: Recipient phone number (format: "whatsapp:+1234567890")
            message: Message text
            media_url: (Optional) URL of media to attach

        Returns:
            dict with status, message_sid, and error details
        """
        if not all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_WHATSAPP_FROM,
            ]
        ):
            logger.warning("Twilio credentials not fully configured")
            return {
                "success": False,
                "error": "WhatsApp service not configured",
                "channel": "whatsapp",
            }

        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Ensure phone number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"

            message_obj = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number,
                body=message,
                media_url=[media_url] if media_url else None,
            )

            logger.info(f"WhatsApp sent to {to_number}, SID: {message_obj.sid}")
            return {
                "success": True,
                "channel": "whatsapp",
                "recipient": to_number,
                "message_sid": message_obj.sid,
                "message": "WhatsApp message sent successfully",
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_number}: {str(e)}")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": str(e),
            }

    @staticmethod
    def send_whatsapp_template(
        to_number: str,
        content_sid: str,
        content_variables: dict,
    ) -> dict:
        """
        Send a WhatsApp template message via Twilio Content API.

        Args:
            to_number: Recipient phone number, with or without "whatsapp:" prefix
            content_sid: Twilio Content Template SID
            content_variables: Dict of template variable values, e.g. {"1": "Alice"}

        Returns:
            dict with status, message_sid, and error details
        """
        if not all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_WHATSAPP_FROM,
                content_sid,
            ]
        ):
            logger.warning("Twilio template messaging not fully configured")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": "WhatsApp template service not configured",
            }

        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"

            message_obj = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number,
                content_sid=content_sid,
                content_variables=str(content_variables).replace("'", '"'),
            )

            logger.info(f"WhatsApp template sent to {to_number}, SID: {message_obj.sid}")
            return {
                "success": True,
                "channel": "whatsapp",
                "recipient": to_number,
                "message_sid": message_obj.sid,
                "message": "WhatsApp template sent successfully",
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp template to {to_number}: {str(e)}")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": str(e),
            }

    @staticmethod
    def send_sms(to_number: str, message: str) -> dict:
        """
        Send SMS via Twilio.

        Args:
            to_number: Recipient phone number (format: "+1234567890")
            message: Message text

        Returns:
            dict with status, message_sid, and error details
        """
        if not all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_PHONE_FROM,
            ]
        ):
            logger.warning("Twilio SMS credentials not fully configured")
            return {
                "success": False,
                "error": "SMS service not configured",
                "channel": "sms",
            }

        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            message_obj = client.messages.create(
                from_=settings.TWILIO_PHONE_FROM,
                to=to_number,
                body=message,
            )

            logger.info(f"SMS sent to {to_number}, SID: {message_obj.sid}")
            return {
                "success": True,
                "channel": "sms",
                "recipient": to_number,
                "message_sid": message_obj.sid,
                "message": "SMS sent successfully",
            }
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "channel": "sms",
                "error": str(e),
            }

    @staticmethod
    def send_to_admin_email(subject: str, message: str) -> dict:
        """
        Send notification email to portfolio admin.

        Args:
            subject: Email subject
            message: Message body

        Returns:
            dict with status and error details
        """
        admin_email = getattr(settings, "ADMIN_EMAIL", "admin@portfolio.local")
        return MessageService.send_email(
            subject=subject,
            recipient=admin_email,
            body=message,
            sender_name="Portfolio System",
        )

    @staticmethod
    def send_contact_notification(
        name: str, email: str, phone: str, message: str, channels: list = None
    ) -> dict:
        """
        Send contact form notification through multiple channels.

        Args:
            name: Visitor name
            email: Visitor email
            phone: Visitor phone (with country code, e.g., "+1234567890")
            message: Contact message
            channels: List of channels to use ["email", "whatsapp", "sms"]
                      Defaults to ["email"]

        Returns:
            dict with status of each channel attempt
        """
        if channels is None:
            channels = ["email"]

        results = {"submitted_by": name, "channels": {}}

        # Send to portfolio owner via email
        if "email" in channels:
            email_body = f"""
New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}

---
This message was submitted through your portfolio contact form.
            """
            email_result = MessageService.send_email(
                subject=f"Portfolio Contact from {name}",
                recipient=settings.DEFAULT_FROM_EMAIL,
                body=email_body,
            )
            results["channels"]["email"] = email_result

        # Send confirmation to visitor
        if "email" in channels:
            confirmation_body = f"""
Hi {name},

Thank you for reaching out! We've received your message and will get back to you shortly.

Best regards,
Portfolio Team
            """
            confirmation_result = MessageService.send_email(
                subject="We received your message",
                recipient=email,
                body=confirmation_body,
                sender_name="Portfolio",
            )
            results["channels"]["confirmation_email"] = confirmation_result

        # Send WhatsApp to portfolio owner when enabled
        if "whatsapp" in channels:
            owner_whatsapp = getattr(settings, "TWILIO_OWNER_WHATSAPP_TO", "")
            if owner_whatsapp:
                template_sid = getattr(settings, "TWILIO_WHATSAPP_CONTENT_SID", "")
                if template_sid:
                    # Template variable mapping follows Twilio Content variables.
                    content_variables = {
                        "1": name,
                        "2": phone or "No phone provided",
                        "3": email,
                    }
                    whatsapp_result = MessageService.send_whatsapp_template(
                        to_number=owner_whatsapp,
                        content_sid=template_sid,
                        content_variables=content_variables,
                    )
                else:
                    whatsapp_msg = (
                        "New portfolio contact:\n"
                        f"Name: {name}\n"
                        f"Email: {email}\n"
                        f"Phone: {phone or 'N/A'}\n\n"
                        f"Message:\n{message}"
                    )
                    whatsapp_result = MessageService.send_whatsapp(
                        to_number=owner_whatsapp,
                        message=whatsapp_msg,
                    )
            else:
                whatsapp_result = {
                    "success": False,
                    "channel": "whatsapp",
                    "error": "Owner WhatsApp destination is not configured",
                }
            results["channels"]["whatsapp_owner"] = whatsapp_result

        # Send SMS to visitor (optional)
        if "sms" in channels and phone:
            sms_msg = f"Hi {name}! We received your message through the portfolio contact form. We'll be in touch soon!"
            sms_result = MessageService.send_sms(to_number=phone, message=sms_msg)
            results["channels"]["sms"] = sms_result

        # Send Slack notification if configured
        slack_url = getattr(settings, "SLACK_WEBHOOK_URL", None)
        if slack_url:
            slack_data = {
                "text": f"New portfolio contact:\n*Name:* {name}\n*Email:* {email}\n*Phone:* {phone}\n*Channels Used:* {', '.join(channels)}\n*Message:* {message}"
            }
            try:
                requests.post(slack_url, json=slack_data, timeout=5)
                logger.info("Slack notification sent")
            except Exception as e:
                logger.warning(f"Slack notification failed: {str(e)}")

        return results
