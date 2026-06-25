from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

LOAN_STATUSES = Literal["active", "returned", "overdue"]


class LoanCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    device_id: int = Field(..., gt=0)


class LoanUpdate(BaseModel):
    status: LOAN_STATUSES


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: str

    model_config = ConfigDict(from_attributes=True)


class UserBrief(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class DeviceBrief(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    loan_id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime] = None
    user: UserBrief
    device: DeviceBrief
