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
    async def test_create_ai_participant(self, client, session_with_participants):
        """Test creating an AI participant"""
        session_id = session_with_participants["session"]["id"]
        
        response = client.post(
            "/api/participants/",
            json={
                "session_id": session_id,
                "name": "AI Helper",
                "type": "AI",
                "ai_model": "gpt-4",
                "ai_config": {
                    "persona": "Helpful assistant",
                    "knowledge": {"domain": "general"},
                    "strategy": "Be supportive"
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "AI Helper"
        assert data["type"] == "AI"
        assert data["ai_model"] == "gpt-4"
        assert data["ai_config"]["persona"] == "Helpful assistant"
        assert data["has_consented"] is True  # AI always consents
    
    @pytest.mark.asyncio
    async def test_bulk_create_ai_participants(self, client, session_with_participants):
        """Test creating multiple AI participants at once"""
        session_id = session_with_participants["session"]["id"]
        
        ai_configs = [
            {
                "name": "Agent One",
                "model": "gpt-4",
                "persona": "Technical expert",
                "knowledge": {"domain": "programming"},
                "strategy": "Provide detailed explanations"
            },
            {
                "name": "Agent Two",
                "model": "claude-3",
                "persona": "Creative thinker",
                "knowledge": {"domain": "design"},
                "strategy": "Encourage exploration"
            }
        ]
        
        response = client.post(
            "/api/participants/ai/bulk",
            json={
                "session_id": session_id,
                "ai_configs": ai_configs
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["participants"]) == 2
        assert data["participants"][0]["name"] == "Agent One"
        assert data["participants"][1]["name"] == "Agent Two"
        assert data["count"] == 2
    
    @pytest.mark.asyncio
    async def test_get_participant(self, client, session_with_participants):
        """Test retrieving a participant"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.get(f"/api/participants/{participant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == participant_id
        assert data["name"] == "Test Human"
        assert data["type"] == "human"
        assert data["has_consented"] is True
    
    @pytest.mark.asyncio
    async def test_list_participants(self, client, session_with_participants):
        """Test listing participants with filters"""
        session_id = session_with_participants["session"]["id"]
        
        # List all participants in session
        response = client.get(
            "/api/participants/",
            params={"session_id": session_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 2  # At least human + AI
        
        # Filter by type
        response = client.get(
            "/api/participants/",
            params={"session_id": session_id, "type": "human"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(p["type"] == "human" for p in data["items"])
        
        # Filter by consent status
        response = client.get(
            "/api/participants/",
            params={"session_id": session_id, "has_consented": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(p["has_consented"] for p in data["items"])
    
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
    async def test_withdraw_consent(self, client, session_with_participants):
        """Test withdrawing consent"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.post(
            f"/api/participants/{participant_id}/consent",
            json={
                "consent_given": False,
                "withdrawal_reason": "Changed my mind"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_consented"] is False
        assert data["consent_withdrawn_at"] is not None
    
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
    
    @pytest.mark.asyncio
    async def test_partial_data_withdrawal(self, client, session_with_participants):
        """Test partial data withdrawal"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.post(
            f"/api/participants/{participant_id}/withdraw",
            json={
                "withdrawal_type": "partial",
                "reason": "Only want to remove messages",
                "delete_messages": True,
                "delete_metadata": False,
                "confirmation": "I understand this action cannot be undone"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["withdrawal_type"] == "partial"
        assert data["items_affected"]["metadata_removed"] is False
    
    @pytest.mark.asyncio
    async def test_update_participant_avatar(self, client, session_with_participants):
        """Test updating participant avatar"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.put(
            f"/api/participants/{participant_id}",
            json={"avatar": "https://example.com/avatar.png"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["avatar"] == "https://example.com/avatar.png"
    
    @pytest.mark.asyncio
    async def test_participant_leave_session(self, client, session_with_participants):
        """Test participant leaving session"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.post(f"/api/participants/{participant_id}/leave")
        
        assert response.status_code == 200
        data = response.json()
        assert data["left_at"] is not None
        assert data["message"] == "Successfully left the session"
    
    @pytest.mark.asyncio
    async def test_get_participant_messages(self, client, session_with_participants):
        """Test retrieving participant's messages"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.get(f"/api/participants/{participant_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_create_participant_duplicate_email(self, client, session_with_participants):
        """Test creating participants with duplicate emails in same session"""
        session_id = session_with_participants["session"]["id"]
        email = "duplicate@example.com"
        
        # First participant
        client.post(
            "/api/participants/",
            json={
                "session_id": session_id,
                "name": "User 1",
                "type": "human",
                "email": email
            }
        )
        
        # Second participant with same email should fail
        response = client.post(
            "/api/participants/",
            json={
                "session_id": session_id,
                "name": "User 2",
                "type": "human",
                "email": email
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_ai_participant_cannot_withdraw_consent(self, client, session_with_participants):
        """Test that AI participants cannot withdraw consent"""
        ai_participant_id = session_with_participants["ai_participants"][0]["id"]
        
        response = client.post(
            f"/api/participants/{ai_participant_id}/consent",
            json={"consent_given": False}
        )
        
        assert response.status_code == 400
        assert "cannot withdraw consent" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_participant_statistics(self, client, session_with_participants):
        """Test getting participant statistics"""
        participant_id = session_with_participants["human_participant"]["id"]
        
        response = client.get(f"/api/participants/{participant_id}/statistics")
        
        assert response.status_code == 200
        stats = response.json()
        assert stats["participant_id"] == participant_id
        assert "message_count" in stats
        assert "session_duration_seconds" in stats
        assert "joined_at" in stats