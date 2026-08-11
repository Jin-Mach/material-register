from datetime import date, datetime, timedelta

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _now() -> datetime:
    return datetime.now()

def get_filter_range(key: str) -> tuple[str, str] | None:
    now = _now()
    if key == "today":
        start = datetime.combine(now.date(), datetime.min.time())
    elif key == "week":
        monday = now.date() - timedelta(days=now.weekday())
        start = datetime.combine(monday, datetime.min.time())
    elif key == "month":
        start = datetime.combine(now.date().replace(day=1), datetime.min.time())
    elif key == "year":
        start = datetime.combine(date(now.year, 1, 1), datetime.min.time())
    else:
        return None
    end = now
    return start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT)