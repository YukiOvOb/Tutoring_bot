from __future__ import annotations

import os
import logging
from typing import Final

from telegram import ReplyKeyboardMarkup, Update, Bot
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from messaging import send_text, send_button, ad_message_text
from chooser import parse_intent
from materials import send_materials_link
from users import save_user_record
from users import load_user_ids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN: Final = os.getenv("TELEGRAM_BOT_TOKEN") or '8237551014:AAGjpKh0_UbXG7oHwE0LiU6YwhjfIAGPRk0'

INTENT = 1


class BotApp:
    def __init__(self, token: str):
        self.token = token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = ReplyKeyboardMarkup(
            [["Tutoring consultation", "Free Chinese materials"]], one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Hello! I am Midas Chinese Tutor Bot.\nIf you want a tutoring consultation, tap 'Tutoring consultation'.\nIf you want free Chinese learning materials, tap 'Free Chinese materials'.\n\nPlease choose an option by tapping a button or typing your choice:",
            reply_markup=keyboard,
        )
        return INTENT

    async def intent_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        text = update.message.text.strip()
        intent = parse_intent(text)
        save_user_record(user.id if user else 0, user.username if user else None, intent)

        # Flow: consultation -> ad then materials; free_material -> materials then ad
        if intent in ("consultation", "exam_prep"):
            # send ad first
            await send_text(context.bot, update.effective_chat.id, ad_message_text())
            await send_materials_link(context.bot, update.effective_chat.id)
        elif intent in ("free_material", "interest"):
            await send_materials_link(context.bot, update.effective_chat.id)
            await send_text(context.bot, update.effective_chat.id, ad_message_text())
        else:
            await update.message.reply_text("Unrecognized option. Reply 1 for consultation, or 2 for free materials, or send /start to restart.")
            return INTENT

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Canceled. Use /start to begin again.")
        return ConversationHandler.END

    def run(self) -> None:
        app = ApplicationBuilder().token(self.token).build()

        conv = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={INTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.intent_handler)]},
            fallbacks=[CommandHandler("cancel", self.cancel)],
            allow_reentry=True,
        )
        app.add_handler(conv)
        app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text("Use /start to begin")))

        # send a one-time startup message to previously recorded users using the synchronous Bot
        try:
            user_ids = load_user_ids()
            # prefer requests if available
            try:
                import requests
                import json

                base = f"https://api.telegram.org/bot{self.token}/sendMessage"
                reply_markup = json.dumps({
                    "keyboard": [["Tutoring consultation", "Free Chinese materials"]],
                    "one_time_keyboard": True,
                    "resize_keyboard": True,
                })
                for uid in user_ids:
                    try:
                        requests.post(
                            base,
                            data={
                                "chat_id": uid,
                                "text": (
                                    "Hello! I am Midas Chinese Tutor Bot.\n"
                                    "If you want a tutoring consultation, tap 'Tutoring consultation'.\n"
                                    "If you want free Chinese learning materials, tap 'Free Chinese materials'."
                                ),
                                "reply_markup": reply_markup,
                            },
                            timeout=5,
                        )
                    except Exception as e:
                        logger.debug("Failed to send startup message to %s: %s", uid, e)
            except Exception:
                # fallback to urllib
                import urllib.parse
                import urllib.request

                import json
                reply_markup = json.dumps({
                    "keyboard": [["Tutoring consultation", "Free Chinese materials"]],
                    "one_time_keyboard": True,
                    "resize_keyboard": True,
                })
                for uid in user_ids:
                    try:
                        params = {
                            "chat_id": uid,
                            "text": (
                                "Hello! I am Midas Chinese Tutor Bot.\n"
                                "If you want a tutoring consultation, tap 'Tutoring consultation'.\n"
                                "If you want free Chinese learning materials, tap 'Free Chinese materials'."
                            ),
                            "reply_markup": reply_markup,
                        }
                        data = urllib.parse.urlencode(params).encode()
                        urllib.request.urlopen(f"https://api.telegram.org/bot{self.token}/sendMessage", data=data, timeout=5)
                    except Exception as e:
                        logger.debug("Failed to send startup message to %s: %s", uid, e)
        except Exception:
            logger.debug("Could not send startup messages via HTTP")

        logger.info("Bot starting")
        app.run_polling()


if __name__ == "__main__":
    BotApp(TOKEN).run()
 