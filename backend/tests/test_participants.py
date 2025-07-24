"""
Tests for Participant API endpoints
"""
import pytest
from uuid import uuid4
from datetime import datetime


class TestParticipantAPI:
    """Test cases for participant endpoints"""
    
    @pytest.fixture
    async def session_with_participants(self, client, experiment_with_conditions):
        """Create a session with participants for testing"""
        experiment_id = experiment_with_conditions["id"]
        conditions_response = client.get(f"/api/experiments/{experiment_id}/conditions")
        condition_id = conditions_response.json()[0]["id"]
        
        # Create session
        create_response = client.post(
            "/api/sessions/",
            json={"condition_id": condition_id}
        )
        session_data = create_response.json()
        
        # Join with human participant
        join_response = client.post(
            "/api/sessions/join",
            json={
                "access_code": session_data["access_code"],
                "participant_name": "Test Human",
                "consent_given": True
            }
        )
        
        return {
            "session": session_data,
            "human_participant": join_response.json()["participant"],
            "ai_participants": join_response.json()["ai_participants"]
        }
    
    @pytest.mark.asyncio
    async def test_create_participant(self, client, session_with_participants):
        """Test creating a new participant"""
        session_id = session_with_participants["session"]["id"]
        
        response = client.post(
            "/api/participants/",
            json={
                "session_id": session_id,
                "name": "New Participant",
                "type": "human",
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Participant"
        assert data["type"] == "human"
        assert data["email"] == "test@example.com"
        assert data["session_id"] == session_id
        assert data["has_consented"] is False
        assert "id" in data
        assert "joined_at" in data
    
    @pytest.mark.asyncio
    async def test_update_participant_consent(self, client, session_with_participants):
        """Test updating participant consent"""
        # Create participant without consent
        session_id = session_with_participants["session"]["id"]
        create_response = client.post(
            "/api/participants/",
            json={
                "session_id": session_id,
                "name": "No Consent User",
                "type": "human"
            }
        )
        participant_id = create_response.json()["id"]
        
        # Give consent
        response = client.post(
            f"/api/participants/{participant_id}/consent",
            json={
                "consent_given": True,
                "consent_details": {
                    "data_collection": True,
                    "data_sharing": True,
                    "recording": False
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_consented"] is True
        assert data["consent_given_at"] is not None
        assert "consent_withdrawn_at" not in data or data["consent_withdrawn_at"] is None
    
    @pytest.mark.asyncio
    async def test_withdraw_participant_data(self, client, session_with_participants):
        """Test data withdrawal request"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.post(
            f"/api/participants/{participant_id}/withdraw",
            json={
                "withdrawal_type": "full",
                "reason": "Privacy concerns",
                "delete_messages": True,
                "delete_metadata": True,
                "confirmation": "I understand this action cannot be undone"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["withdrawal_type"] == "full"
        assert data["items_affected"]["messages_deleted"] >= 0
        assert data["items_affected"]["metadata_removed"] is True
        assert "timestamp" in data