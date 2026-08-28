from datetime import timedelta
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID")
SERVICE_ACCOUNT_FILE = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

def create_event(calendar_id: str, summary: str, description: str, start_time, duration_minutes: int = 60) -> str:
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Europe/Kyiv",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Europe/Kyiv",
        },
    }

    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event.get("id")

def delete_event(calendar_id: str, event_id: str):
    if not event_id:
        return
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"Подію {event_id} успішно видалено з Google Calendar")
    except Exception as e:
        print(f"Помилка при видаленні події з Google Calendar: {e}")

def get_busy_hours(date_str: str) -> list:
    try:
        time_min = f"{date_str}T00:00:00Z"
        time_max = f"{date_str}T23:59:59Z"

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        busy_hours = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            if "T" in start:
                time_part = start.split("T")[1][:5]
                busy_hours.append(time_part)

        return busy_hours
    except Exception as e:
        print(f"Помилка отримання зайнятого часу: {e}")
        return []