from datetime import datetime, timezone
import re


def parse_date(date_str: str) -> str:
    date = datetime.strptime(date_str, "%Y%m%d")
    date_utc = date.replace(tzinfo=timezone.utc)
    return date_utc.isoformat()


def parse_datetime(datetime_str: str) -> str:
    date = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")
    date_utc = date.astimezone(timezone.utc)
    return date_utc.isoformat()


def parse_ics_data(ics_data: str):
    event_pattern = re.compile(r"BEGIN:VEVENT(.*?)END:VEVENT", re.DOTALL)
    events = []

    for event in event_pattern.findall(ics_data):
        event_dict = {
            "id": re.search(r"UID:(.*)", event).group(1).strip(),
            "title": re.search(r"SUMMARY:(.*)", event).group(1).strip() if re.search(r"SUMMARY:(.*)", event) else "",
            "dateFrom": parse_date(re.search(r"DTSTART;VALUE=DATE:(.*)", event).group(1).strip()),
            "dateTo": parse_date(re.search(r"DTEND;VALUE=DATE:(.*)", event).group(1).strip()),
            "description": re.search(r"DESCRIPTION:(.*)", event).group(1).strip() if re.search(r"DESCRIPTION:(.*)",
                                                                                               event) else ""
        }
        events.append(event_dict)

    return events
