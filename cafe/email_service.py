"""
Craft Cafe — Email Service
Handles all transactional emails via Django's email backend (SMTP/SendGrid).
Configure via environment variables in .env / settings.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _send(subject, html_content, to_email, reply_to=None):
    """Core send helper — always HTML with plain-text fallback."""
    try:
        plain = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            reply_to=[reply_to or settings.DEFAULT_FROM_EMAIL],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Email sent → {to_email} | Subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email failed → {to_email} | Error: {e}")
        return False


def send_order_confirmation(order):
    """
    Sends order confirmation to the customer immediately after checkout.
    """
    subject = f"☕ Order Confirmed — #{order.id} | Craft Cafe"
    html = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'items': order.items.all(),
    })
    return _send(subject, html, order.customer_email)


def send_order_status_update(order):
    """
    Sent whenever admin updates order status (Preparing / On the Way / Delivered).
    """
    status_emoji = {
        'preparing': '👨‍🍳',
        'on_the_way': '🛵',
        'delivered': '✅',
        'cancelled': '❌',
    }
    emoji = status_emoji.get(order.status, '📦')
    subject = f"{emoji} Your Order #{order.id} is {order.get_status_display()} — Craft Cafe"
    html = render_to_string('emails/order_status.html', {
        'order': order,
        'items': order.items.all(),
    })
    return _send(subject, html, order.customer_email)


def send_new_order_admin_alert(order):
    """
    Alerts the cafe owner instantly when a new order is placed.
    """
    subject = f"🔔 NEW ORDER #{order.id} — Rs.{order.total_amount} | {order.customer_name}"
    html = render_to_string('emails/admin_new_order.html', {
        'order': order,
        'items': order.items.all(),
    })
    return _send(subject, html, settings.ADMIN_EMAIL)


def send_contact_message(name, email, message):
    """
    Forwards contact form submissions to the cafe owner.
    Also sends an auto-reply to the visitor.
    """
    # To admin
    subject = f"📩 New Contact Message from {name}"
    html = render_to_string('emails/contact_message.html', {
        'name': name, 'email': email, 'message': message,
    })
    _send(subject, html, settings.ADMIN_EMAIL, reply_to=email)

    # Auto-reply to visitor
    auto_html = render_to_string('emails/contact_autoreply.html', {
        'name': name,
    })
    _send("We received your message — Craft Cafe ☕", auto_html, email)


def send_feedback_thank_you(reviewer_name, email):
    """Thank-you email after a customer leaves feedback."""
    if not email:
        return False
    subject = "Thank you for your feedback! ☕ — Craft Cafe"
    html = render_to_string('emails/feedback_thanks.html', {
        'reviewer_name': reviewer_name,
    })
    return _send(subject, html, email)
