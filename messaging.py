from __future__ import annotations

from typing import Optional


def ad_message_text() -> str:
    return (
        "🎯 We offer high-quality online Chinese tutoring with native-speaking teachers. "
        "Please complete this short form to get personalized assistance:\n"
        "https://forms.gle/9dnyNMZmNGoDtr9a8\n\n"
        "If you'd like to consult directly, reply 'Consult'."
    )


async def send_text(bot, chat_id: int, text: str, parse_mode: Optional[str] = None) -> None:
    """Send a plain text message via bot to chat_id."""
    await bot.send_message(chat_id=chat_id, text=text)


async def reply_text(update, text: str) -> None:
    """Reply to the incoming update with text (uses reply_text on message)."""
    await update.message.reply_text(text)


async def send_button(bot, chat_id: int, text: str, button_text: str, url: str) -> None:
    """Send a simple URL button to the chat; fall back to plain text if InlineKeyboard is unavailable."""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        kb = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=url)]])
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb)
    except Exception:
        # graceful fallback to plain link text
        await bot.send_message(chat_id=chat_id, text=f"{text}\n{url}")

