"""
Tests for WebSocket functionality
"""
import pytest
import json
from fastapi.testclient import TestClient
from uuid import uuid4


class TestWebSocket:
    """Test cases for WebSocket endpoints"""
    
    @pytest.fixture
    async def active_session(self, client, experiment_with_conditions):
        """Create an active session with participants"""
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
                "participant_name": "Test User",
                "consent_given": True
            }
        )
        
        return {
            "session_id": session_data["id"],
            "participant_id": join_response.json()["participant"]["id"],
            "ai_participants": join_response.json()["ai_participants"]
        }
    
    def test_websocket_connect_success(self, client, active_session):
        """Test successful WebSocket connection"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            # Should receive session info on connect
            data = websocket.receive_json()
            assert data["type"] == "session_info"
            assert data["session_id"] == session_id
            assert "participants" in data
            assert "message_history" in data
            assert data["status"] == "active"
    
    def test_websocket_send_chat_message(self, client, active_session):
        """Test sending chat message through WebSocket"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            # Skip session info message
            websocket.receive_json()
            
            # Send chat message
            websocket.send_json({
                "type": "chat",
                "content": "Hello, this is a test message!"
            })
            
            # Should receive broadcast of own message
            data = websocket.receive_json()
            assert data["type"] == "chat"
            assert data["content"] == "Hello, this is a test message!"
            assert data["participant_id"] == participant_id
            assert "timestamp" in data
            assert "sequence_number" in data