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