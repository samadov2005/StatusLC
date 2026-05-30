"""
Telegram bot webhook handler for StatusLC.

This module handles incoming updates from Telegram and processes
bot commands and queries related to student payments and attendance.

Setup:
    1. Create a bot with @BotFather
    2. Set TELEGRAM_BOT_TOKEN environment variable
    3. Configure webhook: POST https://api.telegram.org/botTOKEN/setWebhook
       with {"url": "https://yourdomain.com/telegram/TOKEN/"}
"""

import os
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import date

from core.models import Student, Payment

logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')


def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """
    Send a message to a Telegram chat.
    
    Args:
        chat_id: Telegram chat ID
        text: Message text
        parse_mode: 'HTML' or 'Markdown'
    """
    import requests
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")
        return False


def get_student_info(student_id):
    """Get student information for display."""
    try:
        student = Student.objects.get(id=student_id)
        return student
    except Student.DoesNotExist:
        return None


def get_unpaid_info(month_date):
    """Get unpaid students for a month."""
    from core.utils import get_unpaid_students
    return get_unpaid_students(month_date)


@csrf_exempt
def webhook(request, token=None):
    """
    Telegram webhook endpoint.
    
    Handles incoming updates from Telegram bot.
    Verify token for security.
    
    Args:
        token: Webhook token from URL
    """
    
    # Verify token
    if token != TELEGRAM_TOKEN:
        logger.warning(f"Invalid Telegram token received: {token}")
        return JsonResponse({'detail': 'Invalid token'}, status=403)

    if request.method != 'POST':
        return HttpResponse('OK')

    try:
        update = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to parse Telegram update: {str(e)}")
        return JsonResponse({'detail': 'Bad payload'}, status=400)

    # Process update
    process_update(update)
    
    return JsonResponse({'ok': True})


def process_update(update):
    """
    Process incoming Telegram update.
    
    Args:
        update: Update object from Telegram
    """
    
    # Handle messages
    if 'message' not in update:
        return
    
    message = update['message']
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '').strip()
    
    if not chat_id or not text:
        return
    
    logger.info(f"Processing Telegram message from {chat_id}: {text}")
    
    # Handle commands
    if text.startswith('/'):
        handle_command(chat_id, text)
    else:
        handle_text(chat_id, text)


def handle_command(chat_id, text):
    """
    Handle Telegram bot commands.
    
    Supported commands:
        /start - Show welcome message
        /help - Show available commands
        /unpaid - List unpaid students for current month
        /payments - Check payment status
    """
    
    command = text.split()[0].lower()
    
    if command == '/start':
        message = (
            "🎓 Welcome to StatusLC Bot!\n\n"
            "I can help you manage student payments and attendance.\n\n"
            "Use /help to see available commands."
        )
        send_telegram_message(chat_id, message)
    
    elif command == '/help':
        message = (
            "<b>Available Commands:</b>\n\n"
            "/start - Welcome message\n"
            "/unpaid - List unpaid students for current month\n"
            "/unpaid_date YYYY-MM - Unpaid students for specific month\n"
            "/help - Show this message\n\n"
            "<b>Examples:</b>\n"
            "/unpaid_date 2026-04 - Students unpaid in April 2026"
        )
        send_telegram_message(chat_id, message, parse_mode='HTML')
    
    elif command == '/unpaid' or command == '/unpaid_date':
        # Parse month if provided
        parts = text.split()
        if len(parts) > 1:
            try:
                month_str = parts[1]
                import datetime
                month_date = datetime.datetime.strptime(month_str, '%Y-%m').date()
                month_date = month_date.replace(day=1)
            except (ValueError, IndexError):
                send_telegram_message(
                    chat_id,
                    "❌ Invalid date format. Use /unpaid_date YYYY-MM (e.g., /unpaid_date 2026-04)"
                )
                return
        else:
            month_date = date.today().replace(day=1)
        
        unpaid_students = get_unpaid_info(month_date)
        
        if not unpaid_students.exists():
            message = f"✅ All students have paid for {month_date.strftime('%B %Y')}!"
            send_telegram_message(chat_id, message)
        else:
            message = f"❌ <b>Unpaid Students ({month_date.strftime('%B %Y')}):</b>\n\n"
            for student in unpaid_students[:10]:  # Limit to 10
                message += f"• {student.first_name} {student.last_name}\n"
                message += f"  📱 {student.phone}\n"
                if student.parent_phone:
                    message += f"  👨‍👩‍👧 {student.parent_phone}\n"
            
            if unpaid_students.count() > 10:
                message += f"\n... and {unpaid_students.count() - 10} more"
            
            send_telegram_message(chat_id, message, parse_mode='HTML')
    
    else:
        message = f"❓ Unknown command: {command}\n\nUse /help for available commands."
        send_telegram_message(chat_id, message)


def handle_text(chat_id, text):
    """Handle plain text messages."""
    
    message = (
        "ℹ️ I understand commands, not free text.\n\n"
        "Send /help to see what I can do!"
    )
    send_telegram_message(chat_id, message)

