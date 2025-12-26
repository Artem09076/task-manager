from google.oauth2 import service_account
from googleapiclient.discovery import build
from config.settings import settings


class GoogleCalendarClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_JSON,
            scopes=[settings.GOOGLE_CALENDAR_SCOPES],
        )
        self.service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)


    def list_events(self, calendar_id: str) -> list[dict]:
        res = (self.service.events().list(
            calendarId=calendar_id,
            singleEvents=True,
            orderBy='updated'
        ).execute())
        print(res)
        return res.get('items', [])