from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class CouponCode(SQLModel, table=True):
    code: str = Field(primary_key=True, index=True)
    global_total_repeat_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    repeat_config: "CouponRepeatConfig" = Relationship(
        back_populates="coupon_code", sa_relationship_kwargs={"uselist": False}
    )
    usages: List["CouponUsage"] = Relationship(
        back_populates="coupon_code"
    )
    global_usage: Optional["GlobalCouponUsage"] = Relationship(
        back_populates="coupon_code", sa_relationship_kwargs={"uselist": False}
    )

class CouponRepeatConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    coupon_code_code: str = Field(
        foreign_key="couponcode.code", unique=True
    )
    user_total_repeat_count: Optional[int]
    user_daily_repeat_count: Optional[int]
    user_weekly_repeat_count: Optional[int]

    coupon_code: CouponCode = Relationship(
        back_populates="repeat_config"
    )

class CouponUsage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    coupon_code_code: str = Field(foreign_key="couponcode.code")
    user_id: str
    used_at: datetime = Field(default_factory=datetime.utcnow)

    coupon_code: CouponCode = Relationship(back_populates="usages")

class GlobalCouponUsage(SQLModel, table=True):
    coupon_code_code: str = Field(
        foreign_key="couponcode.code", primary_key=True
    )
    usage_count: int = Field(default=0)

    coupon_code: CouponCode = Relationship(back_populates="global_usage")