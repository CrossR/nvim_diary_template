from typing import List

from ...classes.calendar_event_class import CalendarEvent


class MockGCalService:
    def __init__(self) -> None:
        self.active = True
        self.events: List[CalendarEvent] = []