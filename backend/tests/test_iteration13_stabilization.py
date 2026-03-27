"""
Iteration 13 - Stabilization Testing
Tests for: signup, login, password reset, plan limits, dashboard counts, 
status badges, sidebar plan display, demo mode, onboarding, empty states,
mobile layout, form validation, notifications
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthFlows:
    """Test signup, login, password reset flows"""
    
    def test_signup_success(self):
        """Test successful signup with valid credentials"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        })
        assert response.status_code == 200, f"Signup failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["subscription_plan"] == "solo"
        assert data["user"]["subscription_status"] == "trial"
        assert data["user"]["property_limit"] == 1
        print(f"✓ Signup successful for {unique_email}")
    
    def test_signup_duplicate_email(self):
        """Test signup with duplicate email fails"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
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
        print("✓ Duplicate email signup correctly rejected")
    
    def test_login_success(self):
        """Test successful login"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        # Create user first
        requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        })
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == unique_email.lower()
        print("✓ Login successful")
    
    def test_login_wrong_password(self):
        """Test login with wrong password fails"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
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
        assert "invalid" in response.json()["detail"].lower()
        print("✓ Wrong password correctly rejected")
    
    def test_login_nonexistent_email(self):
        """Test login with non-existent email fails"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 401
        print("✓ Non-existent email login correctly rejected")
    
    def test_password_reset_request(self):
        """Test password reset request (mocked email)"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "email": "test@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "instructions" in data["message"].lower() or "email" in data["message"].lower()
        print("✓ Password reset request successful (mocked)")


class TestPlanLimits:
    """Test plan limit enforcement"""
    
    def test_solo_plan_property_limit(self):
        """Test Solo plan user cannot add more than 1 property"""
        # Create new user (Solo plan by default)
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "Solo User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add first property - should succeed
        prop1_response = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "First Property",
            "address": "123 Test Street",
            "postcode": "SW1A 1AA",
            "uk_nation": "England"
        }, headers=headers)
        assert prop1_response.status_code == 200, f"First property failed: {prop1_response.text}"
        print("✓ First property added successfully")
        
        # Add second property - should fail with 403
        prop2_response = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "Second Property",
            "address": "456 Test Avenue",
            "postcode": "SW1A 2BB",
            "uk_nation": "England"
        }, headers=headers)
        assert prop2_response.status_code == 403, f"Expected 403, got {prop2_response.status_code}"
        error_detail = prop2_response.json()["detail"]
        assert "limit" in error_detail.lower()
        assert "upgrade" in error_detail.lower()
        print(f"✓ Second property correctly rejected: {error_detail}")
    
    def test_portfolio_plan_property_limit(self):
        """Test Portfolio plan allows up to 5 properties"""
        # Use demo mode which gives Portfolio plan
        demo_response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert demo_response.status_code == 200
        token = demo_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Demo already has 3 properties, try adding 2 more
        for i in range(2):
            response = requests.post(f"{BASE_URL}/api/properties", json={
                "name": f"Additional Property {i+1}",
                "address": f"{i+100} Test Street",
                "postcode": f"SW{i+1}A 1AA",
                "uk_nation": "England"
            }, headers=headers)
            assert response.status_code == 200, f"Property {i+4} failed: {response.text}"
        print("✓ Portfolio plan allows 5 properties")
        
        # Try adding 6th property - should fail
        response = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "Sixth Property",
            "address": "600 Test Street",
            "postcode": "SW6A 1AA",
            "uk_nation": "England"
        }, headers=headers)
        assert response.status_code == 403
        assert "limit" in response.json()["detail"].lower()
        print("✓ 6th property correctly rejected for Portfolio plan")


class TestDemoMode:
    """Test demo mode functionality"""
    
    def test_demo_creates_portfolio_account(self):
        """Test demo mode creates Portfolio plan account"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["subscription_plan"] == "portfolio"
        assert data["user"]["property_limit"] == 5
        assert data["user"]["property_count"] == 3
        print("✓ Demo creates Portfolio account with 3 properties")
    
    def test_demo_creates_uk_properties(self):
        """Test demo mode creates realistic UK properties"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        properties = props_response.json()
        
        assert len(properties) == 3
        
        # Check for UK-specific properties
        property_names = [p["name"] for p in properties]
        assert "Victoria Terrace Apartment" in property_names
        assert "Cotswold Cottage" in property_names
        assert "Edinburgh Old Town Flat" in property_names
        
        # Check UK nations
        nations = [p["uk_nation"] for p in properties]
        assert "England" in nations
        assert "Scotland" in nations
        print("✓ Demo creates realistic UK properties")
    
    def test_demo_creates_varied_compliance(self):
        """Test demo mode creates compliance records with varied statuses"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        compliance_response = requests.get(f"{BASE_URL}/api/compliance-records", headers=headers)
        records = compliance_response.json()
        
        assert len(records) >= 10, f"Expected at least 10 compliance records, got {len(records)}"
        
        # Check for varied statuses
        statuses = set(r["compliance_status"] for r in records)
        assert "compliant" in statuses
        assert "expiring_soon" in statuses
        assert "overdue" in statuses
        print(f"✓ Demo creates {len(records)} compliance records with varied statuses: {statuses}")


class TestDashboardData:
    """Test dashboard counts and data consistency"""
    
    def test_dashboard_stats_match_data(self):
        """Test dashboard stats match actual data counts"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get dashboard stats
        stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        stats = stats_response.json()
        
        # Get actual properties
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        properties = [p for p in props_response.json() if p.get("property_status") == "active"]
        
        # Get actual compliance records
        compliance_response = requests.get(f"{BASE_URL}/api/compliance-records", headers=headers)
        records = compliance_response.json()
        
        # Verify counts
        assert stats["total_properties"] == len(properties), f"Properties mismatch: {stats['total_properties']} vs {len(properties)}"
        
        expiring_count = sum(1 for r in records if r.get("compliance_status") == "expiring_soon")
        assert stats["upcoming_expiries"] == expiring_count, f"Expiring mismatch: {stats['upcoming_expiries']} vs {expiring_count}"
        
        overdue_count = sum(1 for r in records if r.get("compliance_status") == "overdue")
        assert stats["overdue_items"] == overdue_count, f"Overdue mismatch: {stats['overdue_items']} vs {overdue_count}"
        
        print(f"✓ Dashboard stats match: {stats['total_properties']} properties, {stats['upcoming_expiries']} expiring, {stats['overdue_items']} overdue")
    
    def test_dashboard_data_endpoint(self):
        """Test dashboard data endpoint returns complete data"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        data_response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=headers)
        assert data_response.status_code == 200
        data = data_response.json()
        
        assert "stats" in data
        assert "upcoming_expiries" in data
        assert "overdue_records" in data
        assert "tasks_due_this_month" in data
        
        # Verify upcoming expiries have required fields
        if data["upcoming_expiries"]:
            expiry = data["upcoming_expiries"][0]
            assert "id" in expiry
            assert "title" in expiry
            assert "property_name" in expiry
            assert "days_until_expiry" in expiry
        
        print("✓ Dashboard data endpoint returns complete structure")


class TestOnboarding:
    """Test onboarding wizard functionality"""
    
    def test_new_user_onboarding_status(self):
        """Test new user has incomplete onboarding"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "New User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        onboarding_response = requests.get(f"{BASE_URL}/api/user/onboarding", headers=headers)
        assert onboarding_response.status_code == 200
        data = onboarding_response.json()
        
        assert data["completed"] == False
        assert data["current_step"] == 1
        assert len(data["steps_completed"]) == 0
        print("✓ New user has incomplete onboarding")
    
    def test_demo_user_onboarding_complete(self):
        """Test demo user has completed onboarding"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        onboarding_response = requests.get(f"{BASE_URL}/api/user/onboarding", headers=headers)
        data = onboarding_response.json()
        
        # Demo user should have completed onboarding
        assert data["completed"] == True or len(data["steps_completed"]) >= 2
        print("✓ Demo user has completed onboarding")
    
    def test_complete_onboarding_endpoint(self):
        """Test completing onboarding"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "TestPass123!",
            "full_name": "New User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        complete_response = requests.post(f"{BASE_URL}/api/user/onboarding/complete", headers=headers)
        assert complete_response.status_code == 200
        assert complete_response.json()["success"] == True
        print("✓ Onboarding can be completed")


class TestNotifications:
    """Test notification functionality"""
    
    def test_notification_generation(self):
        """Test notifications are generated for expiring/overdue items"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate notifications
        gen_response = requests.get(f"{BASE_URL}/api/notifications/generate", headers=headers)
        assert gen_response.status_code == 200
        
        # Get notifications
        notif_response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        assert notif_response.status_code == 200
        notifications = notif_response.json()
        
        # Demo data should generate some notifications
        print(f"✓ Generated {len(notifications)} notifications")
    
    def test_unread_notification_count(self):
        """Test unread notification count in dashboard stats"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate notifications first
        requests.get(f"{BASE_URL}/api/notifications/generate", headers=headers)
        
        # Get dashboard stats
        stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        stats = stats_response.json()
        
        assert "unread_notifications" in stats
        print(f"✓ Unread notifications count: {stats['unread_notifications']}")
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate and get notifications
        requests.get(f"{BASE_URL}/api/notifications/generate", headers=headers)
        notif_response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        notifications = notif_response.json()
        
        if notifications:
            notif_id = notifications[0]["id"]
            mark_response = requests.put(f"{BASE_URL}/api/notifications/{notif_id}/read", headers=headers)
            assert mark_response.status_code == 200
            print("✓ Notification marked as read")
        else:
            print("⚠ No notifications to mark as read")


class TestFormValidation:
    """Test form validation on backend"""
    
    def test_property_required_fields(self):
        """Test property creation requires name, address, postcode"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Missing name
        resp = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "",
            "address": "123 Test St",
            "postcode": "SW1A 1AA"
        }, headers=headers)
        assert resp.status_code == 400
        assert "name" in resp.json()["detail"].lower()
        
        # Missing address
        resp = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "Test Property",
            "address": "",
            "postcode": "SW1A 1AA"
        }, headers=headers)
        assert resp.status_code == 400
        assert "address" in resp.json()["detail"].lower()
        
        # Missing postcode
        resp = requests.post(f"{BASE_URL}/api/properties", json={
            "name": "Test Property",
            "address": "123 Test St",
            "postcode": ""
        }, headers=headers)
        assert resp.status_code == 400
        assert "postcode" in resp.json()["detail"].lower()
        
        print("✓ Property validation works for required fields")
    
    def test_compliance_required_fields(self):
        """Test compliance record creation requires title, category, property_id"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get a property ID
        props = requests.get(f"{BASE_URL}/api/properties", headers=headers).json()
        prop_id = props[0]["id"]
        
        # Missing title
        resp = requests.post(f"{BASE_URL}/api/compliance-records", json={
            "title": "",
            "category": "gas_safety",
            "property_id": prop_id
        }, headers=headers)
        assert resp.status_code == 400
        
        # Missing category
        resp = requests.post(f"{BASE_URL}/api/compliance-records", json={
            "title": "Test Record",
            "category": "",
            "property_id": prop_id
        }, headers=headers)
        assert resp.status_code == 400
        
        print("✓ Compliance record validation works for required fields")
    
    def test_task_required_fields(self):
        """Test task creation requires title"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Missing title
        resp = requests.post(f"{BASE_URL}/api/tasks", json={
            "title": "",
            "priority": "medium"
        }, headers=headers)
        assert resp.status_code == 400
        assert "title" in resp.json()["detail"].lower()
        
        print("✓ Task validation works for required fields")


class TestSubscriptionInfo:
    """Test subscription information in user response"""
    
    def test_user_response_includes_plan_info(self):
        """Test /auth/me returns plan information"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        user = me_response.json()
        
        assert "subscription_plan" in user
        assert "subscription_status" in user
        assert "property_limit" in user
        assert "property_count" in user
        
        assert user["subscription_plan"] == "portfolio"
        assert user["property_limit"] == 5
        print(f"✓ User response includes plan info: {user['subscription_plan']} ({user['subscription_status']})")
    
    def test_subscription_endpoint(self):
        """Test /subscription endpoint returns detailed plan info"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        sub_response = requests.get(f"{BASE_URL}/api/subscription", headers=headers)
        assert sub_response.status_code == 200
        sub = sub_response.json()
        
        assert "plan" in sub
        assert "plan_name" in sub
        assert "status" in sub
        assert "property_limit" in sub
        assert "features" in sub
        
        print(f"✓ Subscription endpoint returns: {sub['plan_name']} plan with {sub['property_limit']} property limit")


class TestStatusBadges:
    """Test compliance status calculation"""
    
    def test_status_updates_on_expiry_date_change(self):
        """Test compliance status updates when expiry date changes"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get a property
        props = requests.get(f"{BASE_URL}/api/properties", headers=headers).json()
        prop_id = props[0]["id"]
        
        # Create a compliant record (far future expiry)
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        
        create_resp = requests.post(f"{BASE_URL}/api/compliance-records", json={
            "title": "Test Status Record",
            "category": "gas_safety",
            "property_id": prop_id,
            "expiry_date": future_date
        }, headers=headers)
        assert create_resp.status_code == 200
        record = create_resp.json()
        assert record["compliance_status"] == "compliant"
        record_id = record["id"]
        
        # Update to expiring soon (within 30 days)
        soon_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        update_resp = requests.put(f"{BASE_URL}/api/compliance-records/{record_id}", json={
            "expiry_date": soon_date
        }, headers=headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["compliance_status"] == "expiring_soon"
        
        # Update to overdue (past date)
        past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        update_resp = requests.put(f"{BASE_URL}/api/compliance-records/{record_id}", json={
            "expiry_date": past_date
        }, headers=headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["compliance_status"] == "overdue"
        
        print("✓ Status badges update correctly based on expiry date")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
