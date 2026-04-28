import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthCheck:
    def test_root_endpoint(self):
        """Test the root health check endpoint."""
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello"}


class TestAIRoutes:
    def test_create_new_session(self):
        """Test creating a new AI session."""
        response = client.post("/ai/new")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        return data["session_id"]

    def test_chat_without_session(self):
        """Test chat with non-existent session returns 404."""
        response = client.post(
            "/ai/chat/nonexistent-session",
            json={"message": "Hello"}
        )
        assert response.status_code == 404

    def test_close_session(self):
        """Test closing an AI session."""
        new_session = client.post("/ai/new")
        session_id = new_session.json()["session_id"]
        
        response = client.delete(f"/ai/close/{session_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Сессия закрыта"

    def test_close_nonexistent_session(self):
        """Test closing non-existent session returns 404."""
        response = client.delete("/ai/close/nonexistent-session")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
