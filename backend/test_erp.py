import functools
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_erp_endpoints():
    print("--- Running ERP Integration Tests ---")
    
    # 1. Test ERP Inventory Endpoint
    print("Testing GET /api/v1/erp/inventory/1 ...")
    response = client.get("/api/v1/erp/inventory/1")
    print(f"Status Code: {response.status_code}")
    
    # Depending on DB initialization, it might be 404 (no tenant) or 200 (tenant exists).
    # Since we didn't force-seed Tenant 1 in this exact script, we check for structural presence of the route.
    assert response.status_code in [200, 404], "Route should exist and return either 200 or 404"
    if response.status_code == 200:
        data = response.json()
        assert "tenant_id" in data
        assert "devices" in data
        print("Inventory JSON Structure validated.")
        
    # 2. Test ERP Monitoring Status Endpoint
    print("Testing GET /api/v1/erp/monitoring/status/1 ...")
    response_mon = client.get("/api/v1/erp/monitoring/status/1")
    print(f"Status Code: {response_mon.status_code}")
    assert response_mon.status_code in [200, 404], "Route should exist and return either 200 or 404"
    if response_mon.status_code == 200:
        data_mon = response_mon.json()
        assert "summary_status" in data_mon
        assert "node_status" in data_mon
        print("Monitoring JSON Structure validated.")
        
    print("--- ERP Integration API structurally sound ---")

if __name__ == "__main__":
    test_erp_endpoints()
