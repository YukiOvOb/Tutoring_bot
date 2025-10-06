from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Final
import os

from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
	ApplicationBuilder,
	CommandHandler,
	ContextTypes,
	ConversationHandler,
	MessageHandler,
	filters,
)


TOKEN: Final = os.getenv("TELEGRAM_BOT_TOKEN") or '8237551014:AAGjpKh0_UbXG7oHwE0LiU6YwhjfIAGPRk0'
BOT_USERNAME: Final = '@Learning_Chinese_Tutor_Bot'


# 状态
INTENT = 1

# 免费材料文件路径（把你的免费文件放到与此脚本同目录，命名为 free_material.pdf）
FREE_FILE = Path(__file__).parent / "free_material.pdf"
USERS_CSV = Path(__file__).parent / "users.csv"

logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level=logging.INFO,
)
logger = logging.getLogger(__name__)


def save_user_record(user_id: int, username: str | None, intent: str) -> None:
	"""把用户记录追加到 CSV（user_id, username, intent, timestamp）。"""
	first = not USERS_CSV.exists()
	with USERS_CSV.open("a", encoding="utf-8-sig", newline="") as f:
		writer = csv.writer(f)
		if first:
			writer.writerow(["user_id", "username", "intent", "timestamp"])
		writer.writerow([user_id, username or "", intent, datetime.utcnow().isoformat()])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""当用户发送 /start 或首次打开对话时调用，询问学习意图。"""
	user = update.effective_user
	logger.info("User %s started the bot.", user.id if user else "unknown")

	keyboard = ReplyKeyboardMarkup(
		[["Tutoring consultation", "Free Chinese materials"]], one_time_keyboard=True, resize_keyboard=True
	)

	await update.message.reply_text(
		"Hello! I am Midas Chinese Tutor Bot.\nIf you want a tutoring consultation, tap 'Tutoring consultation'.\nIf you want free Chinese learning materials, tap 'Free Chinese materials'.\n\nPlease choose an option by tapping a button or typing your choice:",
		reply_markup=keyboard,
	)
	return INTENT


async def intent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""处理用户选择的学习意图，记录并发送相应内容。"""
	user = update.effective_user
	text = update.message.text.strip()
	logger.info("User %s selected intent: %s", user.id if user else "unknown", text)

	# Recognize multiple input forms (numbers, Chinese, and English phrases)
	normalized = text.strip().lower()
	if normalized in ("1", "咨询", "consult", "consultation", "tutoring consultation", "tutoringconsultation"):
		intent_label = "consultation"
	elif normalized in ("2", "免费", "free", "free material", "free materials", "free chinese materials", "free chinese material", "free_chinese_materials", "free_chinese_material"):
		intent_label = "free_material"
	elif text == "备考":
		intent_label = "exam_prep"
	elif text == "自己兴趣":
		intent_label = "interest"
	else:
		# 未识别的输入也记录原始文本
		intent_label = text

	save_user_record(user.id if user else 0, user.username if user else None, intent_label)

	# 按照流程图实现：
	# - 选择1（咨询/备考）：先发送广告，再发送免费资料
	# - 选择2（免费资料/自己兴趣）：先发送免费资料，再发送广告
	if intent_label in ("consultation", "exam_prep"):
		# send advertisement first
		ad_message = (
			"🎯 We offer high-quality online Chinese tutoring with native-speaking teachers. "
			"Please complete this short form to get personalized assistance:\n"
			"https://forms.gle/9dnyNMZmNGoDtr9a8\n\n"
			"If you'd like to consult directly, reply 'Consult'."
		)
		await update.message.reply_text(ad_message)

		# 然后发送免费资料
		if FREE_FILE.exists():
			try:
				with open(FREE_FILE, "rb") as f:
					await update.message.reply_document(document=f)
			except TelegramError as e:
				logger.exception("发送免费文件失败：%s", e)
				await update.message.reply_text(
					"Sorry, there was an error sending the free file. Please try again later or contact the administrator."
				)
		else:
			await update.message.reply_text(
				"The free file 'free_material.pdf' has not been uploaded to the server. Please place it in the program directory, or reply 'Contact' to request a manual send."
			)

	elif intent_label in ("free_material", "interest"):
		# 先发送免费资料
		if FREE_FILE.exists():
			try:
				with open(FREE_FILE, "rb") as f:
					await update.message.reply_document(document=f)
			except TelegramError as e:
				logger.exception("发送免费文件失败：%s", e)
				await update.message.reply_text(
					"抱歉，发送免费文件时出错；请稍后再试或联系管理员。"
				)
		else:
			await update.message.reply_text(
				"免费文件目前未上传到服务器。请将 `free_material.pdf` 放到程序目录，或回复“联系”获取手动发送方式。"
			)

		# then send advertisement (same as choice 1)
		ad_message = (
			"🎯 We offer high-quality online Chinese tutoring with native-speaking teachers. "
			"Please complete this short form to get personalized assistance:\n"
			"https://forms.gle/9dnyNMZmNGoDtr9a8\n\n"
			"If you'd like to consult directly, reply 'Consult'."
		)
		await update.message.reply_text(ad_message)

	else:
		# unrecognized input, prompt to choose again
		await update.message.reply_text(
			"Unrecognized option. Reply 1 for consultation, or 2 for free materials, or send /start to restart."
		)
		return INTENT

	# end conversation
	await update.message.reply_text("I've sent you the free materials. Happy studying!")
	return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("已取消。如需重新开始请输入 /start 。")
	return ConversationHandler.END


def main() -> None:
	"""启动 Telegram bot。"""
	app = ApplicationBuilder().token(TOKEN).build()

	conv = ConversationHandler(
		entry_points=[CommandHandler("start", start)],
		states={
			INTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, intent_handler)],
		},
		fallbacks=[CommandHandler("cancel", cancel)],
		allow_reentry=True,
	)

	app.add_handler(conv)

	# 额外的帮助命令
	async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
		await update.message.reply_text("使用 /start 开始，选择你的学习意图。")

	app.add_handler(CommandHandler("help", help_cmd))

	logger.info("Bot starting...")
	app.run_polling()


if __name__ == "__main__":
	main()
