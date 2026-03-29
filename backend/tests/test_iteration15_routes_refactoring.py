"""
Iteration 15 - Routes Refactoring Verification Tests
Tests all modular routes after server.py refactoring from 2100+ to 870 lines.
Route modules: auth.py, properties.py, compliance.py, tasks.py, notifications.py, billing.py
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndConstants:
    """Basic health and constants endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health endpoint returns healthy status")
    
    def test_constants_endpoint(self):
        """Test /api/constants returns all required constants"""
        response = requests.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        data = response.json()
        assert "uk_nations" in data
        assert "property_types" in data
        assert "compliance_categories" in data
        assert "subscription_plans" in data
        print("PASS: Constants endpoint returns all required constants")


class TestAuthRoutes:
    """Test auth routes from /routes/auth.py"""
    
    def test_demo_mode_creates_account(self):
        """Test POST /api/auth/demo creates demo account with Portfolio plan"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["subscription_plan"] == "portfolio"
        assert data["user"]["full_name"] == "Demo User"
        print("PASS: Demo mode creates Portfolio account")
        return data["token"]
    
    def test_signup_creates_solo_account(self):
        """Test POST /api/auth/signup creates Solo plan account"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["subscription_plan"] == "solo"
        assert data["user"]["subscription_status"] == "trial"
        print(f"PASS: Signup creates Solo trial account for {unique_email}")
        return data["token"], unique_email
    
    def test_signup_duplicate_email_fails(self):
        """Test signup with duplicate email returns 400"""
        # First signup
        unique_email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test User"
        })
        # Second signup with same email
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test User 2"
        })
        assert response.status_code == 400
        print("PASS: Duplicate email signup returns 400")
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        # Create account first
        unique_email = f"login_{uuid.uuid4().hex[:8]}@test.com"
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Login Test"
        })
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print("PASS: Login with valid credentials works")
    
    def test_login_with_invalid_password(self):
        """Test login with wrong password returns 401"""
        unique_email = f"wrongpw_{uuid.uuid4().hex[:8]}@test.com"
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Wrong PW Test"
        })
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("PASS: Login with wrong password returns 401")
    
    def test_get_me_endpoint(self):
        """Test GET /api/auth/me returns current user"""
        # Get demo token
        demo_response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = demo_response.json()["token"]
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "full_name" in data
        print("PASS: GET /auth/me returns current user")
    
    def test_password_reset_request(self):
        """Test POST /api/auth/reset-password (MOCKED - no email sent)"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "email": "test@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("PASS: Password reset request returns success (MOCKED)")
    
    def test_change_password(self):
        """Test POST /api/auth/change-password"""
        # Create account
        unique_email = f"changepw_{uuid.uuid4().hex[:8]}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "oldpassword123",
            "full_name": "Change PW Test"
        })
        token = signup_response.json()["token"]
        
        # Change password
        response = requests.post(f"{BASE_URL}/api/auth/change-password", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 200
        print("PASS: Change password works")


class TestPropertiesRoutes:
    """Test properties routes from /routes/properties.py"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_get_properties(self, auth_token):
        """Test GET /api/properties returns list"""
        response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Demo creates 3 properties
        print(f"PASS: GET /properties returns {len(data)} properties")
    
    def test_create_property(self, auth_token):
        """Test POST /api/properties creates property"""
        response = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test Property",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA",
                "uk_nation": "England",
                "is_in_london": True,
                "property_type": "apartment",
                "ownership_type": "owned",
                "bedrooms": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Property"
        print("PASS: Create property works")
        return data["id"]
    
    def test_get_property_by_id(self, auth_token):
        """Test GET /api/properties/{id} returns property"""
        # Get properties first
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.get(f"{BASE_URL}/api/properties/{prop_id}", headers={
                "Authorization": f"Bearer {auth_token}"
            })
            assert response.status_code == 200
            print("PASS: GET property by ID works")
    
    def test_update_property(self, auth_token):
        """Test PUT /api/properties/{id} updates property"""
        # Get properties first
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.put(f"{BASE_URL}/api/properties/{prop_id}", 
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"notes": "Updated notes"}
            )
            assert response.status_code == 200
            print("PASS: Update property works")
    
    def test_property_export_pdf(self, auth_token):
        """Test GET /api/properties/{id}/export returns PDF"""
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.get(f"{BASE_URL}/api/properties/{prop_id}/export", headers={
                "Authorization": f"Bearer {auth_token}"
            })
            assert response.status_code == 200
            assert "application/pdf" in response.headers.get("content-type", "")
            print("PASS: Property PDF export works")


class TestComplianceRoutes:
    """Test compliance routes from /routes/compliance.py"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_get_compliance_records(self, auth_token):
        """Test GET /api/compliance-records returns list"""
        response = requests.get(f"{BASE_URL}/api/compliance-records", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 10  # Demo creates 12 compliance records
        print(f"PASS: GET /compliance-records returns {len(data)} records")
    
    def test_create_compliance_record(self, auth_token):
        """Test POST /api/compliance-records creates record"""
        # Get a property ID first
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.post(f"{BASE_URL}/api/compliance-records", 
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "property_id": prop_id,
                    "title": "Test Compliance Record",
                    "category": "gas_safety",
                    "expiry_date": "2026-12-31"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Compliance Record"
            print("PASS: Create compliance record works")
            return data["id"]
    
    def test_update_compliance_record(self, auth_token):
        """Test PUT /api/compliance-records/{id} updates record"""
        records_response = requests.get(f"{BASE_URL}/api/compliance-records", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        records = records_response.json()
        if records:
            record_id = records[0]["id"]
            response = requests.put(f"{BASE_URL}/api/compliance-records/{record_id}", 
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"notes": "Updated compliance notes"}
            )
            assert response.status_code == 200
            print("PASS: Update compliance record works")
    
    def test_get_record_documents(self, auth_token):
        """Test GET /api/compliance-records/{id}/documents"""
        records_response = requests.get(f"{BASE_URL}/api/compliance-records", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        records = records_response.json()
        if records:
            record_id = records[0]["id"]
            response = requests.get(f"{BASE_URL}/api/compliance-records/{record_id}/documents", headers={
                "Authorization": f"Bearer {auth_token}"
            })
            assert response.status_code == 200
            print("PASS: Get compliance record documents works")


class TestTasksRoutes:
    """Test tasks routes from /routes/tasks.py"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_get_tasks(self, auth_token):
        """Test GET /api/tasks returns list"""
        response = requests.get(f"{BASE_URL}/api/tasks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5  # Demo creates 6 tasks
        print(f"PASS: GET /tasks returns {len(data)} tasks")
    
    def test_get_task_templates(self, auth_token):
        """Test GET /api/tasks/templates returns templates"""
        response = requests.get(f"{BASE_URL}/api/tasks/templates", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        print(f"PASS: GET /tasks/templates returns {len(data)} templates")
    
    def test_create_task(self, auth_token):
        """Test POST /api/tasks creates task"""
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.post(f"{BASE_URL}/api/tasks", 
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "property_id": prop_id,
                    "title": "Test Task",
                    "description": "Test task description",
                    "priority": "high",
                    "category": "maintenance"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Task"
            print("PASS: Create task works")
            return data["id"]
    
    def test_update_task(self, auth_token):
        """Test PUT /api/tasks/{id} updates task"""
        tasks_response = requests.get(f"{BASE_URL}/api/tasks", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        tasks = tasks_response.json()
        if tasks:
            task_id = tasks[0]["id"]
            response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"task_status": "in_progress"}
            )
            assert response.status_code == 200
            print("PASS: Update task works")


class TestNotificationsRoutes:
    """Test notifications routes from /routes/notifications.py"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_generate_notifications(self, auth_token):
        """Test GET /api/notifications/generate"""
        response = requests.get(f"{BASE_URL}/api/notifications/generate", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        print(f"PASS: Generate notifications created {data['created']} notifications")
    
    def test_get_notifications(self, auth_token):
        """Test GET /api/notifications returns list"""
        # Generate first
        requests.get(f"{BASE_URL}/api/notifications/generate", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        response = requests.get(f"{BASE_URL}/api/notifications", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /notifications returns {len(data)} notifications")
    
    def test_mark_all_read(self, auth_token):
        """Test PUT /api/notifications/read-all"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        print("PASS: Mark all notifications read works")
    
    def test_get_user_preferences(self, auth_token):
        """Test GET /api/user/preferences"""
        response = requests.get(f"{BASE_URL}/api/user/preferences", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "email_reminders" in data
        assert "inapp_reminders" in data
        print("PASS: GET /user/preferences works")
    
    def test_update_user_preferences(self, auth_token):
        """Test PUT /api/user/preferences"""
        response = requests.put(f"{BASE_URL}/api/user/preferences", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"company_name": "Test Company"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Test Company"
        print("PASS: Update user preferences works")


class TestBillingRoutes:
    """Test billing routes from /routes/billing.py"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_get_subscription(self, auth_token):
        """Test GET /api/subscription returns subscription details"""
        response = requests.get(f"{BASE_URL}/api/subscription", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "plan_name" in data
        assert "property_limit" in data
        assert "features" in data
        print(f"PASS: GET /subscription returns {data['plan_name']} plan")
    
    def test_get_subscription_plans(self, auth_token):
        """Test GET /api/subscription/plans returns all plans"""
        response = requests.get(f"{BASE_URL}/api/subscription/plans", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "solo" in data["plans"]
        assert "portfolio" in data["plans"]
        assert "operator" in data["plans"]
        print("PASS: GET /subscription/plans returns all 3 plans")
    
    def test_check_property_limit(self, auth_token):
        """Test GET /api/subscription/check-limit"""
        response = requests.get(f"{BASE_URL}/api/subscription/check-limit", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "allowed" in data
        assert "current_count" in data
        assert "limit" in data
        print(f"PASS: Check property limit: {data['current_count']}/{data['limit']}")


class TestDashboardRoutes:
    """Test dashboard routes (still in server.py)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_dashboard_stats(self, auth_token):
        """Test GET /api/dashboard/stats"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "total_properties" in data
        assert "upcoming_expiries" in data
        assert "overdue_items" in data
        assert "tasks_due" in data
        print(f"PASS: Dashboard stats: {data['total_properties']} properties, {data['tasks_due']} tasks due")
    
    def test_dashboard_data(self, auth_token):
        """Test GET /api/dashboard/data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "upcoming_expiries" in data
        assert "overdue_records" in data
        assert "tasks_due_this_month" in data
        print("PASS: Dashboard data returns complete structure")


class TestAIAssistantRoutes:
    """Test AI assistant routes (still in server.py)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_ai_insights(self, auth_token):
        """Test GET /api/assistant/insights"""
        response = requests.get(f"{BASE_URL}/api/assistant/insights", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data or "property_risks" in data or "insights" in data
        print("PASS: AI insights endpoint works")
    
    def test_ai_ask(self, auth_token):
        """Test POST /api/assistant/ask"""
        response = requests.post(f"{BASE_URL}/api/assistant/ask", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"question": "What compliance items are expiring soon?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data or "response" in data
        print("PASS: AI ask endpoint works")
    
    def test_ai_property_insights(self, auth_token):
        """Test GET /api/assistant/property/{id}"""
        props_response = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        props = props_response.json()
        if props:
            prop_id = props[0]["id"]
            response = requests.get(f"{BASE_URL}/api/assistant/property/{prop_id}", headers={
                "Authorization": f"Bearer {auth_token}"
            })
            assert response.status_code == 200
            print("PASS: AI property insights endpoint works")


class TestOnboardingRoutes:
    """Test onboarding routes (still in server.py)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get demo auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        return response.json()["token"]
    
    def test_get_onboarding_status(self, auth_token):
        """Test GET /api/user/onboarding"""
        response = requests.get(f"{BASE_URL}/api/user/onboarding", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "completed" in data
        assert "current_step" in data
        assert "steps_completed" in data
        print("PASS: Get onboarding status works")
    
    def test_complete_onboarding(self, auth_token):
        """Test POST /api/user/onboarding/complete"""
        response = requests.post(f"{BASE_URL}/api/user/onboarding/complete", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        print("PASS: Complete onboarding works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
