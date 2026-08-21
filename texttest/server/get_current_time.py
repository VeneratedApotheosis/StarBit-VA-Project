from datetime import datetime, timezone


async def get_current_time():
    now_utc = datetime.now(timezone.utc)
    formatted_time = now_utc.strftime("%A, %b %d, %Y at %I:%M %p")
    return formatted_time