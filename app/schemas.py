# app/schemas.py

from sqlmodel import SQLModel
from typing import Optional

class RepeatCounts(SQLModel):
    user_total: Optional[int] = None
    user_daily: Optional[int] = None
    user_weekly: Optional[int] = None
    global_total: int

class CreateCoupon(SQLModel):
    code: str
    repeat_counts: RepeatCounts

class VerifyCouponResponse(SQLModel):
    code: str
    is_valid: bool
    message: str

class ApplyCouponRequest(SQLModel):
    code: str
    user_id: str