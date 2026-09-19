from datetime import UTC, date, datetime, timedelta

DATE_FORMAT_FULL = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def _now() -> datetime:
    return datetime.now(UTC)


def get_filter_range(key: str) -> tuple[str, str] | None:
    now = _now()
    local_now = now.astimezone()
    if key == "today":
        start = datetime.combine(local_now.date(), datetime.min.time())
    elif key == "week":
        monday = local_now.date() - timedelta(days=local_now.weekday())
        start = datetime.combine(monday, datetime.min.time())
    elif key == "month":
        start = datetime.combine(local_now.date().replace(day=1), datetime.min.time())
    elif key == "year":
        start = datetime.combine(date(local_now.year, 1, 1), datetime.min.time())
    else:
        return None
    start = start.astimezone(UTC)
    return (
        start.strftime(DATE_FORMAT_FULL),
        now.strftime(DATE_FORMAT_FULL),
    )


def parse_date(string_date: str) -> datetime:
    return datetime.strptime(string_date, DATE_FORMAT)
