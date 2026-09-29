import logging
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import configure_logging
from app.main import app
from app.repositories.lead_repository import save_lead
from app.services.lead_service import create_lead_service

client = TestClient(app, raise_server_exceptions=False)


def test_create_lead_success():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Lead analyzed successfully"
    assert data["lead"]["name"] == "Test Lead"
    assert data["lead"]["company_size"] == 25
    assert "analysis" in data

def test_create_lead_negative_company_size():
    response = client.post(
        "/leads",
        json={
            "name": "Invalid Lead",
            "company": "Test Company",
            "message": "This is an invalid test message",
            "company_size": -10,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "greater_than_equal"
    assert data["detail"][0]["loc"] == ["body", "company_size"]

def test_create_lead_missing_name():
    response = client.post(
        "/leads",
        json={
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422
    data = response.json()

    assert data["detail"][0]["loc"] == ["body", "name"]

def test_create_lead_short_message():
    response = client.post(
        "/leads",
        json={
            "name": "Invalid Lead",
            "company": "Test Company",
            "message": "Hi",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

def test_create_lead_missing_message():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "message"]

def test_create_lead_missing_company():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "company"]

def test_create_lead_missing_company_size():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "company_size"]

def test_create_lead_empty_name():
    response = client.post(
        "/leads",
        json={
            "name": "",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "string_too_short"
    assert data["detail"][0]["loc"] == ["body", "name"]

def test_create_lead_empty_company():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "string_too_short"
    assert data["detail"][0]["loc"] == ["body", "company"]

def test_create_lead_empty_message():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["type"] == "string_too_short"
    assert data["detail"][0]["loc"] == ["body", "message"]

def test_create_lead_invalid_company_size_type():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": "large",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == ["body", "company_size"]

def test_create_lead_invalid_name_type():
    response = client.post(
        "/leads",
        json={
            "name": 123,
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == ["body", "name"]

def test_create_lead_invalid_message_type():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": 12345,
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == ["body", "message"]


def test_create_lead_invalid_company_type():
    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": 123,
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == ["body", "company"]


def test_invalid_endpoint():
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404

def test_get_nonexistent_lead():
    response = client.get("/leads/99999")

    assert response.status_code == 404

def test_get_lead_success():
    create_response = client.post(
        "/leads",
        json={
            "name": "Get Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert create_response.status_code == 200

    print(create_response.json())

    lead_id = create_response.json()["lead"]["id"]

    response = client.get(f"/leads/{lead_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == lead_id
    assert data["name"] == "Get Test Lead"
    assert data["company"] == "Test Company"

def test_get_lead_not_found():
    response = client.get("/leads/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead not found"

def test_get_lead_response_structure():
    create_response = client.post(
        "/leads",
        json={
            "name": "Structure Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert create_response.status_code == 200

    lead_id = create_response.json()["lead"]["id"]

    response = client.get(f"/leads/{lead_id}")

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "id",
        "name",
        "company",
        "company_size",
        "message",
        "score",
        "priority",
        "recommendation",
    }

    assert expected_fields.issubset(data.keys())



def test_save_lead_rolls_back_on_database_error():
    db = Mock()
    lead_db = Mock()

    db.commit.side_effect = SQLAlchemyError("Database failure")

    with pytest.raises(SQLAlchemyError, match="Database failure"):
        save_lead(db, lead_db)

    db.rollback.assert_called_once()


def test_create_lead_service_logs_database_error(caplog, monkeypatch):
    lead = Mock(
        name="Test Lead",
        company="Test Company",
        message="This is a valid test message",
        company_size=25,
    )

    db = Mock()

    def fail_to_save_lead(db, lead_db):
        raise SQLAlchemyError("Database failure")

    monkeypatch.setattr(
        "app.services.lead_service.save_lead",
        fail_to_save_lead,
    )

    with caplog.at_level(logging.ERROR), pytest.raises(
        SQLAlchemyError,
        match="Database failure",
    ):
        create_lead_service(lead, db)

    assert "Failed to create lead: company=Test Company" in caplog.text

def test_create_lead_service_logs_success(caplog,monkeypatch):
    lead = Mock(
        name="Test Lead",
        company="Test Company",
        message="This is a valid test message",
        company_size=25,
    )

    db = Mock()

    saved_lead = Mock(
        id=123,
        company="Test Company",
        score=80,
        priority="high",
    )

    def mock_save_lead(db, lead_db):
        return saved_lead

    monkeypatch.setattr(
        "app.services.lead_service.save_lead",
        mock_save_lead,
    )

    with caplog.at_level(logging.INFO):
        create_lead_service(lead, db)

    assert "Lead created successfully" in caplog.text
    assert "id=123" in caplog.text
    assert "company=Test Company" in caplog.text

def test_configure_logging_sets_info_level(monkeypatch):
    monkeypatch.setattr(
        "app.core.config.APP_ENV",
        "development",
    )

    logging.getLogger().setLevel(logging.NOTSET)

    configure_logging()

    assert logging.getLogger().level == logging.INFO

def test_create_lead_returns_500_on_database_error(monkeypatch):
    def fail_create_lead_service(lead, db):
        raise SQLAlchemyError("Database failure")

    monkeypatch.setattr(
        "app.routes.leads.create_lead_service",
        fail_create_lead_service,
    )

    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
    }

    
def test_create_lead_returns_500_on_unexpected_error(monkeypatch):
    def fail_create_lead_service(lead, db):
      raise AttributeError("Unexpected programming error")

    monkeypatch.setattr(
        "app.routes.leads.create_lead_service",
        fail_create_lead_service,
    )

    response = client.post(
        "/leads",
        json={
            "name": "Test Lead",
            "company": "Test Company",
            "message": "This is a valid test message",
            "company_size": 25,
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
    }

def test_readiness_returns_503_when_database_is_unavailable(monkeypatch):
    mock_engine = Mock()
    mock_engine.connect.side_effect = SQLAlchemyError("Database unavailable")

    monkeypatch.setattr("app.main.engine", mock_engine)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "unavailable",
    }