from pydantic import BaseModel
from typing import List


class CalendarEvent(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    event_type: str
    start_time: str
    end_time: str
    attendees: List[str]
    created_at: str


class CalendarEventCreate(BaseModel):
    title: str
    description: str
    event_type: str
    start_time: str
    end_time: str
    attendees: List[str]
