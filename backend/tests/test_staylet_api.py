"""
Staylet API Backend Tests
Tests for: Authentication, Properties CRUD, Compliance Records CRUD, Dashboard Stats, Validation
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "bugtest@staylet.com"
TEST_PASSWORD = "Test1234!"

class TestHealthAndConstants:
    """Health check and constants endpoints"""
    
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ Root endpoint passed")
    
    def test_constants_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        data = response.json()
        assert "uk_nations" in data
        assert "property_types" in data
        assert "compliance_categories" in data
        assert "compliance_status" in data
        print("✓ Constants endpoint passed")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_success(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL.lower()
        print("✓ Login success test passed")
    
    def test_login_invalid_credentials(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Login invalid credentials test passed")
    
    def test_get_me_authenticated(self):
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["token"]
        
        # Get current user
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL.lower()
        print("✓ Get me authenticated test passed")
    
    def test_get_me_unauthorized(self):
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
        print("✓ Get me unauthorized test passed")
    
    def test_password_reset_request(self):
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Password reset request test passed (MOCKED)")


@pytest.fixture(scope="class")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Authentication failed - skipping authenticated tests")


class TestPropertyValidation:
    """Property validation tests - reject empty/whitespace fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_token):
        self.token = auth_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_property_empty_name_rejected(self, auth_token):
        """Backend should reject empty property name"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA"
            })
        assert response.status_code == 400
        assert "name" in response.json()["detail"].lower()
        print("✓ Empty property name rejected")
    
    def test_create_property_whitespace_name_rejected(self, auth_token):
        """Backend should reject whitespace-only property name"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "   ",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA"
            })
        assert response.status_code == 400
        assert "name" in response.json()["detail"].lower()
        print("✓ Whitespace property name rejected")
    
    def test_create_property_empty_address_rejected(self, auth_token):
        """Backend should reject empty address"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Property",
                "address": "",
                "postcode": "SW1A 1AA"
            })
        assert response.status_code == 400
        assert "address" in response.json()["detail"].lower()
        print("✓ Empty address rejected")
    
    def test_create_property_whitespace_address_rejected(self, auth_token):
        """Backend should reject whitespace-only address"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Property",
                "address": "   ",
                "postcode": "SW1A 1AA"
            })
        assert response.status_code == 400
        assert "address" in response.json()["detail"].lower()
        print("✓ Whitespace address rejected")
    
    def test_create_property_empty_postcode_rejected(self, auth_token):
        """Backend should reject empty postcode"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Property",
                "address": "123 Test Street",
                "postcode": ""
            })
        assert response.status_code == 400
        assert "postcode" in response.json()["detail"].lower()
        print("✓ Empty postcode rejected")
    
    def test_create_property_whitespace_postcode_rejected(self, auth_token):
        """Backend should reject whitespace-only postcode"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Property",
                "address": "123 Test Street",
                "postcode": "   "
            })
        assert response.status_code == 400
        assert "postcode" in response.json()["detail"].lower()
        print("✓ Whitespace postcode rejected")


class TestPropertyCRUD:
    """Property CRUD operations tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_token):
        self.token = auth_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_property_ids = []
    
    def teardown_method(self, method):
        """Cleanup created test properties"""
        for prop_id in self.created_property_ids:
            try:
                requests.delete(f"{BASE_URL}/api/properties/{prop_id}", headers=self.headers)
            except:
                pass
    
    def test_create_property_success(self, auth_token):
        """Create property with valid data"""
        unique_name = f"TEST_Property_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": unique_name,
                "address": "123 Test Street",
                "postcode": "SW1A 1AA",
                "uk_nation": "England",
                "property_type": "apartment",
                "bedrooms": 2
            })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == unique_name
        assert data["address"] == "123 Test Street"
        assert data["postcode"] == "SW1A 1AA"
        assert "id" in data
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/properties/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Create property success test passed")
    
    def test_get_properties_list(self, auth_token):
        """Get list of properties"""
        response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ Get properties list test passed")
    
    def test_get_property_by_id(self, auth_token):
        """Get single property by ID"""
        # First create a property
        unique_name = f"TEST_GetById_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": unique_name,
                "address": "456 Test Avenue",
                "postcode": "NW1 8AB"
            })
        property_id = create_response.json()["id"]
        
        # Get by ID
        response = requests.get(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == property_id
        assert data["name"] == unique_name
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Get property by ID test passed")
    
    def test_update_property(self, auth_token):
        """Update property"""
        # Create property
        unique_name = f"TEST_Update_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": unique_name,
                "address": "789 Test Road",
                "postcode": "E1 6AN"
            })
        property_id = create_response.json()["id"]
        
        # Update
        updated_name = f"TEST_Updated_{uuid.uuid4().hex[:8]}"
        response = requests.put(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": updated_name})
        assert response.status_code == 200
        assert response.json()["name"] == updated_name
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert get_response.json()["name"] == updated_name
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Update property test passed")
    
    def test_delete_property(self, auth_token):
        """Delete property"""
        # Create property
        unique_name = f"TEST_Delete_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": unique_name,
                "address": "Delete Street",
                "postcode": "W1A 1AA"
            })
        property_id = create_response.json()["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        
        # Verify deleted
        get_response = requests.get(f"{BASE_URL}/api/properties/{property_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert get_response.status_code == 404
        print("✓ Delete property test passed")
    
    def test_property_search(self, auth_token):
        """Search properties"""
        response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"search": "test"})
        assert response.status_code == 200
        print("✓ Property search test passed")


class TestComplianceRecordValidation:
    """Compliance record validation tests - reject empty/whitespace fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_token):
        self.token = auth_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        # Get a property ID for testing
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=self.headers)
        if props_response.status_code == 200 and len(props_response.json()) > 0:
            self.property_id = props_response.json()[0]["id"]
        else:
            # Create a test property
            create_response = requests.post(f"{BASE_URL}/api/properties", 
                headers=self.headers,
                json={
                    "name": f"TEST_ComplianceValidation_{uuid.uuid4().hex[:8]}",
                    "address": "Test Address",
                    "postcode": "SW1A 1AA"
                })
            self.property_id = create_response.json()["id"]
    
    def test_create_compliance_empty_title_rejected(self, auth_token):
        """Backend should reject empty compliance title"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": "",
                "category": "gas_safety"
            })
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()
        print("✓ Empty compliance title rejected")
    
    def test_create_compliance_whitespace_title_rejected(self, auth_token):
        """Backend should reject whitespace-only compliance title"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": "   ",
                "category": "gas_safety"
            })
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()
        print("✓ Whitespace compliance title rejected")
    
    def test_create_compliance_empty_category_rejected(self, auth_token):
        """Backend should reject empty compliance category"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": "Test Certificate",
                "category": ""
            })
        assert response.status_code == 400
        assert "category" in response.json()["detail"].lower()
        print("✓ Empty compliance category rejected")


class TestComplianceRecordCRUD:
    """Compliance record CRUD operations tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_token):
        self.token = auth_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_compliance_record_success(self, auth_token):
        """Create compliance record with valid data"""
        # Get a property
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        unique_title = f"TEST_GasCert_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": unique_title,
                "category": "gas_safety",
                "expiry_date": (datetime.now() + timedelta(days=365)).isoformat()
            })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == unique_title
        assert data["category"] == "gas_safety"
        assert "id" in data
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Create compliance record success test passed")
    
    def test_get_compliance_records_list(self, auth_token):
        """Get list of compliance records"""
        response = requests.get(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ Get compliance records list test passed")
    
    def test_compliance_status_calculation_compliant(self, auth_token):
        """Test compliance status is 'compliant' for future expiry date"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        # Create record with expiry 60 days in future (should be compliant)
        future_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": f"TEST_Compliant_{uuid.uuid4().hex[:8]}",
                "category": "epc",
                "expiry_date": future_date
            })
        assert response.status_code == 200
        data = response.json()
        assert data["compliance_status"] == "compliant"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Compliance status 'compliant' calculation test passed")
    
    def test_compliance_status_calculation_expiring_soon(self, auth_token):
        """Test compliance status is 'expiring_soon' for expiry within 30 days"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        # Create record with expiry 15 days in future (should be expiring_soon)
        soon_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": f"TEST_ExpiringSoon_{uuid.uuid4().hex[:8]}",
                "category": "eicr",
                "expiry_date": soon_date
            })
        assert response.status_code == 200
        data = response.json()
        assert data["compliance_status"] == "expiring_soon"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Compliance status 'expiring_soon' calculation test passed")
    
    def test_compliance_status_calculation_overdue(self, auth_token):
        """Test compliance status is 'overdue' for past expiry date"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        # Create record with expiry in the past (should be overdue)
        past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": f"TEST_Overdue_{uuid.uuid4().hex[:8]}",
                "category": "insurance",
                "expiry_date": past_date
            })
        assert response.status_code == 200
        data = response.json()
        assert data["compliance_status"] == "overdue"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/compliance-records/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Compliance status 'overdue' calculation test passed")
    
    def test_delete_compliance_record(self, auth_token):
        """Delete compliance record"""
        props_response = requests.get(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"})
        if props_response.status_code != 200 or len(props_response.json()) == 0:
            pytest.skip("No properties available for testing")
        property_id = props_response.json()[0]["id"]
        
        # Create record
        create_response = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "property_id": property_id,
                "title": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
                "category": "gas_safety"
            })
        record_id = create_response.json()["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/compliance-records/{record_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        
        # Verify deleted
        get_response = requests.get(f"{BASE_URL}/api/compliance-records/{record_id}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert get_response.status_code == 404
        print("✓ Delete compliance record test passed")


class TestDashboardStats:
    """Dashboard stats accuracy tests"""
    
    def test_dashboard_stats_structure(self, auth_token):
        """Test dashboard stats returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        assert "total_properties" in data
        assert "upcoming_expiries" in data
        assert "overdue_items" in data
        assert "missing_records" in data
        assert "tasks_due" in data
        
        # Check values are integers
        assert isinstance(data["total_properties"], int)
        assert isinstance(data["upcoming_expiries"], int)
        assert isinstance(data["overdue_items"], int)
        assert isinstance(data["missing_records"], int)
        assert isinstance(data["tasks_due"], int)
        print("✓ Dashboard stats structure test passed")
    
    def test_dashboard_stats_accuracy(self, auth_token):
        """Test dashboard stats match actual data counts"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get dashboard stats
        stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        stats = stats_response.json()
        
        # Get actual properties count
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        actual_properties = [p for p in props_response.json() if p.get("property_status") == "active"]
        
        # Get actual compliance records
        compliance_response = requests.get(f"{BASE_URL}/api/compliance-records", headers=headers)
        compliance_records = compliance_response.json()
        
        # Count by status
        actual_expiring = sum(1 for r in compliance_records if r.get("compliance_status") == "expiring_soon")
        actual_overdue = sum(1 for r in compliance_records if r.get("compliance_status") == "overdue")
        actual_missing = sum(1 for r in compliance_records if r.get("compliance_status") == "missing")
        
        # Verify counts match
        assert stats["total_properties"] == len(actual_properties), f"Properties mismatch: {stats['total_properties']} vs {len(actual_properties)}"
        assert stats["upcoming_expiries"] == actual_expiring, f"Expiring mismatch: {stats['upcoming_expiries']} vs {actual_expiring}"
        assert stats["overdue_items"] == actual_overdue, f"Overdue mismatch: {stats['overdue_items']} vs {actual_overdue}"
        assert stats["missing_records"] == actual_missing, f"Missing mismatch: {stats['missing_records']} vs {actual_missing}"
        print("✓ Dashboard stats accuracy test passed")


class TestTasksCRUD:
    """Tasks CRUD operations tests"""
    
    def test_get_tasks_list(self, auth_token):
        """Get list of tasks"""
        response = requests.get(f"{BASE_URL}/api/tasks", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ Get tasks list test passed")
    
    def test_create_task(self, auth_token):
        """Create a task"""
        unique_title = f"TEST_Task_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/tasks", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": unique_title,
                "description": "Test task description",
                "priority": "high"
            })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == unique_title
        assert data["task_status"] == "pending"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{data['id']}", 
            headers={"Authorization": f"Bearer {auth_token}"})
        print("✓ Create task test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
