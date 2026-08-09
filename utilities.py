from datetime import datetime


def humanize_date(iso_format_date: str) -> str:
    """
    Converts an ISO date (2026-04-13) into human-readable form (13th April 2026).
    Used for anything human-facing — never for fields your code still needs to compare or sort.
    """
    date_time = datetime.strptime(iso_format_date, "%Y-%m-%d")
    day = date_time.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {date_time.strftime('%B %Y')}"

