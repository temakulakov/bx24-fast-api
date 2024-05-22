from fastapi import APIRouter, HTTPException
from app.schemas import GoogleUrl, DateRange, DateFrom
import requests
from app.utils import parse_datetime, parse_ics_data
from datetime import datetime

router = APIRouter()

@router.post("/calendar/rooms")
async def calendar_rooms():
    url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.element.get.json"
    params = {
        "IBLOCK_TYPE_ID": "lists",
        "IBLOCK_ID": "78",
        "SECTION_ID": "0"
    }

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from the provided URL: {str(e)}")

    data = response.json()

    if 'result' not in data:
        raise HTTPException(status_code=400, detail="Unexpected response format")

    items = data['result']
    processed_items = []

    for item in items:
        processed_item = {
            'id': int(item['ID']),
            'color': list(item['PROPERTY_318'].values())[0],
            'title': item['NAME'],
            'section': int(item['IBLOCK_SECTION_ID']),
            'dateFrom': parse_datetime(list(item['PROPERTY_316'].values())[0]),
            'dateTo': parse_datetime(list(item['PROPERTY_317'].values())[0])
        }
        processed_items.append(processed_item)

    return {
        'data': processed_items
    }

@router.post("/calendar/builds")
async def calendar_builds():
    url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.section.get.json"
    params = {
        "IBLOCK_TYPE_ID": "lists",
        "IBLOCK_ID": "78"
    }

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from the provided URL: {str(e)}")

    data = response.json()

    if 'result' not in data:
        raise HTTPException(status_code=400, detail="Unexpected response format")

    items = data['result']
    processed_items = []

    for item in items:
        processed_item = {
            'id': int(item['ID']),
            'title': item['NAME']
        }
        processed_items.append(processed_item)

    return {
        'data': processed_items
    }

@router.post("/calendar/events")
async def calendar_events(date_range: DateRange):
    url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/crm.deal.list"
    params = {
        "select": [
            "ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "UF_CRM_1714583071",
            "UF_CRM_DEAL_1712137850471", "UF_CRM_DEAL_1712137877584", "UF_CRM_DEAL_1712137914328",
            "UF_CRM_1714663307", "UF_CRM_DEAL_1712138052482", "UF_CRM_DEAL_1712138132003",
            "UF_CRM_DEAL_1712138182738", "UF_CRM_DEAL_1712138239034", "OPPORTUNITY",
            "UF_CRM_DEAL_1712138336714", "UF_CRM_DEAL_1712138395258", "UF_CRM_DEAL_1712138457130",
            "UF_CRM_DEAL_1712138504154", "UF_CRM_DEAL_1712138530562", "UF_CRM_1714648360",
            "ASSIGNED_BY_ID", "CREATED_BY", "UF_CRM_DEAL_1712137787958", "UF_CRM_1714654129",
            'UF_CRM_1715507748', 'UF_CRM_1715508611'
        ],
        "filter": {
            'CATEGORY_ID': 7,
            '>=UF_CRM_DEAL_1712137850471': date_range.dateFrom.isoformat(),
            '<=UF_CRM_DEAL_1712137877584': date_range.dateTo.isoformat()
        }
    }

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from the provided URL: {str(e)}")

    data = response.json()

    if 'result' not in data:
        raise HTTPException(status_code=400, detail="Unexpected response format")

    items = data['result']
    processed_items = []

    for item in items:
        processed_item = {
            'id': int(item['ID']),
            'title': item['TITLE'],
            'stageId': item['STAGE_ID'],
            'opportunity': item['OPPORTUNITY'],
            'responsibleStaffList': item.get('UF_CRM_1714583071'),
            'dateFrom': item.get('UF_CRM_DEAL_1712137850471'),
            'dateTo': item.get('UF_CRM_DEAL_1712137877584'),
            'type': item.get('UF_CRM_DEAL_1712137914328'),
            'duration': item.get('UF_CRM_1714663307'),
            'department': item.get('UF_CRM_1715507748'),
            'rooms': item.get('UF_CRM_1715508611'),
            'seatsCount': item.get('UF_CRM_DEAL_1712138182738'),
            'contractType': item.get('UF_CRM_DEAL_1712138239034'),
            'price': item['OPPORTUNITY'],
            'requisites': item.get('UF_CRM_DEAL_1712138336714'),
            'actionPlaces': item.get('UF_CRM_DEAL_1712138395258'),
            'technicalSupportRequired': item.get('UF_CRM_DEAL_1712138457130'),
            'comments': item.get('UF_CRM_DEAL_1712138504154'),
            'eventDetails': item.get('UF_CRM_DEАЛ_1712138530562'),
            'contactFullName': item.get('UF_CRM_1714648360'),
            'assignedById': item['ASSIGNED_BY_ID'],
            'createdBy': item.get('CREATED_BY'),
            'description': item.get('UF_CRM_DEAL_1712137787958'),
            'techSupportNeeds': item.get('UF_CRM_1714654129')
        }
        processed_items.append(processed_item)

    return {
        'data': processed_items
    }

@router.post("/calendar/google")
async def calendar_google(google_url: GoogleUrl):
    if not google_url.googleUrl:
        raise HTTPException(status_code=400, detail="googleUrl is required")

    try:
        response = requests.get(google_url.googleUrl)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from the provided URL: {str(e)}")

    ics_data = response.text
    events = parse_ics_data(ics_data)

    return {
        'data': events
    }

def get_time_only(time_str, time_format='%Y-%m-%dT%H:%M:%S%z'):
    dt = datetime.strptime(time_str, time_format)
    return dt.time()

def get_minutes_difference(start_time, end_time):
    datetime_format = '%H:%M:%S'
    dummy_date = '2000-01-01'
    start_datetime = datetime.combine(datetime.strptime(dummy_date, '%Y-%m-%d'), start_time)
    end_datetime = datetime.combine(datetime.strptime(dummy_date, '%Y-%m-%d'), end_time)
    return (end_datetime - start_datetime).seconds // 60

@router.post("/calendar/report/day")
async def calendar_report_day(date: DateFrom):
    events_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/crm.deal.list"
    rooms_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.element.get.json"

    # Устанавливаем время для начала и конца дня
    date_from = date.dateFrom.replace(hour=0, minute=0, second=0, microsecond=0)
    date_to = date.dateFrom.replace(hour=23, minute=59, second=59, microsecond=0)

    events_params = {
        "select": [
            "ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "UF_CRM_1714583071",
            "UF_CRM_DEAL_1712137850471", "UF_CRM_DEAL_1712137877584", "UF_CRM_DEAL_1712137914328",
            "UF_CRM_1714663307", "UF_CRM_DEAL_1712138052482", "UF_CRM_DEAL_1712138132003",
            "UF_CRM_DEAL_1712138182738", "UF_CRM_DEAL_1712138239034", "OPPORTUNITY",
            "UF_CRM_DEAL_1712138336714", "UF_CRM_DEAL_1712138395258", "UF_CRM_DEAL_1712138457130",
            "UF_CRM_DEАЛ_1712138504154", "UF_CRM_DEАЛ_1712138530562", "UF_CRM_1714648360",
            "ASSIGNED_BY_ID", "CREATED_BY", "UF_CRM_DEАЛ_1712137787958", "UF_CRM_1714654129",
            'UF_CRM_1715507748', 'UF_CRM_1715508611'
        ],
        "filter": {
            'CATEGORY_ID': 7,
            '!=STAGE_ID': 'C7:NEW',
            '>=UF_CRM_DEAL_1712137850471': date_from.isoformat(),
            '<=UF_CRM_DEAL_1712137877584': date_to.isoformat()
        }
    }

    rooms_params = {
        "IBLOCK_TYPE_ID": "lists",
        "IBLOCK_ID": "78",
        "SECTION_ID": "0"
    }

    try:
        events_response = requests.post(events_url, json=events_params)
        events_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch events data from the provided URL: {str(e)}")

    try:
        rooms_response = requests.post(rooms_url, json=rooms_params)
        rooms_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch rooms data from the provided URL: {str(e)}")

    events_data = events_response.json()
    rooms_data = rooms_response.json()

    if 'result' not in events_data or 'result' not in rooms_data:
        raise HTTPException(status_code=400, detail="Unexpected response format")

    events_items = events_data['result']
    rooms_items = rooms_data['result']

    processed_events = []
    processed_rooms = []

    for item in events_items:
        processed_event = {
            'id': int(item['ID']),
            'title': item['TITLE'],
            'dateFrom': item.get('UF_CRM_DEAL_1712137850471'),
            'dateTo': item.get('UF_CRM_DEAL_1712137877584'),
            'rooms': int(item.get('UF_CRM_1715508611', 0))  # Преобразуем rooms в число
        }
        processed_events.append(processed_event)

    room_time_format = '%d.%m.%Y %H:%M:%S'
    event_time_format = '%Y-%m-%dT%H:%M:%S%z'

    for item in rooms_items:
        room_id = int(item['ID'])
        room_date_from_str = list(item['PROPERTY_316'].values())[0]
        room_date_to_str = list(item['PROPERTY_317'].values())[0]

        room_date_from = get_time_only(room_date_from_str, room_time_format)
        room_date_to = get_time_only(room_date_to_str, room_time_format)

        total_room_minutes = get_minutes_difference(room_date_from, room_date_to)

        room_events = [event for event in processed_events if event['rooms'] == room_id]

        total_event_minutes = 0
        for event in room_events:
            event_date_from = get_time_only(event['dateFrom'], event_time_format)
            event_date_to = get_time_only(event['dateTo'], event_time_format)

            actual_start = max(room_date_from, event_date_from)
            actual_end = min(room_date_to, event_date_to)

            if actual_start < actual_end:
                total_event_minutes += get_minutes_difference(actual_start, actual_end)

        processed_room = {
            'id': room_id,
            'title': item['NAME'],
            'hours': total_event_minutes / 60,
            'percents': (total_event_minutes / total_room_minutes) * 100 if total_room_minutes > 0 else 0,
            'color': list(item['PROPERTY_318'].values())[0],
            'dateFrom': list(item['PROPERTY_316'].values())[0],
            'dateTo': list(item['PROPERTY_317'].values())[0],
        }
        processed_rooms.append(processed_room)

    return {
        "data": processed_rooms
    }

@router.post("/calendar/report/range")
async def calendar_report_range(date_range: DateRange):
    events_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/crm.deal.list"
    rooms_url = "https://intranet.gctm.ru/rest/1552/0ja3gbkg3kxex6aj/lists.element.get.json"

    # Устанавливаем время для начала и конца периода
    date_from = date_range.dateFrom.replace(hour=0, minute=0, second=0, microsecond=0)
    date_to = date_range.dateTo.replace(hour=23, minute=59, second=59, microsecond=0)

    events_params = {
        "select": [
            "ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "UF_CRM_1714583071",
            "UF_CRM_DEAL_1712137850471", "UF_CRM_DEAL_1712137877584", "UF_CRM_DEAL_1712137914328",
            "UF_CRM_1714663307", "UF_CRM_DEAL_1712138052482", "UF_CRM_DEAL_1712138132003",
            "UF_CRM_DEAL_1712138182738", "UF_CRM_DEAL_1712138239034", "OPPORTUNITY",
            "UF_CRM_DEAL_1712138336714", "UF_CRM_DEAL_1712138395258", "UF_CRM_DEAL_1712138457130",
            "UF_CRM_DEAL_1712138504154", "UF_CRM_DEAL_1712138530562", "UF_CRM_1714648360",
            "ASSIGNED_BY_ID", "CREATED_BY", "UF_CRM_DEAL_1712137787958", "UF_CRM_1714654129",
            'UF_CRM_1715507748', 'UF_CRM_1715508611'
        ],
        "filter": {
            'CATEGORY_ID': 7,
            '!=STAGE_ID': 'C7:NEW',
            '>=UF_CRM_DEAL_1712137850471': date_from.isoformat(),
            '<=UF_CRM_DEAL_1712137877584': date_to.isoformat()
        }
    }

    rooms_params = {
        "IBLOCK_TYPE_ID": "lists",
        "IBLOCK_ID": "78",
        "SECTION_ID": "0"
    }

    try:
        events_response = requests.post(events_url, json=events_params)
        events_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch events data from the provided URL: {str(e)}")

    try:
        rooms_response = requests.post(rooms_url, json=rooms_params)
        rooms_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch rooms data from the provided URL: {str(e)}")

    events_data = events_response.json()
    rooms_data = rooms_response.json()

    if 'result' not in events_data or 'result' not in rooms_data:
        raise HTTPException(status_code=400, detail="Unexpected response format")

    events_items = events_data['result']
    rooms_items = rooms_data['result']

    processed_events = []
    processed_rooms = []

    for item in events_items:
        if not item.get('UF_CRM_DEAL_1712137850471') or not item.get('UF_CRM_DEAL_1712137877584'):
            continue

        processed_event = {
            'id': int(item['ID']),
            'title': item['TITLE'],
            'dateFrom': item.get('UF_CRM_DEAL_1712137850471'),
            'dateTo': item.get('UF_CRM_DEAL_1712137877584'),
            'rooms': int(item.get('UF_CRM_1715508611', 0))  # Преобразуем rooms в число
        }
        processed_events.append(processed_event)

    room_time_format = '%d.%m.%Y %H:%M:%S'
    event_time_format = '%Y-%m-%dT%H:%M:%S%z'

    # Вычисляем длительность периода в днях
    total_days = (date_to - date_from).days + 1

    for item in rooms_items:
        room_id = int(item['ID'])
        room_date_from_str = list(item['PROPERTY_316'].values())[0]
        room_date_to_str = list(item['PROPERTY_317'].values())[0]

        room_date_from = get_time_only(room_date_from_str, room_time_format)
        room_date_to = get_time_only(room_date_to_str, room_time_format)

        # Умножаем общее количество минут за день на количество дней
        total_room_minutes = get_minutes_difference(room_date_from, room_date_to) * total_days

        room_events = [event for event in processed_events if event['rooms'] == room_id]

        total_event_minutes = 0
        for event in room_events:
            event_date_from = get_time_only(event['dateFrom'], event_time_format)
            event_date_to = get_time_only(event['dateTo'], event_time_format)

            actual_start = max(room_date_from, event_date_from)
            actual_end = min(room_date_to, event_date_to)

            if actual_start < actual_end:
                total_event_minutes += get_minutes_difference(actual_start, actual_end)

        processed_room = {
            'id': room_id,
            'title': item['NAME'],
            'section': int(item.get('IBLOCK_SECTION_ID', 0)),
            'hours': total_event_minutes / 60,
            'percents': (total_event_minutes / total_room_minutes) * 100 if total_room_minutes > 0 else 0,
            'color': list(item['PROPERTY_318'].values())[0],
            'dateFrom': list(item['PROPERTY_316'].values())[0],
            'dateTo': list(item['PROPERTY_317'].values())[0],
        }
        processed_rooms.append(processed_room)

    return {
        "data": processed_rooms
    }
