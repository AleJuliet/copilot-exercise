"""
Test suite for the Mergington High School Activities API
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
        },
        "Drama Society": {
            "description": "Participate in theatrical productions and improve acting skills",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["anna@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking through structured debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["robert@mergington.edu", "maria@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in scientific challenges and experiments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 24,
            "participants": ["kevin@mergington.edu", "jennifer@mergington.edu", "thomas@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        
        # Check structure of one activity
        soccer = data["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)
    
    def test_activities_have_correct_structure(self, client, reset_activities):
        """Test that all activities have the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Soccer Team"
        
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test signup fails when student is already registered"""
        email = "alex@mergington.edu"  # Already in Soccer Team
        activity = "Soccer Team"
        
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup fails for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_url_encoded_activity_name(self, client, reset_activities):
        """Test signup works with URL-encoded activity names"""
        email = "student@mergington.edu"
        activity = "Art Club"
        encoded_activity = "Art%20Club"
        
        response = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "alex@mergington.edu"  # Existing participant in Soccer Team
        activity = "Soccer Team"
        
        # Verify participant is initially there
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister fails when student is not registered"""
        email = "notregistered@mergington.edu"
        activity = "Soccer Team"
        
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister fails for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_url_encoded_activity_name(self, client, reset_activities):
        """Test unregister works with URL-encoded activity names"""
        email = "lucy@mergington.edu"  # Existing participant in Art Club
        activity = "Art Club"
        encoded_activity = "Art%20Club"
        
        response = client.delete(f"/activities/{encoded_activity}/unregister", params={"email": email})
        assert response.status_code == 200
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestSignupUnregisterIntegration:
    """Test signup and unregister working together"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test complete flow of signing up and then unregistering"""
        email = "testflow@mergington.edu"
        activity = "Drama Society"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_signup_after_unregister(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        email = "sarah@mergington.edu"  # Existing participant in Soccer Team
        activity = "Soccer Team"
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert unregister_response.status_code == 200
        
        # Sign up again
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200
        
        # Verify re-signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]


class TestEmailValidation:
    """Test email parameter handling"""
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with email containing special characters"""
        email = "test+user@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_unregister_with_special_characters_in_email(self, client, reset_activities):
        """Test unregister with email containing special characters"""
        email = "test+user@mergington.edu"
        activity = "Chess Club"
        
        # First signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Then unregister
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestDataPersistence:
    """Test that data changes persist across requests"""
    
    def test_multiple_signups_persist(self, client, reset_activities):
        """Test that multiple signups are all preserved"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        activity = "Programming Class"
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify all are present
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for email in emails:
            assert email in activities_data[activity]["participants"]
    
    def test_mixed_operations_persist(self, client, reset_activities):
        """Test that mixed signup/unregister operations work correctly"""
        activity = "Science Olympiad"
        
        # Get initial participants
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = set(initial_data[activity]["participants"])
        
        # Add new participant
        new_email = "newscience@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": new_email})
        
        # Remove existing participant
        existing_email = "kevin@mergington.edu"
        client.delete(f"/activities/{activity}/unregister", params={"email": existing_email})
        
        # Verify final state
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_participants = set(final_data[activity]["participants"])
        
        expected_participants = (initial_participants - {existing_email}) | {new_email}
        assert final_participants == expected_participants