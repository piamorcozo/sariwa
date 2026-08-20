from datetime import datetime
from zoneinfo import ZoneInfo

MANILA = ZoneInfo("Asia/Manila")
CUTOFF_HOUR = 15


def same_day_status() -> dict:
    now = datetime.now(MANILA)
    cutoff = now.replace(hour=CUTOFF_HOUR, minute=0, second=0, microsecond=0)
    remaining = int((cutoff - now).total_seconds())
    eligible = remaining > 0
    if eligible:
        hours, rem = divmod(remaining, 3600)
        minutes = rem // 60
        label = f"Order within {hours}h {minutes:02d}m for delivery today in Metro Manila."
    else:
        label = "Same-day cutoff has passed. Choose tomorrow or a later date."
    return {
        "eligible": eligible,
        "cutoff": cutoff.isoformat(),
        "remaining_seconds": max(0, remaining),
        "label": label,
    }
