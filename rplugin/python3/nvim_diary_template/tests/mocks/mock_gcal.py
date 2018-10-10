from datetime import date
from typing import List

from ...classes.calendar_event_class import CalendarEvent


class MockGCalService:
    def __init__(self) -> None:
        self.active = True
        self.events: List[CalendarEvent] = []

    def get_events_for_date(self, date_today: date) -> List[CalendarEvent]:
        return self.events
