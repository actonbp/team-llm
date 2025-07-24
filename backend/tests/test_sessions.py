"""
Tests for Session API endpoints
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta


class TestSessionAPI:
    """Test cases for session endpoints"""
    
    @pytest.fixture
    async def experiment_with_conditions(self, client, sample_experiment_yaml):
        """Create an experiment with conditions for testing"""
        response = client.post(
            "/api/experiments/import",
            json={"yaml_content": sample_experiment_yaml}
        )
        return response.json()
    
    @pytest.mark.asyncio
    async def test_create_session(self, client, experiment_with_conditions):
        """Test creating a new session"""
        experiment_id = experiment_with_conditions["id"]
        
        # Get conditions first
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        # Create session
        response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["condition_id"] == condition_id
        assert data["status"] == "waiting"
        assert len(data["access_code"]) == 6
        assert data["access_code"].isupper()
        assert data["max_participants"] == 10
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_join_session_with_access_code(self, client, experiment_with_conditions):
        """Test joining a session using access code"""
        # Create session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_data = create_response.json()
        access_code = session_data["access_code"]
        
        # Join session
        response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_data["id"]
        assert data["participant"]["name"] == "Test User"
        assert data["participant"]["type"] == "human"
        assert data["participant"]["has_consented"] is True
        assert data["status"] == "active"  # Should be active after first human joins
        assert len(data["ai_participants"]) == 1  # AI should be initialized
        assert data["ai_participants"][0]["name"] == "AI Assistant"
    
    @pytest.mark.asyncio
    async def test_join_session_invalid_code(self, client):
        """Test joining with invalid access code"""
        response = client.post(
            "/api/sessions/join",
            json={
                "access_code": "INVALID",
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_join_session_without_consent(self, client, experiment_with_conditions):
        """Test joining session without giving consent"""
        # Create session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        access_code = create_response.json()["access_code"]
        
        # Try to join without consent
        response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test User",
                "consent_given": False
            }
        )
        
        assert response.status_code == 400
        assert "consent required" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_join_full_session(self, client, experiment_with_conditions):
        """Test joining a session that's already full"""
        # Create session with max 1 participant
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id, "max_participants": 1}
        )
        access_code = create_response.json()["access_code"]
        
        # First participant joins successfully
        client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "User 1",
                "consent_given": True
            }
        )
        
        # Second participant should fail
        response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "User 2",
                "consent_given": True
            }
        )
        
        assert response.status_code == 400
        assert "session is full" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_leave_session(self, client, experiment_with_conditions):
        """Test leaving a session"""
        # Create and join session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_id = create_response.json()["id"]
        access_code = create_response.json()["access_code"]
        
        join_response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        participant_id = join_response.json()["participant"]["id"]
        
        # Leave session
        response = client.post(
            f"/api/sessions/{session_id}/leave",
            json={"participant_id": participant_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully left session"
        assert data["participant_id"] == participant_id
    
    @pytest.mark.asyncio
    async def test_complete_session(self, client, experiment_with_conditions):
        """Test completing a session"""
        # Create and join session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_id = create_response.json()["id"]
        access_code = create_response.json()["access_code"]
        
        join_response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        participant_id = join_response.json()["participant"]["id"]
        
        # Complete session
        response = client.post(
            f"/api/sessions/{session_id}/complete",
            json={"triggered_by": participant_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
        assert len(data["completion_code"]) == 8
    
    @pytest.mark.asyncio
    async def test_get_session(self, client, experiment_with_conditions):
        """Test retrieving session details"""
        # Create session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_id = create_response.json()["id"]
        
        # Get session
        response = client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["condition_id"] == condition_id
        assert "participants" in data
        assert "messages" in data
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, client, experiment_with_conditions):
        """Test listing sessions with filters"""
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        # Create multiple sessions
        for i in range(3):
            client.post("/api/sessions/", json={"condition_id": condition_id})
        
        # List all sessions
        response = client.get("/api/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3
        
        # Filter by experiment
        response = client.get("/api/sessions/", params={"experiment_id": experiment_id})
        assert response.status_code == 200
        data = response.json()
        assert all(s["experiment"]["id"] == experiment_id for s in data["items"])
        
        # Filter by status
        response = client.get("/api/sessions/", params={"status": "waiting"})
        assert response.status_code == 200
        data = response.json()
        assert all(s["status"] == "waiting" for s in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_session_statistics(self, client, experiment_with_conditions):
        """Test getting session statistics"""
        # Create and complete a session
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_id = create_response.json()["id"]
        access_code = create_response.json()["access_code"]
        
        # Join and complete
        join_response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        participant_id = join_response.json()["participant"]["id"]
        
        client.post(
            f"/api/sessions/{session_id}/complete",
            json={"triggered_by": participant_id}
        )
        
        # Get statistics
        response = client.get(f"/api/sessions/{session_id}/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["session_id"] == session_id
        assert stats["participant_count"] >= 2  # Human + AI
        assert stats["message_count"] == 0  # No messages sent yet
        assert stats["duration_seconds"] > 0
        assert stats["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_session_access_code_uniqueness(self, client, experiment_with_conditions):
        """Test that access codes are unique"""
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        # Create multiple sessions
        access_codes = set()
        for _ in range(10):
            response = client.post(
                "/api/sessions/",
                json={"condition_id": condition_id}
            )
            access_code = response.json()["access_code"]
            assert access_code not in access_codes
            access_codes.add(access_code)
    
    @pytest.mark.asyncio
    async def test_session_with_multiple_ai_agents(self, client):
        """Test session with multiple AI agents from YAML config"""
        yaml_with_multiple_ai = """
experimentName: "Multi-Agent Study"
description: "Study with multiple AI agents"
version: 1
roles:
  - name: "Human"
    type: "human"
    instructions: "Collaborate with the AI agents"
  - name: "Agent Alpha"
    type: "AI"
    model: "gpt-4"
    persona: "Technical expert"
  - name: "Agent Beta"
    type: "AI"
    model: "claude-3"
    persona: "Creative thinker"
scenario:
  type: "collaborative"
  duration: 600
conditions:
  - id: "multi-ai"
    name: "Multiple AI Agents"
    description: "Both AI agents active"
    variables:
      active_agents: ["Agent Alpha", "Agent Beta"]
"""
        
        # Import experiment
        import_response = client.post(
            "/api/experiments/import",
            json={"yaml_content": yaml_with_multiple_ai}
        )
        experiment_id = import_response.json()["id"]
        
        # Get condition
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        # Create session
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        access_code = create_response.json()["access_code"]
        
        # Join session
        join_response = client.post(
            "/api/sessions/join",
            json={
                "access_code": access_code,
                "participant_name": "Test Human",
                "consent_given": True
            }
        )
        
        assert response.status_code == 200
        data = join_response.json()
        assert len(data["ai_participants"]) == 2
        assert {p["name"] for p in data["ai_participants"]} == {"Agent Alpha", "Agent Beta"}