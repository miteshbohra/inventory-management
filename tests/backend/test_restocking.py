"""
Tests for restocking order API endpoints.
"""
import pytest

import mock_data


@pytest.fixture(autouse=True)
def clean_restocking_orders():
    """Restocking orders live in a module-level list, so reset it around each test."""
    mock_data.restocking_orders.clear()
    yield
    mock_data.restocking_orders.clear()


def forecasts_by_sku(client):
    return {f["item_sku"]: f for f in client.get("/api/demand").json()}


class TestRestockingOrderEndpoints:
    """Test suite for restocking order endpoints."""

    def test_demand_forecasts_include_cost_and_lead_time(self, client):
        """Test that forecasts expose the fields restocking depends on."""
        for forecast in client.get("/api/demand").json():
            assert isinstance(forecast["unit_cost"], (int, float))
            assert forecast["unit_cost"] > 0
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["lead_time_days"] > 0

    def test_list_restocking_orders_empty(self, client):
        """Test that no orders are returned before any are submitted."""
        response = client.get("/api/restocking-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restocking_order(self, client):
        """Test submitting a restocking order."""
        forecasts = forecasts_by_sku(client)
        response = client.post(
            "/api/restocking-orders",
            json={"items": [{"sku": "WDG-001", "quantity": 100}]},
        )
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"].startswith("RST-")
        assert order["status"] == "Submitted"
        assert order["items"][0]["sku"] == "WDG-001"
        assert order["items"][0]["name"] == forecasts["WDG-001"]["item_name"]
        assert order["items"][0]["quantity"] == 100
        assert "T" in order["order_date"]
        assert "T" in order["expected_delivery"]

    def test_order_total_uses_server_costs(self, client):
        """Test that the total is computed from server-side unit costs."""
        forecasts = forecasts_by_sku(client)
        items = [{"sku": "WDG-001", "quantity": 100}, {"sku": "FLT-405", "quantity": 200}]
        order = client.post("/api/restocking-orders", json={"items": items}).json()

        expected = sum(i["quantity"] * forecasts[i["sku"]]["unit_cost"] for i in items)
        assert abs(order["total_value"] - expected) < 0.01

    def test_order_lead_time_is_slowest_item(self, client):
        """Test that lead time is the max across lines and drives the delivery date."""
        forecasts = forecasts_by_sku(client)
        skus = ["FLT-405", "MTR-304"]
        order = client.post(
            "/api/restocking-orders",
            json={"items": [{"sku": s, "quantity": 1} for s in skus]},
        ).json()

        assert order["lead_time_days"] == max(forecasts[s]["lead_time_days"] for s in skus)

        from datetime import datetime
        placed = datetime.fromisoformat(order["order_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert (expected - placed).days == order["lead_time_days"]

    def test_list_returns_newest_first(self, client):
        """Test that submitted orders are listed newest first."""
        first = client.post("/api/restocking-orders", json={"items": [{"sku": "WDG-001", "quantity": 1}]}).json()
        second = client.post("/api/restocking-orders", json={"items": [{"sku": "FLT-405", "quantity": 1}]}).json()

        data = client.get("/api/restocking-orders").json()
        assert [o["id"] for o in data] == [second["id"], first["id"]]
        assert first["order_number"] != second["order_number"]

    def test_create_order_with_no_items(self, client):
        """Test that an empty order is rejected."""
        response = client.post("/api/restocking-orders", json={"items": []})
        assert response.status_code == 400
        assert "at least one item" in response.json()["detail"].lower()

    def test_create_order_with_unknown_sku(self, client):
        """Test that an unknown SKU is rejected."""
        response = client.post(
            "/api/restocking-orders",
            json={"items": [{"sku": "NOPE-999", "quantity": 5}]},
        )
        assert response.status_code == 400
        assert "unknown sku" in response.json()["detail"].lower()

    @pytest.mark.parametrize("quantity", [0, -5])
    def test_create_order_with_non_positive_quantity(self, client, quantity):
        """Test that zero or negative quantities are rejected."""
        response = client.post(
            "/api/restocking-orders",
            json={"items": [{"sku": "WDG-001", "quantity": quantity}]},
        )
        assert response.status_code == 400

    def test_create_order_with_malformed_body(self, client):
        """Test that a body without items fails validation."""
        response = client.post("/api/restocking-orders", json={})
        assert response.status_code == 422

    def test_rejected_order_is_not_stored(self, client):
        """Test that a failed submission leaves no partial order behind."""
        client.post(
            "/api/restocking-orders",
            json={"items": [{"sku": "WDG-001", "quantity": 1}, {"sku": "NOPE-999", "quantity": 1}]},
        )
        assert client.get("/api/restocking-orders").json() == []

    def test_restocking_does_not_affect_sales_orders(self, client):
        """Test that submitting a restocking order leaves /api/orders and the dashboard unchanged."""
        orders_before = client.get("/api/orders").json()
        summary_before = client.get("/api/dashboard/summary").json()

        client.post("/api/restocking-orders", json={"items": [{"sku": "WDG-001", "quantity": 100}]})

        assert client.get("/api/orders").json() == orders_before
        assert client.get("/api/dashboard/summary").json() == summary_before
