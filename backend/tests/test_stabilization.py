"""
Staylet Stabilization Tests - Bug Fixes and Stability Verification
Tests for: form validation, database writes, data refresh, navigation, status badges, dashboard counts
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "bugtest@staylet.com"
TEST_PASSWORD = "Test1234!"


class TestAuthAndSetup:
    """Authentication and setup tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"Login successful for {TEST_EMAIL}")


class TestFormValidation:
    """Form validation tests - verify backend rejects empty/invalid data"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    # Property validation tests
    def test_property_empty_name_rejected(self, auth_headers):
        """Property creation with empty name should be rejected"""
        response = requests.post(f"{BASE_URL}/api/properties", headers=auth_headers, json={
            "name": "",
            "address": "123 Test Street",
            "postcode": "SW1A 1AA"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "name" in response.json().get("detail", "").lower()
        print("Property empty name validation: PASS")
    
    def test_property_whitespace_name_rejected(self, auth_headers):
        """Property creation with whitespace-only name should be rejected"""
        response = requests.post(f"{BASE_URL}/api/properties", headers=auth_headers, json={
            "name": "   ",
            "address": "123 Test Street",
            "postcode": "SW1A 1AA"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Property whitespace name validation: PASS")
    
    def test_property_empty_address_rejected(self, auth_headers):
        """Property creation with empty address should be rejected"""
        response = requests.post(f"{BASE_URL}/api/properties", headers=auth_headers, json={
            "name": "Test Property",
            "address": "",
            "postcode": "SW1A 1AA"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "address" in response.json().get("detail", "").lower()
        print("Property empty address validation: PASS")
    
    def test_property_empty_postcode_rejected(self, auth_headers):
        """Property creation with empty postcode should be rejected"""
        response = requests.post(f"{BASE_URL}/api/properties", headers=auth_headers, json={
            "name": "Test Property",
            "address": "123 Test Street",
            "postcode": ""
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "postcode" in response.json().get("detail", "").lower()
        print("Property empty postcode validation: PASS")
    
    # Compliance record validation tests
    def test_compliance_empty_title_rejected(self, auth_headers):
        """Compliance record with empty title should be rejected"""
        # First get a property ID
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available for testing")
        property_id = props[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "",
            "category": "gas_safety"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "title" in response.json().get("detail", "").lower()
        print("Compliance empty title validation: PASS")
    
    def test_compliance_empty_category_rejected(self, auth_headers):
        """Compliance record with empty category should be rejected"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available for testing")
        property_id = props[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "Test Record",
            "category": ""
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "category" in response.json().get("detail", "").lower()
        print("Compliance empty category validation: PASS")
    
    # Task validation tests
    def test_task_empty_title_rejected(self, auth_headers):
        """Task with empty title should be rejected"""
        response = requests.post(f"{BASE_URL}/api/tasks", headers=auth_headers, json={
            "title": "",
            "priority": "medium"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "title" in response.json().get("detail", "").lower()
        print("Task empty title validation: PASS")
    
    def test_task_whitespace_title_rejected(self, auth_headers):
        """Task with whitespace-only title should be rejected"""
        response = requests.post(f"{BASE_URL}/api/tasks", headers=auth_headers, json={
            "title": "   ",
            "priority": "medium"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Task whitespace title validation: PASS")


class TestDatabaseWrites:
    """Database write tests - verify CRUD operations persist correctly"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    def test_property_create_and_verify(self, auth_headers):
        """Create property and verify it appears in list"""
        # Create property
        create_response = requests.post(f"{BASE_URL}/api/properties", headers=auth_headers, json={
            "name": "TEST_Stabilization Property",
            "address": "456 Test Lane",
            "postcode": "EC1A 1BB",
            "uk_nation": "England",
            "property_type": "apartment",
            "bedrooms": 2
        })
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        created = create_response.json()
        property_id = created["id"]
        
        # Verify in list
        list_response = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers)
        assert list_response.status_code == 200
        properties = list_response.json()
        found = any(p["id"] == property_id for p in properties)
        assert found, "Created property not found in list"
        
        # Verify by direct GET
        get_response = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers)
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == "TEST_Stabilization Property"
        assert fetched["postcode"] == "EC1A 1BB"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers)
        print("Property create and verify: PASS")
    
    def test_compliance_record_create_and_verify(self, auth_headers):
        """Create compliance record and verify it updates property summary"""
        # Get existing property
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        # Get initial summary
        initial_prop = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers).json()
        initial_total = initial_prop.get("compliance_summary", {}).get("total", 0)
        
        # Create compliance record
        expiry_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        create_response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Stabilization Gas Safety",
            "category": "gas_safety",
            "expiry_date": expiry_date
        })
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        record_id = create_response.json()["id"]
        
        # Verify in list
        records = requests.get(f"{BASE_URL}/api/compliance-records", headers=auth_headers, params={"property_id": property_id}).json()
        found = any(r["id"] == record_id for r in records)
        assert found, "Created compliance record not found in list"
        
        # Verify property summary updated
        updated_prop = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers).json()
        updated_total = updated_prop.get("compliance_summary", {}).get("total", 0)
        assert updated_total == initial_total + 1, f"Summary not updated: {initial_total} -> {updated_total}"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{record_id}", headers=auth_headers)
        print("Compliance record create and verify: PASS")
    
    def test_task_create_and_verify(self, auth_headers):
        """Create task and verify it appears in list"""
        # Create task
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        create_response = requests.post(f"{BASE_URL}/api/tasks", headers=auth_headers, json={
            "title": "TEST_Stabilization Task",
            "description": "Test task for stabilization",
            "due_date": due_date,
            "priority": "high",
            "category": "maintenance"
        })
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        task_id = create_response.json()["id"]
        
        # Verify in list
        tasks = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers).json()
        found = any(t["id"] == task_id for t in tasks)
        assert found, "Created task not found in list"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("Task create and verify: PASS")


class TestStatusBadges:
    """Status badge tests - verify compliance status calculation"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    def test_compliant_status(self, auth_headers):
        """Record with expiry > 30 days should be compliant"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        expiry_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Compliant Record",
            "category": "eicr",
            "expiry_date": expiry_date
        })
        assert response.status_code == 200
        record = response.json()
        assert record["compliance_status"] == "compliant", f"Expected compliant, got {record['compliance_status']}"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{record['id']}", headers=auth_headers)
        print("Compliant status: PASS")
    
    def test_expiring_soon_status(self, auth_headers):
        """Record with expiry <= 30 days should be expiring_soon"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        expiry_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Expiring Soon Record",
            "category": "epc",
            "expiry_date": expiry_date
        })
        assert response.status_code == 200
        record = response.json()
        assert record["compliance_status"] == "expiring_soon", f"Expected expiring_soon, got {record['compliance_status']}"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{record['id']}", headers=auth_headers)
        print("Expiring soon status: PASS")
    
    def test_overdue_status(self, auth_headers):
        """Record with past expiry should be overdue"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        expiry_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Overdue Record",
            "category": "insurance",
            "expiry_date": expiry_date
        })
        assert response.status_code == 200
        record = response.json()
        assert record["compliance_status"] == "overdue", f"Expected overdue, got {record['compliance_status']}"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{record['id']}", headers=auth_headers)
        print("Overdue status: PASS")


class TestDashboardCounts:
    """Dashboard count tests - verify stats match actual data"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    def test_dashboard_stats_accuracy(self, auth_headers):
        """Dashboard stats should match actual database counts"""
        # Get dashboard stats
        stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=auth_headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Get actual property count
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        active_props = [p for p in props if p.get("property_status") == "active"]
        assert stats["total_properties"] == len(active_props), f"Property count mismatch: {stats['total_properties']} vs {len(active_props)}"
        
        # Get actual compliance records
        records = requests.get(f"{BASE_URL}/api/compliance-records", headers=auth_headers).json()
        expiring_soon = sum(1 for r in records if r.get("compliance_status") == "expiring_soon")
        overdue = sum(1 for r in records if r.get("compliance_status") == "overdue")
        missing = sum(1 for r in records if r.get("compliance_status") == "missing")
        
        assert stats["upcoming_expiries"] == expiring_soon, f"Expiring soon mismatch: {stats['upcoming_expiries']} vs {expiring_soon}"
        assert stats["overdue_items"] == overdue, f"Overdue mismatch: {stats['overdue_items']} vs {overdue}"
        assert stats["missing_records"] == missing, f"Missing mismatch: {stats['missing_records']} vs {missing}"
        
        print(f"Dashboard stats verified: {stats['total_properties']} properties, {expiring_soon} expiring, {overdue} overdue")
        print("Dashboard stats accuracy: PASS")
    
    def test_dashboard_data_endpoint(self, auth_headers):
        """Dashboard data endpoint should return upcoming expiries and overdue records"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "stats" in data
        assert "upcoming_expiries" in data
        assert "overdue_records" in data
        assert "tasks_due_this_month" in data
        
        # Verify upcoming expiries have required fields
        for expiry in data["upcoming_expiries"]:
            assert "id" in expiry
            assert "title" in expiry
            assert "property_name" in expiry
            assert "days_until_expiry" in expiry
            assert "compliance_status" in expiry
        
        # Verify overdue records have property_name
        for record in data["overdue_records"]:
            assert "property_name" in record
        
        print(f"Dashboard data: {len(data['upcoming_expiries'])} upcoming, {len(data['overdue_records'])} overdue")
        print("Dashboard data endpoint: PASS")


class TestDataRefresh:
    """Data refresh tests - verify list updates after CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    def test_compliance_delete_updates_list(self, auth_headers):
        """After deleting compliance record, list should update"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        # Create record
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Delete Test Record",
            "category": "pat_testing"
        })
        record_id = response.json()["id"]
        
        # Verify in list
        records_before = requests.get(f"{BASE_URL}/api/compliance-records", headers=auth_headers, params={"property_id": property_id}).json()
        assert any(r["id"] == record_id for r in records_before)
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/compliance-records/{record_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Verify removed from list
        records_after = requests.get(f"{BASE_URL}/api/compliance-records", headers=auth_headers, params={"property_id": property_id}).json()
        assert not any(r["id"] == record_id for r in records_after), "Deleted record still in list"
        
        print("Compliance delete updates list: PASS")
    
    def test_property_summary_updates_after_record_delete(self, auth_headers):
        """Property summary should update after compliance record deletion"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        property_id = props[0]["id"]
        
        # Get initial summary
        initial_prop = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers).json()
        initial_total = initial_prop.get("compliance_summary", {}).get("total", 0)
        
        # Create record
        response = requests.post(f"{BASE_URL}/api/compliance-records", headers=auth_headers, json={
            "property_id": property_id,
            "title": "TEST_Summary Update Test",
            "category": "legionella"
        })
        record_id = response.json()["id"]
        
        # Verify summary increased
        after_create = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers).json()
        assert after_create["compliance_summary"]["total"] == initial_total + 1
        
        # Delete record
        requests.delete(f"{BASE_URL}/api/compliance-records/{record_id}", headers=auth_headers)
        
        # Verify summary decreased
        after_delete = requests.get(f"{BASE_URL}/api/properties/{property_id}", headers=auth_headers).json()
        assert after_delete["compliance_summary"]["total"] == initial_total
        
        print("Property summary updates after record delete: PASS")


class TestNavigation:
    """Navigation tests - verify API endpoints for navigation"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed")
    
    def test_properties_list_endpoint(self, auth_headers):
        """Properties list endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("Properties list endpoint: PASS")
    
    def test_property_detail_endpoint(self, auth_headers):
        """Property detail endpoint should work"""
        props = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers).json()
        if not props:
            pytest.skip("No properties available")
        
        response = requests.get(f"{BASE_URL}/api/properties/{props[0]['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert "compliance_summary" in response.json()
        print("Property detail endpoint: PASS")
    
    def test_compliance_list_endpoint(self, auth_headers):
        """Compliance records list endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/compliance-records", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("Compliance list endpoint: PASS")
    
    def test_tasks_list_endpoint(self, auth_headers):
        """Tasks list endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("Tasks list endpoint: PASS")
    
    def test_constants_endpoint(self, auth_headers):
        """Constants endpoint should return all required constants"""
        response = requests.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        data = response.json()
        
        required_keys = ["uk_nations", "property_types", "compliance_categories", "task_statuses", "task_priorities"]
        for key in required_keys:
            assert key in data, f"Missing constant: {key}"
        
        print("Constants endpoint: PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
