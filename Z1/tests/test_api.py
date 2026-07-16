import os
from datetime import date

from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("Z1_BOOTSTRAP_ADMIN_PASSWORD", "admin")

from backend.main import app

_BEARER = "Bearer"


def _auth(client: TestClient) -> dict:
    resp = client.post("/auth/token", json={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": " ".join((_BEARER, token))}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_success() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_login_and_dashboard() -> None:
    with TestClient(app) as client:
        token_response = client.post("/auth/token", json={"username": "admin", "password": "admin"})
        assert token_response.status_code == 200

        token = token_response.json()["access_token"]
        auth_header = {"Authorization": " ".join((_BEARER, token))}
        response = client.get("/dashboard/summary", headers=auth_header)
        assert response.status_code == 200
        assert "finance" in response.json()


def test_unauthenticated_request_returns_401() -> None:
    with TestClient(app) as client:
        assert client.get("/dashboard/summary").status_code == 401


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def test_user_crud() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        r = client.post("/users", json={"username": "testuser", "password": "securepass", "role": "viewer"}, headers=headers)
        assert r.status_code == 201
        uid = r.json()["id"]

        assert client.get("/users/" + str(uid), headers=headers).status_code == 200
        users = client.get("/users", headers=headers).json()
        assert any(u["id"] == uid for u in users)

        r = client.put("/users/" + str(uid), json={"role": "editor"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["role"] == "editor"

        assert client.delete("/users/" + str(uid), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Electra
# ---------------------------------------------------------------------------

def test_electra_wind_farm_crud() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        farm_data = {"name": "Nordwind Alpha", "location": "Hamburg", "capacity_kw": 5000.0}
        r = client.post("/electra/wind-farms", json=farm_data, headers=headers)
        assert r.status_code == 201
        farm_id = r.json()["id"]

        assert client.get("/electra/wind-farms/" + str(farm_id), headers=headers).status_code == 200

        r = client.put("/electra/wind-farms/" + str(farm_id), json={"status": "maintenance"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "maintenance"

        reading = {"timestamp": "2026-01-01T12:00:00", "production_kwh": 450.5, "wind_speed_ms": 12.3}
        r = client.post("/electra/wind-farms/" + str(farm_id) + "/readings", json=reading, headers=headers)
        assert r.status_code == 201

        contract = {
            "wind_farm_id": farm_id,
            "name": "Vertrag A",
            "counterparty": "Stadtwerke GmbH",
            "price_per_kwh": 0.085,
            "start_date": "2026-01-01",
        }
        assert client.post("/electra/contracts", json=contract, headers=headers).status_code == 201

        summary = client.get("/electra/summary", headers=headers).json()
        assert "total_farms" in summary

        assert client.delete("/electra/wind-farms/" + str(farm_id), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Gaia
# ---------------------------------------------------------------------------

def test_gaia_property_crud() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        prop_data = {
            "name": "Musterwohnung",
            "address": "Hauptstrasse 1",
            "city": "Berlin",
            "property_type": "apartment",
            "area_sqm": 75.0,
            "monthly_rent": 1200.0,
        }
        r = client.post("/gaia/properties", json=prop_data, headers=headers)
        assert r.status_code == 201
        prop_id = r.json()["id"]

        tenant = {"property_id": prop_id, "name": "Max Mustermann", "lease_start": "2026-01-01", "monthly_rent": 1200.0}
        assert client.post("/gaia/properties/" + str(prop_id) + "/tenants", json=tenant, headers=headers).status_code == 201

        maint = {"property_id": prop_id, "title": "Heizung defekt", "priority": "high"}
        r = client.post("/gaia/maintenance", json=maint, headers=headers)
        assert r.status_code == 201
        maint_id = r.json()["id"]
        assert client.put("/gaia/maintenance/" + str(maint_id), json={"status": "resolved"}, headers=headers).status_code == 200

        summary = client.get("/gaia/summary", headers=headers).json()
        assert "total_properties" in summary

        assert client.delete("/gaia/properties/" + str(prop_id), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Fortuna
# ---------------------------------------------------------------------------

def test_fortuna_transactions() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        r = client.post("/fortuna/categories", json={"name": "Miete", "category_type": "income", "color": "#4caf50"}, headers=headers)
        assert r.status_code == 201
        cat_id = r.json()["id"]

        tx = {
            "transaction_date": str(date.today()),
            "description": "Mieteinnahme Jan",
            "amount": 1200.0,
            "transaction_type": "income",
            "category_id": cat_id,
        }
        r = client.post("/fortuna/transactions", json=tx, headers=headers)
        assert r.status_code == 201
        tx_id = r.json()["id"]

        assert len(client.get("/fortuna/transactions", headers=headers).json()) >= 1

        summary = client.get("/fortuna/summary", headers=headers).json()
        assert summary["total_income"] >= 1200.0

        assert client.delete("/fortuna/transactions/" + str(tx_id), headers=headers).status_code == 204
        assert client.delete("/fortuna/categories/" + str(cat_id), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Themis
# ---------------------------------------------------------------------------

def test_themis_contracts() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        contract = {
            "title": "Mietvertrag Hauptstrasse 1",
            "counterparty": "Max Mustermann",
            "contract_type": "rental",
            "status": "active",
            "start_date": "2026-01-01",
            "value": 14400.0,
        }
        r = client.post("/themis/contracts", json=contract, headers=headers)
        assert r.status_code == 201
        cid = r.json()["id"]

        dl = {"contract_id": cid, "title": "Verlaengerungsoption", "due_date": "2027-01-01"}
        r = client.post("/themis/contracts/" + str(cid) + "/deadlines", json=dl, headers=headers)
        assert r.status_code == 201
        dl_id = r.json()["id"]

        summary = client.get("/themis/summary", headers=headers).json()
        assert summary["active_contracts"] >= 1

        assert client.delete("/themis/deadlines/" + str(dl_id), headers=headers).status_code == 204
        assert client.delete("/themis/contracts/" + str(cid), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Diplomatia
# ---------------------------------------------------------------------------

def test_diplomatia_documents() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        doc = {
            "title": "Memo Q1",
            "language": "de",
            "document_type": "memo",
            "content": "Zusammenfassung Q1 2026.",
            "tags": "memo,q1",
        }
        r = client.post("/diplomatia/documents", json=doc, headers=headers)
        assert r.status_code == 201
        doc_id = r.json()["id"]

        r = client.post("/diplomatia/documents/" + str(doc_id) + "/archive", headers=headers)
        assert r.status_code == 200
        assert r.json()["is_archived"] is True

        corr = {
            "subject": "Re: Q1",
            "sender": "admin@z1.de",
            "recipient": "board@z1.de",
            "sent_date": str(date.today()),
            "document_id": doc_id,
        }
        assert client.post("/diplomatia/correspondence", json=corr, headers=headers).status_code == 201

        summary = client.get("/diplomatia/summary", headers=headers).json()
        assert summary["archived_documents"] >= 1

        assert client.delete("/diplomatia/documents/" + str(doc_id), headers=headers).status_code == 204


# ---------------------------------------------------------------------------
# Astraea
# ---------------------------------------------------------------------------

def test_astraea_backups() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        r = client.post("/astraea/backups", json={"filename": "backup_2026_01.sql"}, headers=headers)
        assert r.status_code == 201
        assert r.json()["status"] == "completed"

        assert len(client.get("/astraea/backups", headers=headers).json()) >= 1

        summary = client.get("/astraea/summary", headers=headers).json()
        assert summary["total_backups"] >= 1


# ---------------------------------------------------------------------------
# Zoe
# ---------------------------------------------------------------------------

def test_zoe_tasks_and_dispatch() -> None:
    with TestClient(app) as client:
        headers = _auth(client)

        r = client.post("/zoe/tasks", json={"title": "Windpark Bericht erstellen", "priority": "high", "assigned_module": "electra"}, headers=headers)
        assert r.status_code == 201
        task_id = r.json()["id"]

        r = client.post("/zoe/memory", json={"key": "last_report_date", "value": "2026-01-01", "context": "electra"}, headers=headers)
        assert r.status_code == 201

        r = client.put("/zoe/memory/last_report_date", json={"value": "2026-07-01", "context": "electra"}, headers=headers)
        assert r.status_code == 200

        r = client.post("/zoe/dispatch", json={"prompt": "Wie viel Energie hat der Windpark produziert?"}, headers=headers)
        assert r.status_code == 200
        body = r.json()
        assert body["routed_to"] == "electra"
        assert "run_id" in body

        summary = client.get("/zoe/summary", headers=headers).json()
        assert summary["total_tasks"] >= 1

        assert client.delete("/zoe/tasks/" + str(task_id), headers=headers).status_code == 204
        assert client.delete("/zoe/memory/last_report_date", headers=headers).status_code == 204
