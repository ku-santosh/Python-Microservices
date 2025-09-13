import json
from app import app

def test_get_products(monkeypatch):
    client = app.test_client()

    class DummyResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"products": [{"id": 1, "title": "Test Product", "brand": "BrandX", "price": 100, "description": "Desc"}]}

    monkeypatch.setattr("requests.get", lambda url: DummyResponse())

    response = client.get('/products')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['data'][0]['title'] == "Test Product"
