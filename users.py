from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

USERS_CSV = Path(__file__).parent / "users.csv"


def save_user_record(user_id: int, username: str | None, intent: str) -> None:
    first = not USERS_CSV.exists()
    with USERS_CSV.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if first:
            writer.writerow(["user_id", "username", "intent", "timestamp"])
        writer.writerow([user_id, username or "", intent, datetime.now(timezone.utc).isoformat()])


def load_user_ids() -> list[int]:
    """Return a list of user_ids recorded in USERS_CSV. If file missing, return empty list."""
    if not USERS_CSV.exists():
        return []
    ids: list[int] = []
    with USERS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        for row in reader:
            if not row:
                continue
            try:
                uid = int(row[0])
            except Exception:
                continue
            ids.append(uid)
    # de-duplicate while preserving order
    seen = set()
    out: list[int] = []
    for u in ids:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out
