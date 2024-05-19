from pydantic import BaseModel
from datetime import datetime

class GoogleUrl(BaseModel):
    googleUrl: str

class DateRange(BaseModel):
    dateFrom: datetime
    dateTo: datetime

class DateFrom(BaseModel):
    dateFrom: datetime