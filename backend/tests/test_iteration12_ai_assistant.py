"""
Test suite for Iteration 12 - AI Assistant Features
Tests:
- Dashboard AI Assistant insights endpoint
- Property-level AI Assistant endpoint
- Natural language query endpoint
- Existing flows still work (auth, CRUD)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Basic health and auth tests to ensure system is working"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")
    
    def test_demo_mode_creates_account(self):
        """Test demo mode creates account with seeded data"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["property_count"] == 3  # Demo creates 3 properties
        print(f"✓ Demo mode created account with {data['user']['property_count']} properties")
        return data["token"]


class TestAIAssistantInsights:
    """Test the dashboard AI assistant insights endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create demo account for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_insights_returns_valid_structure(self):
        """Test /api/assistant/insights returns expected structure"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        assert "summary" in data
        assert "highest_risk_property" in data
        assert "property_risks" in data
        assert "urgent_actions" in data
        assert "expiring_this_month" in data
        assert "tasks_this_month" in data
        assert "missing_by_property" in data
        
        print("✓ Insights endpoint returns valid structure")
    
    def test_insights_summary_has_correct_fields(self):
        """Test insights summary contains expected fields"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        summary = data["summary"]
        assert "total_properties" in summary
        assert "total_records" in summary
        assert "total_tasks" in summary
        assert "overdue_records" in summary
        assert "expiring_soon_records" in summary
        assert "pending_tasks" in summary
        
        # Demo mode creates 3 properties
        assert summary["total_properties"] == 3
        print(f"✓ Summary shows {summary['total_properties']} properties, {summary['total_records']} records")
    
    def test_insights_highest_risk_property(self):
        """Test highest risk property is identified correctly"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Demo data has properties with overdue items, so highest_risk should exist
        if data["highest_risk_property"]:
            hrp = data["highest_risk_property"]
            assert "property_id" in hrp
            assert "property_name" in hrp
            assert "risk_score" in hrp
            assert "risk_reasons" in hrp
            print(f"✓ Highest risk property: {hrp['property_name']} (score: {hrp['risk_score']})")
        else:
            print("✓ No high-risk properties (all compliant)")
    
    def test_insights_urgent_actions(self):
        """Test urgent actions are returned"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Demo data has overdue items, so urgent_actions should exist
        if data["urgent_actions"]:
            action = data["urgent_actions"][0]
            assert "type" in action
            assert "priority" in action
            assert "action" in action
            assert "property_name" in action
            print(f"✓ Found {len(data['urgent_actions'])} urgent actions")
        else:
            print("✓ No urgent actions needed")
    
    def test_insights_missing_by_property(self):
        """Test missing compliance records are identified"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["missing_by_property"]:
            missing = data["missing_by_property"][0]
            assert "property_id" in missing
            assert "property_name" in missing
            assert "missing" in missing
            assert isinstance(missing["missing"], list)
            print(f"✓ Found {len(data['missing_by_property'])} properties with missing records")
        else:
            print("✓ No missing compliance records")
    
    def test_insights_requires_auth(self):
        """Test insights endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights")
        assert response.status_code in [401, 403]
        print("✓ Insights endpoint requires authentication")


class TestPropertyAssistant:
    """Test the property-level AI assistant endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create demo account and get property ID"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get first property ID
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=self.headers)
        assert props_response.status_code == 200
        self.properties = props_response.json()
        self.property_id = self.properties[0]["id"] if self.properties else None
    
    def test_property_insights_returns_valid_structure(self):
        """Test /api/assistant/property/{id} returns expected structure"""
        if not self.property_id:
            pytest.skip("No properties available")
        
        response = requests.get(
            f"{BASE_URL}/api/assistant/property/{self.property_id}", 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "property" in data
        assert "compliance_score" in data
        assert "missing_records" in data
        assert "overdue_records" in data
        assert "expiring_soon_records" in data
        assert "compliant_records" in data
        assert "pending_tasks" in data
        assert "recommended_actions" in data
        assert "summary" in data
        
        print(f"✓ Property insights returns valid structure for {data['property']['name']}")
    
    def test_property_compliance_score(self):
        """Test compliance score is calculated correctly"""
        if not self.property_id:
            pytest.skip("No properties available")
        
        response = requests.get(
            f"{BASE_URL}/api/assistant/property/{self.property_id}", 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data["compliance_score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100
        print(f"✓ Compliance score: {score}%")
    
    def test_property_recommended_actions(self):
        """Test recommended actions are returned"""
        if not self.property_id:
            pytest.skip("No properties available")
        
        response = requests.get(
            f"{BASE_URL}/api/assistant/property/{self.property_id}", 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["recommended_actions"]:
            action = data["recommended_actions"][0]
            assert "priority" in action
            assert "action" in action
            assert "detail" in action
            print(f"✓ Found {len(data['recommended_actions'])} recommended actions")
        else:
            print("✓ No recommended actions (property fully compliant)")
    
    def test_property_insights_404_for_invalid_id(self):
        """Test 404 returned for non-existent property"""
        response = requests.get(
            f"{BASE_URL}/api/assistant/property/invalid-property-id", 
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ Returns 404 for invalid property ID")
    
    def test_property_insights_requires_auth(self):
        """Test property insights requires authentication"""
        if not self.property_id:
            pytest.skip("No properties available")
        
        response = requests.get(f"{BASE_URL}/api/assistant/property/{self.property_id}")
        assert response.status_code in [401, 403]
        print("✓ Property insights requires authentication")


class TestNaturalLanguageQuery:
    """Test the natural language query endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create demo account for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_ask_question_returns_answer(self):
        """Test /api/assistant/ask returns an answer"""
        response = requests.post(
            f"{BASE_URL}/api/assistant/ask",
            headers=self.headers,
            json={"question": "What expires this month?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "source" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        print(f"✓ Got answer: {data['answer'][:100]}...")
    
    def test_ask_question_about_properties(self):
        """Test asking about properties"""
        response = requests.post(
            f"{BASE_URL}/api/assistant/ask",
            headers=self.headers,
            json={"question": "Which properties have overdue items?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        print(f"✓ Property question answered: {data['answer'][:100]}...")
    
    def test_ask_question_about_tasks(self):
        """Test asking about tasks"""
        response = requests.post(
            f"{BASE_URL}/api/assistant/ask",
            headers=self.headers,
            json={"question": "What tasks need attention?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        print(f"✓ Task question answered: {data['answer'][:100]}...")
    
    def test_ask_empty_question_rejected(self):
        """Test empty question is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/assistant/ask",
            headers=self.headers,
            json={"question": "   "}
        )
        assert response.status_code == 400
        print("✓ Empty question rejected with 400")
    
    def test_ask_requires_auth(self):
        """Test ask endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/assistant/ask",
            json={"question": "What expires this month?"}
        )
        assert response.status_code in [401, 403]
        print("✓ Ask endpoint requires authentication")


class TestExistingFlowsStillWork:
    """Verify existing flows still work after AI Assistant addition"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create demo account for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_dashboard_stats_still_work(self):
        """Test dashboard stats endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_properties" in data
        assert "overdue_items" in data
        print(f"✓ Dashboard stats: {data['total_properties']} properties, {data['overdue_items']} overdue")
    
    def test_dashboard_data_still_works(self):
        """Test dashboard data endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "upcoming_expiries" in data
        print("✓ Dashboard data endpoint working")
    
    def test_properties_crud_still_works(self):
        """Test properties CRUD still works"""
        # Create
        create_response = requests.post(
            f"{BASE_URL}/api/properties",
            headers=self.headers,
            json={
                "name": "TEST_AI_Property",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA",
                "uk_nation": "England",
                "property_type": "apartment",
                "bedrooms": 2
            }
        )
        assert create_response.status_code == 200
        property_id = create_response.json()["id"]
        
        # Read
        get_response = requests.get(
            f"{BASE_URL}/api/properties/{property_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        # Update
        update_response = requests.put(
            f"{BASE_URL}/api/properties/{property_id}",
            headers=self.headers,
            json={"name": "TEST_AI_Property_Updated"}
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/properties/{property_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 200
        
        print("✓ Properties CRUD still working")
    
    def test_compliance_records_still_work(self):
        """Test compliance records endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/compliance-records", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Compliance records: {len(data)} records found")
    
    def test_tasks_still_work(self):
        """Test tasks endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/tasks", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks: {len(data)} tasks found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
