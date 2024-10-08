from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from app import models, schemas
from app.logger import logger

def create_coupon(db: Session, coupon: schemas.CreateCoupon) -> dict:
    db_coupon = models.CouponCode(
        code=coupon.code,
        global_total_repeat_count=coupon.repeat_counts.global_total,
    )
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)

    # Create repeat config
    db_config = models.CouponRepeatConfig(
        coupon_code_code=coupon.code,
        user_total_repeat_count=coupon.repeat_counts.user_total,
        user_daily_repeat_count=coupon.repeat_counts.user_daily,
        user_weekly_repeat_count=coupon.repeat_counts.user_weekly,
    )
    db.add(db_config)

    # Initialize global usage
    db_global_usage = models.GlobalCouponUsage(
        coupon_code_code=coupon.code,
        usage_count=0
    )
    db.add(db_global_usage)
    db.commit()
    logger.info(f"Created coupon: {db_coupon.code} \n " 
                f"Repeat config: {db_coupon.repeat_config} \n"
                f"Global usage: {db_coupon.global_usage} \n"
                f"User usage: {db_coupon.usages} \n")
    return db_coupon

def get_coupon(db: Session, code: str) -> dict:
    statement = select(models.CouponCode).where(models.CouponCode.code == code)
    result = db.exec(statement).first()
    logger.info(f"Get coupon: {result}")
    logger.info(f"Get coupon type: {type(result)}")
    return result

def get_user_usage_counts(db: Session, code: str, user_id: str) -> dict:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=today_start.weekday())

    # Total usage
    statement = select(func.count(models.CouponUsage.id)).where(
        models.CouponUsage.coupon_code_code == code,
        models.CouponUsage.user_id == user_id
    )
    total_usage = db.exec(statement).first()
    logger.info(f"Total usage: {total_usage}")


    # Daily usage
    statement = select(func.count(models.CouponUsage.id)).where(
        models.CouponUsage.coupon_code_code == code,
        models.CouponUsage.user_id == user_id,
        models.CouponUsage.used_at >= today_start
    )
    daily_usage = db.exec(statement).first()
    logger.info(f"Daily usage: {daily_usage}")

    # Weekly usage
    statement = select(func.count(models.CouponUsage.id)).where(
        models.CouponUsage.coupon_code_code == code,
        models.CouponUsage.user_id == user_id,
        models.CouponUsage.used_at >= week_start
    )
    weekly_usage = db.exec(statement).first()
    logger.info(f"Weekly usage: {weekly_usage}")

    return {
        "total_usage": total_usage,
        "daily_usage": daily_usage,
        "weekly_usage": weekly_usage
    }

def get_global_usage(db: Session, code: str) -> int:
    statement = select(models.GlobalCouponUsage).where(
        models.GlobalCouponUsage.coupon_code_code == code
    )
    usage = db.exec(statement).first()
    logger.info(f"Global usage: {usage.usage_count}")
    return usage.usage_count if usage else 0

def increment_usage(db: Session, code: str, user_id: str) -> int:
    # Record user usage
    db_usage = models.CouponUsage(
        coupon_code_code=code,
        user_id=user_id
    )
    db.add(db_usage)

    # Increment global usage
    statement = select(models.GlobalCouponUsage).where(
        models.GlobalCouponUsage.coupon_code_code == code
    )
    global_usage = db.exec(statement).first()
    if global_usage:
        global_usage.usage_count += 1
        db.add(global_usage)
    db.commit()
    logger.info(f"Global usage incremented: {global_usage.usage_count}")
    return global_usage.usage_count