"""
Phase 5: Subscription Billing Tests
Tests for subscription plans, trial status, plan limits, and upgrade/downgrade functionality
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_TRIAL = {"email": "trialtest@staylet.com", "password": "Test1234!"}
TEST_USER_AT_LIMIT = {"email": "bugtest@staylet.com", "password": "Test1234!"}

# Expected plan limits
PLAN_LIMITS = {
    "solo": 1,
    "portfolio": 5,
    "operator": 15
}

PLAN_PRICES = {
    "solo": {"monthly": 19, "yearly": 190},
    "portfolio": {"monthly": 39, "yearly": 390},
    "operator": {"monthly": 79, "yearly": 790}
}


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def trial_user_token(api_client):
    """Get auth token for trial test user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=TEST_USER_TRIAL)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Trial user login failed: {response.status_code}")


@pytest.fixture(scope="module")
def limit_user_token(api_client):
    """Get auth token for user at limit"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=TEST_USER_AT_LIMIT)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Limit user login failed: {response.status_code}")


class TestSubscriptionPlansEndpoint:
    """Tests for GET /api/subscription/plans"""
    
    def test_get_plans_returns_all_three_plans(self, api_client):
        """Verify /api/subscription/plans returns Solo, Portfolio, Operator plans"""
        response = api_client.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plans" in data, "Response should contain 'plans' key"
        plans = data["plans"]
        
        # Verify all 3 plans exist
        assert "solo" in plans, "Solo plan missing"
        assert "portfolio" in plans, "Portfolio plan missing"
        assert "operator" in plans, "Operator plan missing"
        print("SUCCESS: All 3 plans returned (Solo, Portfolio, Operator)")
    
    def test_solo_plan_details(self, api_client):
        """Verify Solo plan has correct pricing and limit"""
        response = api_client.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200
        
        solo = response.json()["plans"]["solo"]
        assert solo["name"] == "Solo", f"Expected name 'Solo', got {solo['name']}"
        assert solo["price_monthly"] == 19, f"Expected £19/month, got £{solo['price_monthly']}"
        assert solo["price_yearly"] == 190, f"Expected £190/year, got £{solo['price_yearly']}"
        assert solo["property_limit"] == 1, f"Expected 1 property limit, got {solo['property_limit']}"
        print("SUCCESS: Solo plan - £19/month, 1 property limit")
    
    def test_portfolio_plan_details(self, api_client):
        """Verify Portfolio plan has correct pricing and limit"""
        response = api_client.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200
        
        portfolio = response.json()["plans"]["portfolio"]
        assert portfolio["name"] == "Portfolio", f"Expected name 'Portfolio', got {portfolio['name']}"
        assert portfolio["price_monthly"] == 39, f"Expected £39/month, got £{portfolio['price_monthly']}"
        assert portfolio["price_yearly"] == 390, f"Expected £390/year, got £{portfolio['price_yearly']}"
        assert portfolio["property_limit"] == 5, f"Expected 5 property limit, got {portfolio['property_limit']}"
        print("SUCCESS: Portfolio plan - £39/month, 5 property limit")
    
    def test_operator_plan_details(self, api_client):
        """Verify Operator plan has correct pricing and limit"""
        response = api_client.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200
        
        operator = response.json()["plans"]["operator"]
        assert operator["name"] == "Operator", f"Expected name 'Operator', got {operator['name']}"
        assert operator["price_monthly"] == 79, f"Expected £79/month, got £{operator['price_monthly']}"
        assert operator["price_yearly"] == 790, f"Expected £790/year, got £{operator['price_yearly']}"
        assert operator["property_limit"] == 15, f"Expected 15 property limit, got {operator['property_limit']}"
        print("SUCCESS: Operator plan - £79/month, 15 property limit")
    
    def test_plans_include_trial_days(self, api_client):
        """Verify response includes trial_days constant"""
        response = api_client.get(f"{BASE_URL}/api/subscription/plans")
        assert response.status_code == 200
        
        data = response.json()
        assert "trial_days" in data, "Response should include trial_days"
        assert data["trial_days"] == 14, f"Expected 14 trial days, got {data['trial_days']}"
        print("SUCCESS: Trial days = 14")


class TestSubscriptionEndpoint:
    """Tests for GET /api/subscription (current user's subscription)"""
    
    def test_get_subscription_requires_auth(self, api_client):
        """Verify /api/subscription requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/subscription")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("SUCCESS: /api/subscription requires authentication")
    
    def test_get_subscription_returns_plan_details(self, api_client, trial_user_token):
        """Verify subscription endpoint returns plan details"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/subscription", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check required fields
        required_fields = ["plan", "plan_name", "status", "property_limit", "property_count", 
                          "price_monthly", "price_yearly", "features", "can_upgrade", "can_downgrade"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"SUCCESS: Subscription returns all required fields. Plan: {data['plan_name']}, Status: {data['status']}")
    
    def test_subscription_includes_trial_info(self, api_client, trial_user_token):
        """Verify subscription includes trial_start, trial_end, trial_days_remaining"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/subscription", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # Trial info should be present (may be null if not on trial)
        assert "trial_start" in data, "Missing trial_start field"
        assert "trial_end" in data, "Missing trial_end field"
        assert "trial_days_remaining" in data, "Missing trial_days_remaining field"
        
        print(f"SUCCESS: Trial info present - Days remaining: {data.get('trial_days_remaining')}")


class TestCheckLimitEndpoint:
    """Tests for GET /api/subscription/check-limit"""
    
    def test_check_limit_requires_auth(self, api_client):
        """Verify check-limit requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/subscription/check-limit")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("SUCCESS: /api/subscription/check-limit requires authentication")
    
    def test_check_limit_returns_allowed_status(self, api_client, trial_user_token):
        """Verify check-limit returns allowed, current_count, limit, plan, message"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/subscription/check-limit", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        required_fields = ["allowed", "current_count", "limit", "plan"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["allowed"], bool), "allowed should be boolean"
        assert isinstance(data["current_count"], int), "current_count should be integer"
        assert isinstance(data["limit"], int), "limit should be integer"
        
        print(f"SUCCESS: Check limit - Allowed: {data['allowed']}, Count: {data['current_count']}/{data['limit']}")
    
    def test_check_limit_at_limit_returns_false(self, api_client, limit_user_token):
        """Verify check-limit returns allowed=false when at property limit"""
        headers = {"Authorization": f"Bearer {limit_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/subscription/check-limit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # User bugtest@staylet.com is on Solo plan with 2 properties (exceeds 1 limit)
        if data["current_count"] >= data["limit"]:
            assert data["allowed"] == False, "Should not be allowed when at/over limit"
            assert data["message"] is not None, "Should have upgrade message when at limit"
            print(f"SUCCESS: At limit - allowed=false, message: {data['message'][:50]}...")
        else:
            print(f"INFO: User not at limit ({data['current_count']}/{data['limit']}), skipping limit test")


class TestChangePlanEndpoint:
    """Tests for POST /api/subscription/change"""
    
    def test_change_plan_requires_auth(self, api_client):
        """Verify change plan requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/subscription/change", json={"plan": "portfolio"})
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("SUCCESS: /api/subscription/change requires authentication")
    
    def test_change_plan_invalid_plan_rejected(self, api_client, trial_user_token):
        """Verify invalid plan name is rejected"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        response = api_client.post(f"{BASE_URL}/api/subscription/change", 
                                   json={"plan": "invalid_plan"}, headers=headers)
        assert response.status_code == 400, f"Expected 400 for invalid plan, got {response.status_code}"
        print("SUCCESS: Invalid plan name rejected with 400")
    
    def test_upgrade_to_portfolio_works(self, api_client, trial_user_token):
        """Test upgrading to Portfolio plan"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        
        # First check current plan
        sub_response = api_client.get(f"{BASE_URL}/api/subscription", headers=headers)
        current_plan = sub_response.json().get("plan", "solo")
        
        # Upgrade to portfolio
        response = api_client.post(f"{BASE_URL}/api/subscription/change", 
                                   json={"plan": "portfolio"}, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["plan"] == "portfolio", f"Expected portfolio plan, got {data['plan']}"
        assert data["property_limit"] == 5, f"Expected 5 property limit, got {data['property_limit']}"
        assert data["status"] == "active", f"Expected active status after upgrade, got {data['status']}"
        
        print(f"SUCCESS: Upgraded from {current_plan} to portfolio (5 properties)")
    
    def test_downgrade_blocked_if_over_limit(self, api_client, limit_user_token):
        """Verify downgrade is blocked if property count exceeds new plan limit"""
        headers = {"Authorization": f"Bearer {limit_user_token}"}
        
        # Check current property count
        sub_response = api_client.get(f"{BASE_URL}/api/subscription", headers=headers)
        sub_data = sub_response.json()
        property_count = sub_data.get("property_count", 0)
        current_plan = sub_data.get("plan", "solo")
        
        # If user has more than 1 property and tries to downgrade to solo
        if property_count > 1 and current_plan != "solo":
            response = api_client.post(f"{BASE_URL}/api/subscription/change", 
                                       json={"plan": "solo"}, headers=headers)
            assert response.status_code == 400, f"Expected 400 when downgrading with too many properties, got {response.status_code}"
            assert "Cannot downgrade" in response.json().get("detail", ""), "Should mention cannot downgrade"
            print(f"SUCCESS: Downgrade blocked - {property_count} properties exceeds Solo limit of 1")
        else:
            print(f"INFO: User has {property_count} properties on {current_plan}, skipping downgrade block test")


class TestNewUserSignupTrial:
    """Tests for new user signup with trial status"""
    
    def test_signup_creates_trial_user(self, api_client):
        """Verify new signup starts with Solo plan on trial status"""
        import uuid
        test_email = f"test_trial_{uuid.uuid4().hex[:8]}@staylet.com"
        
        response = api_client.post(f"{BASE_URL}/api/auth/signup", json={
            "email": test_email,
            "password": "Test1234!",
            "full_name": "Test Trial User"
        })
        
        assert response.status_code == 200, f"Signup failed: {response.status_code} - {response.text}"
        
        data = response.json()
        user = data.get("user", {})
        
        # Verify trial status
        assert user.get("subscription_plan") == "solo", f"Expected solo plan, got {user.get('subscription_plan')}"
        assert user.get("subscription_status") == "trial", f"Expected trial status, got {user.get('subscription_status')}"
        assert user.get("trial_start") is not None, "trial_start should be set"
        assert user.get("trial_end") is not None, "trial_end should be set"
        assert user.get("property_limit") == 1, f"Expected property_limit 1, got {user.get('property_limit')}"
        
        # Verify trial_end is ~14 days from now
        if user.get("trial_end"):
            trial_end = datetime.fromisoformat(user["trial_end"].replace('Z', '+00:00'))
            days_until_end = (trial_end - datetime.now(trial_end.tzinfo)).days
            assert 13 <= days_until_end <= 14, f"Expected ~14 days trial, got {days_until_end} days"
        
        print(f"SUCCESS: New user created with Solo plan, trial status, 14-day trial")
        
        # Cleanup: We can't delete users via API, but the test data is isolated


class TestConstantsEndpoint:
    """Tests for subscription info in constants endpoint"""
    
    def test_constants_includes_subscription_plans(self, api_client):
        """Verify /api/constants includes subscription_plans and trial_days"""
        response = api_client.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        
        data = response.json()
        assert "subscription_plans" in data, "Missing subscription_plans in constants"
        assert "trial_days" in data, "Missing trial_days in constants"
        
        plans = data["subscription_plans"]
        assert "solo" in plans, "Solo plan missing from constants"
        assert "portfolio" in plans, "Portfolio plan missing from constants"
        assert "operator" in plans, "Operator plan missing from constants"
        
        assert data["trial_days"] == 14, f"Expected 14 trial days, got {data['trial_days']}"
        
        print("SUCCESS: Constants endpoint includes subscription_plans and trial_days")


class TestAuthMeSubscriptionInfo:
    """Tests for subscription info in /api/auth/me"""
    
    def test_auth_me_includes_subscription_fields(self, api_client, trial_user_token):
        """Verify /api/auth/me returns subscription fields"""
        headers = {"Authorization": f"Bearer {trial_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        subscription_fields = ["subscription_plan", "subscription_status", "property_limit", "property_count"]
        for field in subscription_fields:
            assert field in data, f"Missing {field} in /api/auth/me response"
        
        print(f"SUCCESS: /api/auth/me includes subscription info - Plan: {data['subscription_plan']}, Status: {data['subscription_status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
