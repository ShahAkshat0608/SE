from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class EmailNotificationBase(BaseModel):
    user_id: int
    email: EmailStr
    subject: str
    body: str

class EmailNotificationCreate(EmailNotificationBase):
    pass

class EmailNotificationUpdate(BaseModel):
    status: str
    sent_at: Optional[datetime] = None

class EmailNotificationResponse(EmailNotificationBase):
    id: int
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CalendarEventBase(BaseModel):
    user_id: int
    email: EmailStr
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    status: str
    event_id: Optional[str] = None

class CalendarEventResponse(CalendarEventBase):
    id: int
    status: str
    created_at: datetime
    event_id: Optional[str] = None

    class Config:
        orm_mode = True 