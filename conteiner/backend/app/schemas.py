from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    check_type: str
    check_target: str
    frequency: int

class ServiceCreate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: int
    is_active: bool
    last_checked_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)

class HealthCheckOut(BaseModel):
    id: int
    service_id: int
    status: str
    response_time: Optional[float]
    error_message: Optional[str]
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)
