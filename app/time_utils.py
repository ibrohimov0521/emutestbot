from __future__ import annotations

from datetime import datetime, timedelta, timezone

TASHKENT_TZ = timezone(timedelta(hours=5), name="Asia/Tashkent")


def format_tashkent(value: str | None) -> str:
    if not value:
        return "-"

    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M")
