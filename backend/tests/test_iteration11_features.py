"""
Test iteration 11 features:
- Settings page endpoints (preferences, password change, contact form)
- PDF export endpoint
- Demo mode still works
- Basic auth flow
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")

class TestAuthFlow:
    """Test basic authentication flow"""
    
    def test_signup_new_user(self):
        """Test user signup"""
        unique_email = f"test_iter11_{int(time.time())}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test User Iter11"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
        print(f"✓ Signup working - created user {unique_email}")
        return data["token"], unique_email
    
    def test_login_existing_user(self):
        """Test login with existing user"""
        # First create a user
        unique_email = f"test_login_{int(time.time())}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test Login User"
        })
        assert signup_response.status_code == 200
        
        # Now login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        assert "token" in data
        assert data["user"]["email"] == unique_email
        print(f"✓ Login working for {unique_email}")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")

class TestDemoMode:
    """Test demo mode functionality"""
    
    def test_demo_mode_creates_account(self):
        """Test demo mode creates account with seed data"""
        response = requests.post(f"{BASE_URL}/api/auth/demo")
        assert response.status_code == 200
        data = response.json()
        
        # Verify user created
        assert "token" in data
        assert "user" in data
        assert data["user"]["full_name"] == "Demo User"
        assert data["user"]["subscription_plan"] == "portfolio"
        assert data["user"]["property_count"] == 3
        
        print("✓ Demo mode creates account with 3 properties")
        return data["token"]
    
    def test_demo_mode_has_properties(self):
        """Test demo mode has seeded properties"""
        # Create demo account
        demo_response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = demo_response.json()["token"]
        
        # Get properties
        headers = {"Authorization": f"Bearer {token}"}
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        assert props_response.status_code == 200
        properties = props_response.json()
        
        assert len(properties) == 3
        property_names = [p["name"] for p in properties]
        assert "Victoria Terrace Apartment" in property_names
        assert "Cotswold Cottage" in property_names
        assert "Edinburgh Old Town Flat" in property_names
        
        print("✓ Demo mode has 3 seeded properties")

class TestUserPreferences:
    """Test user preferences endpoints (Settings Account & Notifications tabs)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        import random
        unique_email = f"test_prefs_{int(time.time())}_{random.randint(1000,9999)}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test Prefs User"
        })
        if response.status_code != 200:
            pytest.skip(f"Could not create test user: {response.text}")
        return response.json()["token"]
    
    def test_get_default_preferences(self, auth_token):
        """Test getting default preferences"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/user/preferences", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check default values
        assert data["email_reminders"] == True
        assert data["inapp_reminders"] == True
        assert data["reminder_lead_days"] == [90, 60, 30, 7]
        assert data["weekly_digest"] == True
        assert data["marketing_emails"] == False
        
        print("✓ Default preferences returned correctly")
    
    def test_update_company_name(self, auth_token):
        """Test updating company name (Account tab)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/user/preferences", 
            headers=headers,
            json={"company_name": "Test Company Ltd"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Test Company Ltd"
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/user/preferences", headers=headers)
        assert get_response.json()["company_name"] == "Test Company Ltd"
        
        print("✓ Company name saved and persisted")
    
    def test_update_notification_preferences(self, auth_token):
        """Test updating notification preferences (Notifications tab)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/user/preferences", 
            headers=headers,
            json={
                "email_reminders": False,
                "inapp_reminders": True,
                "weekly_digest": False,
                "marketing_emails": True,
                "reminder_lead_days": [60, 30, 7]
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["email_reminders"] == False
        assert data["inapp_reminders"] == True
        assert data["weekly_digest"] == False
        assert data["marketing_emails"] == True
        assert data["reminder_lead_days"] == [60, 30, 7]
        
        print("✓ Notification preferences updated correctly")

class TestPasswordChange:
    """Test password change endpoint (Settings Security tab)"""
    
    def test_change_password_success(self):
        """Test successful password change"""
        # Create user
        unique_email = f"test_pwd_{int(time.time())}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "oldpassword123",
            "full_name": "Test Password User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Change password
        response = requests.post(f"{BASE_URL}/api/auth/change-password",
            headers=headers,
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Password changed successfully" in data["message"]
        
        # Verify can login with new password
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "newpassword456"
        })
        assert login_response.status_code == 200
        
        # Verify old password no longer works
        old_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "oldpassword123"
        })
        assert old_login.status_code == 401
        
        print("✓ Password change working correctly")
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        # Create user
        unique_email = f"test_pwd_wrong_{int(time.time())}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "correctpassword",
            "full_name": "Test Wrong Password"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to change with wrong current password
        response = requests.post(f"{BASE_URL}/api/auth/change-password",
            headers=headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()
        
        print("✓ Wrong current password correctly rejected")

class TestContactForm:
    """Test contact form endpoint (Settings Support tab)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        import random
        unique_email = f"test_contact_{int(time.time())}_{random.randint(1000,9999)}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test Contact User"
        })
        if response.status_code != 200:
            pytest.skip(f"Could not create test user: {response.text}")
        return response.json()["token"]
    
    def test_submit_support_request(self, auth_token):
        """Test submitting a support request"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/contact",
            headers=headers,
            json={
                "subject": "Test Support Request",
                "message": "This is a test support message",
                "contact_type": "support"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        print("✓ Support request submitted successfully")
    
    def test_submit_billing_inquiry(self, auth_token):
        """Test submitting a billing inquiry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/contact",
            headers=headers,
            json={
                "subject": "Billing Question",
                "message": "Question about my subscription",
                "contact_type": "billing"
            }
        )
        assert response.status_code == 200
        
        print("✓ Billing inquiry submitted successfully")
    
    def test_submit_feedback(self, auth_token):
        """Test submitting feedback"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/contact",
            headers=headers,
            json={
                "subject": "Feature Feedback",
                "message": "Great app, love the compliance tracking!",
                "contact_type": "feedback"
            }
        )
        assert response.status_code == 200
        
        print("✓ Feedback submitted successfully")

class TestPDFExport:
    """Test PDF export endpoint"""
    
    def test_export_property_report(self):
        """Test exporting a property compliance report as PDF"""
        # Create demo account (has properties with compliance records)
        demo_response = requests.post(f"{BASE_URL}/api/auth/demo")
        token = demo_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get first property
        props_response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        properties = props_response.json()
        assert len(properties) > 0
        property_id = properties[0]["id"]
        property_name = properties[0]["name"]
        
        # Export PDF
        export_response = requests.get(
            f"{BASE_URL}/api/properties/{property_id}/export",
            headers=headers
        )
        assert export_response.status_code == 200
        
        # Verify it's a PDF
        content_type = export_response.headers.get("content-type", "")
        assert "application/pdf" in content_type
        
        # Verify content disposition header
        content_disp = export_response.headers.get("content-disposition", "")
        assert "attachment" in content_disp
        assert "compliance_report.pdf" in content_disp
        
        # Verify PDF content starts with PDF header
        pdf_content = export_response.content
        assert pdf_content[:4] == b'%PDF'
        assert len(pdf_content) > 1000  # Should be a reasonable size
        
        print(f"✓ PDF export working for property '{property_name}' ({len(pdf_content)} bytes)")
    
    def test_export_nonexistent_property(self):
        """Test export for non-existent property returns 404"""
        # Create user
        unique_email = f"test_export_{int(time.time())}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test Export User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to export non-existent property
        response = requests.get(
            f"{BASE_URL}/api/properties/nonexistent-id/export",
            headers=headers
        )
        assert response.status_code == 404
        
        print("✓ Export for non-existent property correctly returns 404")

class TestAuthMe:
    """Test /auth/me endpoint for user info"""
    
    def test_get_current_user(self):
        """Test getting current user info"""
        # Create user
        unique_email = f"test_me_{int(time.time())}@test.com"
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test Me User"
        })
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current user
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == unique_email
        assert data["full_name"] == "Test Me User"
        assert "subscription_plan" in data
        assert "subscription_status" in data
        
        print("✓ /auth/me endpoint working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
