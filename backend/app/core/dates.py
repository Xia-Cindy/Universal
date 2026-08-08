from datetime import UTC, date, datetime, timedelta, timezone


LOCAL_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")


def local_now() -> datetime:
    return datetime.now(LOCAL_TIMEZONE)


def local_today() -> date:
    return local_now().date()


def parse_local_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def parse_datetime(value: str | datetime | None) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=LOCAL_TIMEZONE)
        return value.astimezone(LOCAL_TIMEZONE)
    if value is None:
        return local_now()
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=LOCAL_TIMEZONE)
    return parsed.astimezone(LOCAL_TIMEZONE)


def utc_now() -> datetime:
    return datetime.now(UTC)
