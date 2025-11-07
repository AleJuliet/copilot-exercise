"""
Test suite for edge cases and performance
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join our competitive soccer team and represent the school",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Art Club": {
            "description": "Express creativity through painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu", "david@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_activity_name_with_special_characters(self, client, reset_activities):
        """Test activity names that need URL encoding"""
        # Test with spaces (already exists as "Art Club")
        response = client.post("/activities/Art%20Club/signup", params={"email": "test@mergington.edu"})
        assert response.status_code == 200
        
        # Test unregister with same encoding
        response = client.delete("/activities/Art%20Club/unregister", params={"email": "test@mergington.edu"})
        assert response.status_code == 200
    
    def test_email_with_plus_sign(self, client, reset_activities):
        """Test email addresses with + signs (common Gmail feature)"""
        email = "student+activities@mergington.edu"
        
        response = client.post("/activities/Soccer Team/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify it was added correctly
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Soccer Team"]["participants"]
    
    def test_empty_email_parameter(self, client, reset_activities):
        """Test behavior with empty email parameter"""
        response = client.post("/activities/Soccer Team/signup", params={"email": ""})
        # Should fail because empty email is not valid
        assert response.status_code == 422
    
    def test_missing_email_parameter(self, client, reset_activities):
        """Test behavior with missing email parameter"""
        response = client.post("/activities/Soccer Team/signup")
        assert response.status_code == 422  # Unprocessable Entity - missing required parameter
    
    def test_very_long_email(self, client, reset_activities):
        """Test with very long email address"""
        long_email = "a" * 100 + "@mergington.edu"
        
        response = client.post("/activities/Soccer Team/signup", params={"email": long_email})
        assert response.status_code == 200
        
        # Verify it was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert long_email in activities_data["Soccer Team"]["participants"]
    
    def test_case_sensitive_activity_names(self, client, reset_activities):
        """Test that activity names are case sensitive"""
        response = client.post("/activities/soccer team/signup", params={"email": "test@mergington.edu"})
        assert response.status_code == 404  # Should not find "soccer team" (lowercase)
    
    def test_unicode_in_email(self, client, reset_activities):
        """Test email with unicode characters"""
        unicode_email = "tëst@mergington.edu"
        
        response = client.post("/activities/Soccer Team/signup", params={"email": unicode_email})
        assert response.status_code == 200
        
        # Test unregister works too
        response = client.delete("/activities/Soccer Team/unregister", params={"email": unicode_email})
        assert response.status_code == 200


class TestConcurrency:
    """Test concurrent operations (simulated)"""
    
    def test_multiple_rapid_signups(self, client, reset_activities):
        """Test multiple signups in rapid succession"""
        base_email = "concurrent{0}@mergington.edu"
        activity = "Basketball Club"
        
        # Simulate concurrent signups
        for i in range(10):
            email = base_email.format(i)
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for i in range(10):
            email = base_email.format(i)
            assert email in activities_data[activity]["participants"]
    
    def test_signup_unregister_same_email(self, client, reset_activities):
        """Test signing up and immediately unregistering the same email"""
        email = "flipflop@mergington.edu"
        activity = "Art Club"
        
        # Rapid signup/unregister cycle
        for _ in range(3):
            # Signup
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
            
            # Unregister
            response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
            assert response.status_code == 200
        
        # Final state should be unregistered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestDataIntegrity:
    """Test data integrity and state management"""
    
    def test_participant_count_consistency(self, client, reset_activities):
        """Test that participant counts remain consistent after operations"""
        activity = "Soccer Team"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Add participant
        client.post(f"/activities/{activity}/signup", params={"email": "newplayer@mergington.edu"})
        
        # Check count increased
        after_signup_response = client.get("/activities")
        after_signup_count = len(after_signup_response.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Remove participant
        client.delete(f"/activities/{activity}/unregister", params={"email": "newplayer@mergington.edu"})
        
        # Check count returned to original
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        assert final_count == initial_count
    
    def test_no_duplicate_participants(self, client, reset_activities):
        """Test that a participant cannot be added twice"""
        email = "duplicate@mergington.edu"
        activity = "Basketball Club"
        
        # First signup should work
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response2.status_code == 400
        
        # Verify only one instance exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participant_count = activities_data[activity]["participants"].count(email)
        assert participant_count == 1
    
    def test_cross_activity_independence(self, client, reset_activities):
        """Test that operations on one activity don't affect others"""
        email = "crosstest@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_test = ["Soccer Team", "Basketball Club", "Art Club"]
        
        for activity in activities_to_test:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Unregister from one activity
        response = client.delete("/activities/Soccer Team/unregister", params={"email": email})
        assert response.status_code == 200
        
        # Verify the participant is still in other activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert email not in activities_data["Soccer Team"]["participants"]
        assert email in activities_data["Basketball Club"]["participants"]
        assert email in activities_data["Art Club"]["participants"]