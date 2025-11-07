"""
Test suite for static file serving
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestStaticFiles:
    """Test static file serving"""
    
    def test_static_index_html_accessible(self, client):
        """Test that the main HTML file is accessible"""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # Check for key content
        content = response.text
        assert "Mergington High School" in content
        assert "Extracurricular Activities" in content
        assert "Sign Up for an Activity" in content
    
    def test_static_css_accessible(self, client):
        """Test that CSS file is accessible"""
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        
        # Check for key CSS classes
        content = response.text
        assert "activity-card" in content
        assert "participants-list" in content
        assert "delete-icon" in content
    
    def test_static_js_accessible(self, client):
        """Test that JavaScript file is accessible"""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "") or "text/plain" in response.headers.get("content-type", "")
        
        # Check for key functions
        content = response.text
        assert "fetchActivities" in content
        assert "unregisterParticipant" in content
        assert "signup-form" in content
    
    def test_static_nonexistent_file(self, client):
        """Test that non-existent static files return 404"""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        
        # Should end up at the HTML page
        content = response.text
        assert "Mergington High School" in content