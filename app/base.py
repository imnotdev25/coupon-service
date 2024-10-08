from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import schemas, crud
from app.database import get_session
from app.logger import logger
import json
router = APIRouter()


@router.post("/api/coupons", response_model=schemas.CreateCoupon)
def add_repeat_counts_to_coupon(coupon: schemas.CreateCoupon, db: Session = Depends(get_session)):
    existing_coupon = crud.get_coupon(db, coupon.code)
    logger.info(f"Existing coupon: {existing_coupon}")
    if existing_coupon:
        logger.error(f"Coupon code already exists: {coupon.code}")
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    crud.create_coupon(db, coupon)
    return coupon


@router.get("/api/coupons/verify", response_model=schemas.VerifyCouponResponse)
def verify_coupon_code(code: str, user_id: str, db: Session = Depends(get_session)):
    coupon = crud.get_coupon(db, code)
    if not coupon:
        return schemas.VerifyCouponResponse(code=code, is_valid=False, message="Coupon code does not exist")

    config = coupon.repeat_config
    user_usages = crud.get_user_usage_counts(db, code, user_id)
    global_usage = crud.get_global_usage(db, code)

    # Check global total repeat count
    if global_usage >= coupon.global_total_repeat_count:
        return schemas.VerifyCouponResponse(code=code, is_valid=False, message="Global usage limit reached")

    # Check user total repeat count
    if config.user_total_repeat_count is not None and user_usages["total_usage"] >= config.user_total_repeat_count:
        return schemas.VerifyCouponResponse(code=code, is_valid=False, message="User total repeat count exceeded")

    # Check user daily repeat count
    if config.user_daily_repeat_count is not None and user_usages["daily_usage"] >= config.user_daily_repeat_count:
        return schemas.VerifyCouponResponse(code=code, is_valid=False, message="User daily repeat count exceeded")

    # Check user weekly repeat count
    if config.user_weekly_repeat_count is not None and user_usages["weekly_usage"] >= config.user_weekly_repeat_count:
        return schemas.VerifyCouponResponse(code=code, is_valid=False, message="User weekly repeat count exceeded")

    return schemas.VerifyCouponResponse(code=code, is_valid=True, message="Coupon is valid for use")


@router.post("/api/coupons/apply")
def apply_coupon_code(request: schemas.ApplyCouponRequest, db: Session = Depends(get_session)):
    verification = verify_coupon_code(request.code, request.user_id, db)
    if not verification.is_valid:
        raise HTTPException(status_code=400, detail=verification.message)

    # Apply the coupon
    crud.increment_usage(db, request.code, request.user_id)
    return {"code": request.code, "status": "applied", "message": "Coupon applied successfully"}
