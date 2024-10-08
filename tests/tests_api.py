from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel
import pytest

client = TestClient(app)

# Fixture to create a new database for testing
@pytest.fixture(scope="module")
def test_db():
    # Create test database
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Drop the test database
    SQLModel.metadata.drop_all(bind=engine)

def test_create_coupon(test_db):
    response = client.post("/api/coupons", json={
        "code": "TEST_COUPON",
        "repeat_counts": {
            "user_total": 2,
            "user_daily": 1,
            "user_weekly": 1,
            "global_total": 5
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST_COUPON"

def test_verify_coupon_valid(test_db):
    response = client.get("/api/coupons/verify", params={"code": "TEST_COUPON", "user_id": "user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True

def test_apply_coupon(test_db):
    response = client.post("/api/coupons/apply", json={"code": "TEST_COUPON", "user_id": "user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "applied"

def test_user_daily_limit(test_db):
    # Try to apply coupon again on the same day
    response = client.post("/api/coupons/apply", json={"code": "TEST_COUPON", "user_id": "user1"})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User daily repeat count exceeded"

def test_global_limit(test_db):
    # Apply coupon until global limit is reached
    users = ["user2", "user3", "user4", "user5"]
    for user in users:
        response = client.post("/api/coupons/apply", json={"code": "TEST_COUPON", "user_id": user})
        assert response.status_code == 200
    # Next application should fail
    response = client.post("/api/coupons/apply", json={"code": "TEST_COUPON", "user_id": "user6"})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Global usage limit reached"