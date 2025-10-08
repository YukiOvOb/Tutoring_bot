from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


# In-process recent-send tracking to avoid duplicate link sends
# Structure: { chat_id: { key: timestamp } }
_recent_sends = {}
RECENT_SEND_TTL = 300.0  # seconds


def _prune_recent(chat_id: int) -> None:
    now = time.time()
    table = _recent_sends.get(chat_id)
    if not table:
        return
    to_del = [k for k, ts in table.items() if now - ts > RECENT_SEND_TTL]
    for k in to_del:
        del table[k]
    if not table:
        _recent_sends.pop(chat_id, None)


GDRIVE_SHARE_LINK = "https://drive.google.com/drive/folders/1qiDmq1P73WgdN9i48-KMuVitl8SV5wN0?usp=drive_link"


async def send_materials(chat_id: int, bot) -> dict:
    """Send the shared Google Drive link to the target chat."""
    # prune and avoid duplicate link sends in short time window
    _prune_recent(chat_id)
    recent = _recent_sends.get(chat_id, {})
    if recent.get("gdrive_link"):
        logger.info("Skipping sending drive link to %s because it was sent recently", chat_id)
        return {"sent": 0, "skipped": 1, "errors": 0}

    try:
        text = (
            "Here are the learning materials in Google Drive:\n"
            f"{GDRIVE_SHARE_LINK}\n\n"
            "If you cannot access them, please let the administrator know."
        )
        await bot.send_message(chat_id=chat_id, text=text)
        # record recent send
        _recent_sends.setdefault(chat_id, {})["gdrive_link"] = time.time()
        return {"sent": 1, "skipped": 0, "errors": 0}
    except Exception as e:
        logger.exception("Failed to send drive link to %s -> %s", chat_id, e)
        return {"sent": 0, "skipped": 0, "errors": 1}
