"""
Iteration 14 - Refactoring Verification Tests
Tests to verify that the modular refactoring didn't break any existing functionality.
Auth routes moved to /routes/auth.py, constants to /utils/constants.py, etc.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("PASS: Health endpoint working")

    def test_constants_endpoint(self):
        """Constants endpoint should return UK nations, property types, etc."""
        response = requests.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        data = response.json()
        assert "uk_nations" in data
        assert "property_types" in data
        assert "compliance_categories" in data
        assert "England" in data["uk_nations"]
        print("PASS: Constants endpoint working")


class TestAuthRoutes:
    """Test auth routes after refactoring to /routes/auth.py"""
    
    def test_signup_creates_user(self):
        """Signup should create a new user with Solo plan"""
        unique_email = f"test_refactor_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Refactor User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["subscription_plan"] == "solo"
        assert data["user"]["subscription_status"] == "trial"
        print(f"PASS: Signup creates user with Solo plan - {unique_email}")
        return data["token"]
    
    def test_signup_duplicate_email_fails(self):
        """Signup with duplicate email should return 400"""
        unique_email = f"test_dup_{uuid.uuid4().hex[:8]}@test.com"
        # First signup
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        })
        # Second signup with same email
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User 2"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
        print("PASS: Duplicate email signup returns 400")
    
    def test_login_valid_credentials(self):
        """Login with valid credentials should return token"""
        unique_email = f"test_login_{uuid.uuid4().hex[:8]}@test.com"
        # Create user first
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Login User"
        })
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print("PASS: Login with valid credentials works")
        return data["token"]
    
    def test_login_invalid_password(self):
        """Login with wrong password should return 401"""
        unique_email = f"test_wrongpw_{uuid.uuid4().hex[:8]}@test.com"
        # Create user first
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        })
        # Login with wrong password
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        assert response.status_code == 401
        print("PASS: Login with wrong password returns 401")
    
    def test_login_nonexistent_email(self):
        """Login with non-existent email should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": f"nonexistent_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 401
        print("PASS: Login with non-existent email returns 401")
    
    def test_password_reset_request(self):
        """Password reset should return success (email mocked)"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "email": "any@email.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "receive password reset" in data["message"].lower()
        print("PASS: Password reset returns success (MOCKED - no email sent)")
    
    def test_me_endpoint_with_token(self):
        """GET /auth/me should return current user info"""
        unique_email = f"test_me_{uuid.uuid4().hex[:8]}@test.com"
        # Create user and get token
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Me User"
        })
        token = signup_resp.json()["token"]
        
        # Get current user
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == unique_email.lower()
        assert data["full_name"] == "Test Me User"
        print("PASS: GET /auth/me returns current user")
    
    def test_change_password(self):
        """Change password should work with valid current password"""
        unique_email = f"test_changepw_{uuid.uuid4().hex[:8]}@test.com"
        # Create user and get token
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "OldPass123!",
            "full_name": "Test Change PW"
        })
        token = signup_resp.json()["token"]
        
        # Change password
        response = requests.post(f"{BASE_URL}/api/auth/change-password", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "OldPass123!",
                "new_password": "NewPass456!"
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Verify new password works
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "NewPass456!"
        })
        assert login_resp.status_code == 200
        print("PASS: Change password works")
    
    def test_change_password_wrong_current(self):
        """Change password with wrong current password should fail"""
        unique_email = f"test_wrongcurr_{uuid.uuid4().hex[:8]}@test.com"
        # Create user and get token
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        })
        token = signup_resp.json()["token"]
        
        # Try to change with wrong current password
        response = requests.post(f"{BASE_URL}/api/auth/change-password", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "WrongCurrent!",
                "new_password": "NewPass456!"
            }
        )
        assert response.status_code == 400
        print("PASS: Change password with wrong current fails")


class TestDemoMode:
    """Test demo mode creates proper data"""
    
    def test_demo_creates_portfolio_account(self):
        """Demo mode should create Portfolio plan account with sample data"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        assert data["user"]["subscription_plan"] == "portfolio"
        assert data["user"]["subscription_status"] == "trial"
        assert data["user"]["property_count"] == 3
        assert data["user"]["full_name"] == "Demo User"
        print("PASS: Demo mode creates Portfolio account with 3 properties")
        return data["token"]
    
    def test_demo_creates_properties(self):
        """Demo mode should create 3 UK properties"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get properties
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        assert props_resp.status_code == 200
        properties = props_resp.json()
        assert len(properties) == 3
        
        # Check property names
        names = [p["name"] for p in properties]
        assert "Victoria Terrace Apartment" in names
        assert "Cotswold Cottage" in names
        assert "Edinburgh Old Town Flat" in names
        print("PASS: Demo creates 3 UK properties")
    
    def test_demo_creates_compliance_records(self):
        """Demo mode should create compliance records with varied statuses"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get compliance records
        records_resp = requests.get(f"{BASE_URL}/api/compliance-records", headers={
            "Authorization": f"Bearer {token}"
        })
        assert records_resp.status_code == 200
        records = records_resp.json()
        assert len(records) >= 10  # Should have at least 10 records
        
        # Check for varied statuses
        statuses = set(r["compliance_status"] for r in records)
        assert "compliant" in statuses or "expiring_soon" in statuses
        print(f"PASS: Demo creates {len(records)} compliance records with statuses: {statuses}")
    
    def test_demo_creates_tasks(self):
        """Demo mode should create tasks"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get tasks
        tasks_resp = requests.get(f"{BASE_URL}/api/tasks", headers={
            "Authorization": f"Bearer {token}"
        })
        assert tasks_resp.status_code == 200
        tasks = tasks_resp.json()
        assert len(tasks) >= 5  # Should have at least 5 tasks
        print(f"PASS: Demo creates {len(tasks)} tasks")


class TestDashboard:
    """Test dashboard endpoints"""
    
    def test_dashboard_stats(self):
        """Dashboard stats should return correct structure"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        stats_resp = requests.get(f"{BASE_URL}/api/dashboard/stats", headers={
            "Authorization": f"Bearer {token}"
        })
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        
        assert "total_properties" in stats
        assert "upcoming_expiries" in stats
        assert "overdue_items" in stats
        assert "tasks_due" in stats
        assert stats["total_properties"] == 3
        print(f"PASS: Dashboard stats - {stats['total_properties']} properties, {stats['upcoming_expiries']} expiring, {stats['overdue_items']} overdue")
    
    def test_dashboard_data(self):
        """Dashboard data should return complete structure"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        data_resp = requests.get(f"{BASE_URL}/api/dashboard/data", headers={
            "Authorization": f"Bearer {token}"
        })
        assert data_resp.status_code == 200
        data = data_resp.json()
        
        assert "stats" in data
        assert "upcoming_expiries" in data
        assert "overdue_records" in data
        assert "tasks_due_this_month" in data
        print("PASS: Dashboard data returns complete structure")


class TestPropertyCRUD:
    """Test property CRUD operations"""
    
    def test_create_property(self):
        """Create property should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        prop_resp = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Property",
                "address": "123 Test Street",
                "postcode": "SW1A 1AA",
                "uk_nation": "England",
                "property_type": "apartment",
                "bedrooms": 2
            }
        )
        assert prop_resp.status_code == 200
        prop = prop_resp.json()
        assert prop["name"] == "Test Property"
        assert prop["postcode"] == "SW1A 1AA"
        print("PASS: Create property works")
        return prop["id"], token
    
    def test_get_property(self):
        """Get property by ID should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first property
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        prop_id = props_resp.json()[0]["id"]
        
        # Get by ID
        get_resp = requests.get(f"{BASE_URL}/api/properties/{prop_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == prop_id
        print("PASS: Get property by ID works")
    
    def test_update_property(self):
        """Update property should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first property
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        prop_id = props_resp.json()[0]["id"]
        
        # Update
        update_resp = requests.put(f"{BASE_URL}/api/properties/{prop_id}", 
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Property Name"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Updated Property Name"
        print("PASS: Update property works")
    
    def test_delete_property(self):
        """Delete property should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Create a property to delete
        prop_resp = requests.post(f"{BASE_URL}/api/properties", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "To Delete",
                "address": "123 Delete St",
                "postcode": "SW1A 1AA"
            }
        )
        prop_id = prop_resp.json()["id"]
        
        # Delete
        del_resp = requests.delete(f"{BASE_URL}/api/properties/{prop_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert del_resp.status_code == 200
        
        # Verify deleted
        get_resp = requests.get(f"{BASE_URL}/api/properties/{prop_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert get_resp.status_code == 404
        print("PASS: Delete property works")


class TestComplianceCRUD:
    """Test compliance record CRUD operations"""
    
    def test_create_compliance_record(self):
        """Create compliance record should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first property
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        prop_id = props_resp.json()[0]["id"]
        
        # Create compliance record
        record_resp = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "property_id": prop_id,
                "title": "Test Gas Safety",
                "category": "gas_safety",
                "expiry_date": "2026-12-31"
            }
        )
        assert record_resp.status_code == 200
        record = record_resp.json()
        assert record["title"] == "Test Gas Safety"
        assert record["category"] == "gas_safety"
        print("PASS: Create compliance record works")
    
    def test_update_compliance_record(self):
        """Update compliance record should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first compliance record
        records_resp = requests.get(f"{BASE_URL}/api/compliance-records", headers={
            "Authorization": f"Bearer {token}"
        })
        record_id = records_resp.json()[0]["id"]
        
        # Update
        update_resp = requests.put(f"{BASE_URL}/api/compliance-records/{record_id}", 
            headers={"Authorization": f"Bearer {token}"},
            json={"notes": "Updated notes"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["notes"] == "Updated notes"
        print("PASS: Update compliance record works")
    
    def test_delete_compliance_record(self):
        """Delete compliance record should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first property
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        prop_id = props_resp.json()[0]["id"]
        
        # Create a record to delete
        record_resp = requests.post(f"{BASE_URL}/api/compliance-records", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "property_id": prop_id,
                "title": "To Delete",
                "category": "eicr"
            }
        )
        record_id = record_resp.json()["id"]
        
        # Delete
        del_resp = requests.delete(f"{BASE_URL}/api/compliance-records/{record_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert del_resp.status_code == 200
        print("PASS: Delete compliance record works")


class TestTasksCRUD:
    """Test tasks CRUD operations"""
    
    def test_create_task(self):
        """Create task should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        task_resp = requests.post(f"{BASE_URL}/api/tasks", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Task",
                "description": "Test description",
                "priority": "high",
                "category": "maintenance"
            }
        )
        assert task_resp.status_code == 200
        task = task_resp.json()
        assert task["title"] == "Test Task"
        assert task["priority"] == "high"
        print("PASS: Create task works")
    
    def test_update_task(self):
        """Update task should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first task
        tasks_resp = requests.get(f"{BASE_URL}/api/tasks", headers={
            "Authorization": f"Bearer {token}"
        })
        task_id = tasks_resp.json()[0]["id"]
        
        # Update
        update_resp = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
            headers={"Authorization": f"Bearer {token}"},
            json={"task_status": "completed"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["task_status"] == "completed"
        print("PASS: Update task works")
    
    def test_delete_task(self):
        """Delete task should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Create a task to delete
        task_resp = requests.post(f"{BASE_URL}/api/tasks", 
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "To Delete"}
        )
        task_id = task_resp.json()["id"]
        
        # Delete
        del_resp = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers={
            "Authorization": f"Bearer {token}"
        })
        assert del_resp.status_code == 200
        print("PASS: Delete task works")
    
    def test_task_templates(self):
        """Task templates endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/tasks/templates")
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) > 0
        assert any("Gas Safety" in t["title"] for t in templates)
        print(f"PASS: Task templates returns {len(templates)} templates")


class TestAIAssistant:
    """Test AI assistant endpoints"""
    
    def test_ai_insights(self):
        """AI insights endpoint should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        insights_resp = requests.get(f"{BASE_URL}/api/assistant/insights", headers={
            "Authorization": f"Bearer {token}"
        })
        assert insights_resp.status_code == 200
        data = insights_resp.json()
        assert "insights" in data
        print("PASS: AI insights endpoint works")
    
    def test_ai_query(self):
        """AI query endpoint should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        query_resp = requests.post(f"{BASE_URL}/api/assistant/query", 
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "What compliance items are expiring soon?"}
        )
        assert query_resp.status_code == 200
        data = query_resp.json()
        assert "answer" in data
        print("PASS: AI query endpoint works")


class TestPDFExport:
    """Test PDF export functionality"""
    
    def test_property_export(self):
        """Property PDF export should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Get first property
        props_resp = requests.get(f"{BASE_URL}/api/properties", headers={
            "Authorization": f"Bearer {token}"
        })
        prop_id = props_resp.json()[0]["id"]
        
        # Export PDF
        export_resp = requests.get(f"{BASE_URL}/api/properties/{prop_id}/export", headers={
            "Authorization": f"Bearer {token}"
        })
        assert export_resp.status_code == 200
        assert export_resp.headers.get("content-type") == "application/pdf"
        print("PASS: Property PDF export works")


class TestSubscription:
    """Test subscription endpoints"""
    
    def test_get_subscription(self):
        """Get subscription should return plan details"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        sub_resp = requests.get(f"{BASE_URL}/api/subscription", headers={
            "Authorization": f"Bearer {token}"
        })
        assert sub_resp.status_code == 200
        data = sub_resp.json()
        assert data["plan"] == "portfolio"
        assert data["property_limit"] == 5
        print("PASS: Get subscription works")
    
    def test_subscription_plans(self):
        """Get subscription plans should return all plans"""
        response = requests.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "solo" in data["plans"]
        assert "portfolio" in data["plans"]
        assert "operator" in data["plans"]
        print("PASS: Subscription plans endpoint works")
    
    def test_check_property_limit(self):
        """Check property limit should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        limit_resp = requests.get(f"{BASE_URL}/api/subscription/check-limit", headers={
            "Authorization": f"Bearer {token}"
        })
        assert limit_resp.status_code == 200
        data = limit_resp.json()
        assert "allowed" in data
        assert "current_count" in data
        assert "limit" in data
        print(f"PASS: Check limit - {data['current_count']}/{data['limit']} properties")


class TestNotifications:
    """Test notification endpoints"""
    
    def test_generate_notifications(self):
        """Generate notifications should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        gen_resp = requests.get(f"{BASE_URL}/api/notifications/generate", headers={
            "Authorization": f"Bearer {token}"
        })
        assert gen_resp.status_code == 200
        print("PASS: Generate notifications works")
    
    def test_get_notifications(self):
        """Get notifications should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        # Generate first
        requests.get(f"{BASE_URL}/api/notifications/generate", headers={
            "Authorization": f"Bearer {token}"
        })
        
        # Get notifications
        notif_resp = requests.get(f"{BASE_URL}/api/notifications", headers={
            "Authorization": f"Bearer {token}"
        })
        assert notif_resp.status_code == 200
        print("PASS: Get notifications works")


class TestUserPreferences:
    """Test user preferences endpoints"""
    
    def test_get_preferences(self):
        """Get user preferences should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        prefs_resp = requests.get(f"{BASE_URL}/api/user/preferences", headers={
            "Authorization": f"Bearer {token}"
        })
        assert prefs_resp.status_code == 200
        data = prefs_resp.json()
        assert "email_reminders" in data
        assert "inapp_reminders" in data
        print("PASS: Get user preferences works")
    
    def test_update_preferences(self):
        """Update user preferences should work"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        
        update_resp = requests.put(f"{BASE_URL}/api/user/preferences", 
            headers={"Authorization": f"Bearer {token}"},
            json={"company_name": "Test Company"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["company_name"] == "Test Company"
        print("PASS: Update user preferences works")


class TestOnboarding:
    """Test onboarding endpoints"""
    
    def test_get_onboarding_status(self):
        """Get onboarding status should work"""
        unique_email = f"test_onboard_{uuid.uuid4().hex[:8]}@test.com"
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Onboard"
        })
        token = signup_resp.json()["token"]
        
        onboard_resp = requests.get(f"{BASE_URL}/api/user/onboarding", headers={
            "Authorization": f"Bearer {token}"
        })
        assert onboard_resp.status_code == 200
        data = onboard_resp.json()
        assert "completed" in data or "is_complete" in data
        assert "current_step" in data
        print("PASS: Get onboarding status works")
    
    def test_complete_onboarding(self):
        """Complete onboarding should work"""
        unique_email = f"test_complete_{uuid.uuid4().hex[:8]}@test.com"
        signup_resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test Complete"
        })
        token = signup_resp.json()["token"]
        
        complete_resp = requests.post(f"{BASE_URL}/api/user/onboarding/complete", headers={
            "Authorization": f"Bearer {token}"
        })
        assert complete_resp.status_code == 200
        print("PASS: Complete onboarding works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
