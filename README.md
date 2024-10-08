## Coupon Service

### Tech Stack
- FastAPI
- SQLAlchemy

## Running the service
- Clone the repository
- Install the dependencies
```bash
poetry install
```
- Run the service
```bash
uvicorn app.main:app
```

## API Documentation
- Swagger UI: http://localhost:8000/docs

## Running the tests
```bash
pytest
```

## Testing API Endpoints

1. Add Repeat Counts to a Coupon Code
```bash
curl -X POST "http://127.0.0.1:8000/api/coupons" \
  -H "Content-Type: application/json" \
  -d '{
        "code": "SUMMER_SALE",
        "repeat_counts": {
          "user_total": 3,
          "user_daily": 1,
          "user_weekly": 1,
          "global_total": 10000
        }
      }'
```

2. Verify a Coupon Code Validity
```bash
curl -X GET "http://127.0.0.1:8000/api/coupons/verify?code=SUMMER_SALE&user_id=user123"
```

3. Redeem a Coupon Code
```bash
curl -X POST "http://127.0.0.1:8000/api/coupons/apply" \
  -H "Content-Type: application/json" \
  -d '{
        "code": "SUMMER_SALE",
        "user_id": "user123"
      }'
```

## Future Improvements

### Trade-offs
- The current implementation uses an in-memory database for simplicity. For production use, we should use a persistent database like PostgreSQL.
- The CouponUsage table can grow large over time. In this implementation, we query this table frequently, which might affect performance. Indexing and archiving old data can help mitigate this.

### Scalability Challenges
- With many users applying coupons simultaneously, there may be race conditions leading to overuse of coupons beyond their limits.
- Caching coupon configurations can reduce database load but may lead to stale data.
- Using a asynchronous implementation can help in handling more requests concurrently.
