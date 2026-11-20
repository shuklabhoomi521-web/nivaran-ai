from fastapi.testclient import TestClient

from app.main import app


def client(host="testclient"):
    return TestClient(app, client=(host, 50000))


def test_without_a_token_only_this_computer_is_answered(monkeypatch):
    monkeypatch.delenv("NIVARAN_API_TOKEN", raising=False)
    assert client("127.0.0.1").get("/tracked-cases/consent-notice").status_code == 200
    assert client("::1").get("/tracked-cases/consent-notice").status_code == 200
    r = client("192.168.1.50").get("/tracked-cases/consent-notice")
    assert r.status_code == 401 and "NIVARAN_API_TOKEN" in r.json()["detail"]
    assert client("192.168.1.50").get("/health").status_code == 200                      # health stays open


def test_with_a_token_every_route_needs_it_from_everyone(monkeypatch):
    monkeypatch.setenv("NIVARAN_API_TOKEN", "pilot-secret-not-real")
    c = client("192.168.1.50")
    assert c.get("/tracked-cases/consent-notice").status_code == 401
    assert c.get("/tracked-cases/consent-notice", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.get("/tracked-cases/consent-notice", headers={"Authorization": "pilot-secret-not-real"}).status_code == 401      # missing "Bearer"
    assert c.get("/tracked-cases/consent-notice", headers={"Authorization": "Bearer pilot-secret-not-real"}).status_code == 200
    assert c.delete("/tracked-cases/x").status_code == 401                                 # writes are protected too
    assert c.post("/speech/transcribe", json={}).status_code == 401
    assert c.get("/health").status_code == 200
    # even this computer needs the token once one is set
    assert client("127.0.0.1").get("/tracked-cases").status_code == 401


def test_browser_preflight_is_not_blocked(monkeypatch):
    monkeypatch.setenv("NIVARAN_API_TOKEN", "pilot-secret-not-real")
    r = client("192.168.1.50").options("/tracked-cases", headers={"Origin": "http://localhost:8081", "Access-Control-Request-Method": "POST",
                                                                  "Access-Control-Request-Headers": "authorization,content-type"})
    assert r.status_code == 200 and "authorization" in r.headers.get("access-control-allow-headers", "").lower()
