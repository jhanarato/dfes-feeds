from datetime import datetime, date


def declared_for(value: date) -> str:
    return value.strftime("%d %B %Y").lstrip("0")


def time_of_issue(value: datetime) -> str:
    return value.strftime("%I:%M %p")


def date_of_issue(value: datetime) -> str:
    return value.strftime("%d %B %Y")