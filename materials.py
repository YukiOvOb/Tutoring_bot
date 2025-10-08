GDRIVE_SHARE_LINK = "https://drive.google.com/drive/folders/1qiDmq1P73WgdN9i48-KMuVitl8SV5wN0?usp=drive_link"


async def send_materials_link(bot, chat_id: int) -> dict:
    """Send the Google Drive link to chat. Returns a simple stats dict."""
    try:
        text = "Here are the learning materials in Google Drive:"  
        await bot.send_message(chat_id=chat_id, text=f"{text}\n{GDRIVE_SHARE_LINK}")
        return {"sent": 1}
    except Exception:
        return {"sent": 0}
