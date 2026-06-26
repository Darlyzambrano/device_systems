from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

DEVICE_TYPES = Literal["laptop", "tablet", "proyector", "camara", "router", "monitor"]


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=3)
    serial_number: str = Field(..., min_length=3)
    device_type: DEVICE_TYPES
    brand: Optional[str] = None
    is_available: bool = True


class DeviceUpdate(BaseModel):
    name: str = Field(..., min_length=3)
    serial_number: str = Field(..., min_length=3)
    device_type: DEVICE_TYPES
    brand: Optional[str] = None
    is_available: bool


class DevicePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    serial_number: Optional[str] = Field(None, min_length=3)
    device_type: Optional[DEVICE_TYPES] = None
    brand: Optional[str] = None
    is_available: Optional[bool] = None


class DeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str]
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
