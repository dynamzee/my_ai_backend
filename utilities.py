from datetime import datetime

def humanize_date(iso_format_date: str) -> str:
    """
    Converts an ISO date (2026-08-12) into human-readable form (12th August 2026).
    Not for fields that my code still needs to compare or sort, just for the notification
    that will be read by users.
    """
    date_time = datetime.strptime(iso_format_date, "%Y-%m-%d")
    day = date_time.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {date_time.strftime('%B %Y')}"

