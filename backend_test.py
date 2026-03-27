import requests
import sys
from datetime import datetime
import json

class StayletAPITester:
    def __init__(self, base_url="https://foundations.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_msg)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health", 200)

    def test_auth_signup(self):
        """Test user signup"""
        print("\n=== AUTHENTICATION TESTS ===")
        
        # Generate unique test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            200,
            data=test_user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_auth_login(self):
        """Test user login with existing credentials"""
        if not self.user_id:
            print("⚠️  Skipping login test - no user created")
            return False
            
        # Try to login with the same credentials used in signup
        timestamp = datetime.now().strftime('%H%M%S')
        login_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            print(f"   New token obtained: {self.token[:20]}...")
            return True
        return False

    def test_auth_me(self):
        """Test getting current user info"""
        if not self.token:
            print("⚠️  Skipping auth/me test - no token available")
            return False
            
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        return success

    def test_password_reset(self):
        """Test password reset (mocked)"""
        reset_data = {
            "email": "test@example.com"
        }
        
        success, response = self.run_test(
            "Password Reset Request",
            "POST",
            "auth/reset-password",
            200,
            data=reset_data
        )
        
        return success

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        print("\n=== DASHBOARD TESTS ===")
        
        if not self.token:
            print("⚠️  Skipping dashboard tests - no token available")
            return False
            
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            expected_fields = ['total_properties', 'upcoming_expiries', 'overdue_items', 'missing_documents', 'tasks_due']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                self.log_test("Dashboard Stats Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Dashboard Stats Structure", True)
        
        return success

    def test_properties_endpoints(self):
        """Test properties CRUD operations"""
        print("\n=== PROPERTIES TESTS ===")
        
        if not self.token:
            print("⚠️  Skipping properties tests - no token available")
            return False
        
        # Test get properties (should be empty initially)
        success, response = self.run_test(
            "Get Properties (Empty)",
            "GET",
            "properties",
            200
        )
        
        # Test create property
        property_data = {
            "name": "Test Property",
            "address": "123 Test Street, London",
            "postcode": "SW1A 1AA",
            "property_type": "apartment",
            "bedrooms": 2
        }
        
        success, response = self.run_test(
            "Create Property",
            "POST",
            "properties",
            200,
            data=property_data
        )
        
        if success:
            # Test get properties again (should have one property)
            self.run_test(
                "Get Properties (With Data)",
                "GET",
                "properties",
                200
            )
        
        return success

    def test_tasks_endpoints(self):
        """Test tasks CRUD operations"""
        print("\n=== TASKS TESTS ===")
        
        if not self.token:
            print("⚠️  Skipping tasks tests - no token available")
            return False
        
        # Test get tasks (should be empty initially)
        self.run_test(
            "Get Tasks (Empty)",
            "GET",
            "tasks",
            200
        )
        
        # Test create task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
            "category": "compliance"
        }
        
        success, response = self.run_test(
            "Create Task",
            "POST",
            "tasks",
            200,
            data=task_data
        )
        
        if success:
            # Test get tasks again (should have one task)
            self.run_test(
                "Get Tasks (With Data)",
                "GET",
                "tasks",
                200
            )
        
        return success

    def test_notifications_endpoint(self):
        """Test notifications endpoint"""
        print("\n=== NOTIFICATIONS TESTS ===")
        
        if not self.token:
            print("⚠️  Skipping notifications tests - no token available")
            return False
        
        success, response = self.run_test(
            "Get Notifications",
            "GET",
            "notifications",
            200
        )
        
        return success

    def test_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        print("\n=== AUTHORIZATION TESTS ===")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        # Test protected endpoints without token
        self.run_test(
            "Dashboard Stats (Unauthorized)",
            "GET",
            "dashboard/stats",
            401
        )
        
        self.run_test(
            "Get Properties (Unauthorized)",
            "GET",
            "properties",
            401
        )
        
        # Restore token
        self.token = original_token

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Staylet API Tests")
        print(f"Base URL: {self.base_url}")
        print("=" * 50)
        
        # Health checks first
        self.test_health_check()
        
        # Authentication flow
        if self.test_auth_signup():
            self.test_auth_me()
            self.test_password_reset()
            
            # Protected endpoints
            self.test_dashboard_stats()
            self.test_properties_endpoints()
            self.test_tasks_endpoints()
            self.test_notifications_endpoint()
            
            # Authorization tests
            self.test_unauthorized_access()
        else:
            print("❌ Signup failed - skipping authenticated tests")
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = StayletAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'tests_run': tester.tests_run,
                'tests_passed': tester.tests_passed,
                'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0
            },
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())