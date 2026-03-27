"""
Staylet Phase 3 API Backend Tests
Tests for: Tasks CRUD with recurring, Notifications, User Preferences, Dashboard Data
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


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def test_property_id(auth_headers):
    """Get or create a test property for task tests"""
    response = requests.get(f"{BASE_URL}/api/properties", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        return response.json()[0]["id"]
    # Create a test property
    create_response = requests.post(f"{BASE_URL}/api/properties", 
        headers=auth_headers,
        json={
            "name": f"TEST_Phase3Property_{uuid.uuid4().hex[:8]}",
            "address": "Test Address",
            "postcode": "SW1A 1AA"
        })
    return create_response.json()["id"]


class TestTasksCRUD:
    """Tasks CRUD operations tests"""
    
    def test_get_tasks_list(self, auth_headers):
        """Get list of tasks"""
        response = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ Get tasks list test passed")
    
    def test_create_task_success(self, auth_headers, test_property_id):
        """Create a task with valid data"""
        unique_title = f"TEST_Task_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={
                "title": unique_title,
                "description": "Test task description",
                "priority": "high",
                "category": "maintenance",
                "property_id": test_property_id,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == unique_title
        assert data["task_status"] == "pending"
        assert data["priority"] == "high"
        assert data["category"] == "maintenance"
        assert "id" in data
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{data['id']}", headers=auth_headers)
        print("✓ Create task success test passed")
    
    def test_create_task_empty_title_rejected(self, auth_headers):
        """Backend should reject empty task title"""
        response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={
                "title": "",
                "priority": "medium"
            })
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()
        print("✓ Empty task title rejected")
    
    def test_create_task_whitespace_title_rejected(self, auth_headers):
        """Backend should reject whitespace-only task title"""
        response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={
                "title": "   ",
                "priority": "medium"
            })
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()
        print("✓ Whitespace task title rejected")
    
    def test_update_task(self, auth_headers):
        """Update a task"""
        # Create task
        unique_title = f"TEST_UpdateTask_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title, "priority": "low"})
        task_id = create_response.json()["id"]
        
        # Update
        updated_title = f"TEST_Updated_{uuid.uuid4().hex[:8]}"
        response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
            headers=auth_headers,
            json={"title": updated_title, "priority": "urgent"})
        assert response.status_code == 200
        assert response.json()["title"] == updated_title
        assert response.json()["priority"] == "urgent"
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers)
        task = next((t for t in get_response.json() if t["id"] == task_id), None)
        assert task is not None
        assert task["title"] == updated_title
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("✓ Update task test passed")
    
    def test_delete_task(self, auth_headers):
        """Delete a task"""
        # Create task
        unique_title = f"TEST_DeleteTask_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title})
        task_id = create_response.json()["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deleted
        get_response = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers)
        task = next((t for t in get_response.json() if t["id"] == task_id), None)
        assert task is None
        print("✓ Delete task test passed")
    
    def test_task_status_change(self, auth_headers):
        """Test task status change to completed"""
        # Create task
        unique_title = f"TEST_StatusTask_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title})
        task_id = create_response.json()["id"]
        
        # Change status to in_progress
        response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
            headers=auth_headers,
            json={"task_status": "in_progress"})
        assert response.status_code == 200
        assert response.json()["task_status"] == "in_progress"
        
        # Change status to completed
        response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
            headers=auth_headers,
            json={"task_status": "completed"})
        assert response.status_code == 200
        assert response.json()["task_status"] == "completed"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("✓ Task status change test passed")


class TestTasksFiltering:
    """Tasks filtering tests"""
    
    def test_filter_by_status(self, auth_headers):
        """Filter tasks by status"""
        # Create a pending task
        unique_title = f"TEST_FilterStatus_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title})
        task_id = create_response.json()["id"]
        
        # Filter by pending
        response = requests.get(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            params={"task_status": "pending"})
        assert response.status_code == 200
        tasks = response.json()
        assert all(t["task_status"] == "pending" for t in tasks)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("✓ Filter tasks by status test passed")
    
    def test_filter_by_priority(self, auth_headers):
        """Filter tasks by priority"""
        # Create a high priority task
        unique_title = f"TEST_FilterPriority_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title, "priority": "high"})
        task_id = create_response.json()["id"]
        
        # Filter by high priority
        response = requests.get(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            params={"priority": "high"})
        assert response.status_code == 200
        tasks = response.json()
        assert all(t["priority"] == "high" for t in tasks)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("✓ Filter tasks by priority test passed")
    
    def test_filter_by_property(self, auth_headers, test_property_id):
        """Filter tasks by property"""
        # Create a task with property
        unique_title = f"TEST_FilterProperty_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={"title": unique_title, "property_id": test_property_id})
        task_id = create_response.json()["id"]
        
        # Filter by property
        response = requests.get(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            params={"property_id": test_property_id})
        assert response.status_code == 200
        tasks = response.json()
        assert all(t["property_id"] == test_property_id for t in tasks)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=auth_headers)
        print("✓ Filter tasks by property test passed")


class TestRecurringTasks:
    """Recurring tasks tests"""
    
    def test_create_recurring_task(self, auth_headers):
        """Create a recurring task"""
        unique_title = f"TEST_RecurringTask_{uuid.uuid4().hex[:8]}"
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={
                "title": unique_title,
                "is_recurring": True,
                "recurrence_pattern": "monthly",
                "due_date": due_date
            })
        assert response.status_code == 200
        data = response.json()
        assert data["is_recurring"] == True
        assert data["recurrence_pattern"] == "monthly"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{data['id']}", headers=auth_headers)
        print("✓ Create recurring task test passed")
    
    def test_complete_recurring_task_creates_next(self, auth_headers):
        """Completing a recurring task should create the next occurrence"""
        unique_title = f"TEST_RecurringComplete_{uuid.uuid4().hex[:8]}"
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Create recurring task
        create_response = requests.post(f"{BASE_URL}/api/tasks", 
            headers=auth_headers,
            json={
                "title": unique_title,
                "is_recurring": True,
                "recurrence_pattern": "monthly",
                "due_date": due_date
            })
        task_id = create_response.json()["id"]
        
        # Get initial task count
        initial_tasks = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers).json()
        initial_count = len([t for t in initial_tasks if t["title"] == unique_title])
        
        # Complete the task
        response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
            headers=auth_headers,
            json={"task_status": "completed"})
        assert response.status_code == 200
        
        # Check if new task was created
        updated_tasks = requests.get(f"{BASE_URL}/api/tasks", headers=auth_headers).json()
        new_count = len([t for t in updated_tasks if t["title"] == unique_title])
        
        # Should have one more task with same title (the new occurrence)
        assert new_count == initial_count + 1, f"Expected {initial_count + 1} tasks, got {new_count}"
        
        # Cleanup - delete all tasks with this title
        for task in updated_tasks:
            if task["title"] == unique_title:
                requests.delete(f"{BASE_URL}/api/tasks/{task['id']}", headers=auth_headers)
        
        print("✓ Complete recurring task creates next occurrence test passed")


class TestTaskTemplates:
    """Task templates endpoint tests"""
    
    def test_get_task_templates(self, auth_headers):
        """Get task templates returns predefined templates"""
        response = requests.get(f"{BASE_URL}/api/tasks/templates", headers=auth_headers)
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) == 10, f"Expected 10 templates, got {len(templates)}"
        
        # Check template structure
        for template in templates:
            assert "title" in template
            assert "category" in template
            assert "priority" in template
        
        # Check some expected templates exist
        titles = [t["title"] for t in templates]
        assert "Smoke & CO Alarm Check" in titles
        assert "Gas Safety Certificate Booking" in titles
        print("✓ Get task templates test passed")


class TestNotifications:
    """Notifications endpoints tests"""
    
    def test_get_notifications(self, auth_headers):
        """Get notifications list"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ Get notifications test passed")
    
    def test_get_unread_notifications(self, auth_headers):
        """Get only unread notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications", 
            headers=auth_headers,
            params={"unread_only": True})
        assert response.status_code == 200
        notifications = response.json()
        # All returned should be unread
        assert all(not n["is_read"] for n in notifications)
        print("✓ Get unread notifications test passed")
    
    def test_generate_notifications(self, auth_headers):
        """Generate notifications endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications/generate", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "created" in data
        print("✓ Generate notifications test passed")
    
    def test_mark_notification_read(self, auth_headers):
        """Mark a notification as read"""
        # First get notifications
        notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        
        if len(notifications) == 0:
            # Generate some notifications first
            requests.get(f"{BASE_URL}/api/notifications/generate", headers=auth_headers)
            notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        
        if len(notifications) == 0:
            pytest.skip("No notifications available for testing")
        
        notification_id = notifications[0]["id"]
        
        # Mark as read
        response = requests.put(f"{BASE_URL}/api/notifications/{notification_id}/read", 
            headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's marked as read
        updated_notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        notification = next((n for n in updated_notifications if n["id"] == notification_id), None)
        assert notification is not None
        assert notification["is_read"] == True
        print("✓ Mark notification read test passed")
    
    def test_mark_all_notifications_read(self, auth_headers):
        """Mark all notifications as read"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify all are read
        notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        assert all(n["is_read"] for n in notifications)
        print("✓ Mark all notifications read test passed")
    
    def test_delete_notification(self, auth_headers):
        """Delete a notification"""
        # Generate notifications first
        requests.get(f"{BASE_URL}/api/notifications/generate", headers=auth_headers)
        notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        
        if len(notifications) == 0:
            pytest.skip("No notifications available for testing")
        
        notification_id = notifications[0]["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/notifications/{notification_id}", 
            headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deleted
        updated_notifications = requests.get(f"{BASE_URL}/api/notifications", headers=auth_headers).json()
        notification = next((n for n in updated_notifications if n["id"] == notification_id), None)
        assert notification is None
        print("✓ Delete notification test passed")


class TestUserPreferences:
    """User preferences endpoints tests"""
    
    def test_get_user_preferences(self, auth_headers):
        """Get user preferences"""
        response = requests.get(f"{BASE_URL}/api/user/preferences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "email_reminders" in data
        assert "inapp_reminders" in data
        assert "reminder_lead_days" in data
        assert isinstance(data["reminder_lead_days"], list)
        print("✓ Get user preferences test passed")
    
    def test_update_user_preferences(self, auth_headers):
        """Update user preferences"""
        # Update preferences
        response = requests.put(f"{BASE_URL}/api/user/preferences", 
            headers=auth_headers,
            json={
                "email_reminders": False,
                "inapp_reminders": True,
                "reminder_lead_days": [90, 30, 7]
            })
        assert response.status_code == 200
        data = response.json()
        assert data["email_reminders"] == False
        assert data["inapp_reminders"] == True
        assert 90 in data["reminder_lead_days"]
        assert 30 in data["reminder_lead_days"]
        assert 7 in data["reminder_lead_days"]
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/user/preferences", headers=auth_headers)
        prefs = get_response.json()
        assert prefs["email_reminders"] == False
        
        # Reset to defaults
        requests.put(f"{BASE_URL}/api/user/preferences", 
            headers=auth_headers,
            json={
                "email_reminders": True,
                "inapp_reminders": True,
                "reminder_lead_days": [90, 60, 30, 7]
            })
        print("✓ Update user preferences test passed")


class TestDashboardData:
    """Dashboard data endpoint tests"""
    
    def test_dashboard_stats_includes_new_fields(self, auth_headers):
        """Dashboard stats should include tasks_due, tasks_due_this_month, unread_notifications"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check new Phase 3 fields
        assert "tasks_due" in data
        assert "tasks_due_this_month" in data
        assert "unread_notifications" in data
        
        # Check types
        assert isinstance(data["tasks_due"], int)
        assert isinstance(data["tasks_due_this_month"], int)
        assert isinstance(data["unread_notifications"], int)
        print("✓ Dashboard stats includes new fields test passed")
    
    def test_dashboard_data_endpoint(self, auth_headers):
        """Dashboard data endpoint returns comprehensive data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "stats" in data
        assert "upcoming_expiries" in data
        assert "overdue_records" in data
        assert "tasks_due_this_month" in data
        
        # Check types
        assert isinstance(data["upcoming_expiries"], list)
        assert isinstance(data["overdue_records"], list)
        assert isinstance(data["tasks_due_this_month"], list)
        
        # Check stats structure
        stats = data["stats"]
        assert "total_properties" in stats
        assert "upcoming_expiries" in stats
        assert "overdue_items" in stats
        assert "tasks_due" in stats
        print("✓ Dashboard data endpoint test passed")
    
    def test_dashboard_upcoming_expiries_structure(self, auth_headers):
        """Upcoming expiries should have correct structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=auth_headers)
        data = response.json()
        
        for expiry in data["upcoming_expiries"]:
            assert "id" in expiry
            assert "title" in expiry
            assert "category" in expiry
            assert "property_id" in expiry
            assert "property_name" in expiry
            assert "expiry_date" in expiry
            assert "days_until_expiry" in expiry
            assert "compliance_status" in expiry
        print("✓ Dashboard upcoming expiries structure test passed")
    
    def test_dashboard_tasks_due_structure(self, auth_headers):
        """Tasks due this month should have correct structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=auth_headers)
        data = response.json()
        
        for task in data["tasks_due_this_month"]:
            assert "id" in task
            assert "title" in task
            assert "priority" in task
            assert "task_status" in task
        print("✓ Dashboard tasks due structure test passed")


class TestConstantsPhase3:
    """Constants endpoint should include Phase 3 additions"""
    
    def test_constants_include_task_fields(self):
        """Constants should include task-related fields"""
        response = requests.get(f"{BASE_URL}/api/constants")
        assert response.status_code == 200
        data = response.json()
        
        assert "task_statuses" in data
        assert "task_priorities" in data
        assert "task_categories" in data
        assert "notification_types" in data
        assert "reminder_intervals" in data
        
        # Check values
        assert "pending" in data["task_statuses"]
        assert "completed" in data["task_statuses"]
        assert "urgent" in data["task_priorities"]
        assert "expiry_reminder" in data["notification_types"]
        print("✓ Constants include task fields test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
