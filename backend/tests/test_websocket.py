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
    
    def test_websocket_connect_invalid_session(self, client):
        """Test WebSocket connection with invalid session"""
        fake_session_id = str(uuid4())
        fake_participant_id = str(uuid4())
        
        with pytest.raises(Exception):  # WebSocket should close
            with client.websocket_connect(
                f"/ws/session/{fake_session_id}?participant_id={fake_participant_id}"
            ):
                pass
    
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
            
            # Should receive AI response (if configured)
            # This depends on AI being properly configured
    
    def test_websocket_typing_indicator(self, client, active_session):
        """Test typing indicator through WebSocket"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        # Connect with two clients
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket1:
            # Skip session info
            websocket1.receive_json()
            
            # Create second participant
            create_response = client.post(
                "/api/participants/",
                json={
                    "session_id": session_id,
                    "name": "Second User",
                    "type": "human"
                }
            )
            participant2_id = create_response.json()["id"]
            
            with client.websocket_connect(
                f"/ws/session/{session_id}?participant_id={participant2_id}"
            ) as websocket2:
                # Skip session info and participant joined messages
                websocket2.receive_json()
                websocket1.receive_json()  # participant_joined message
                
                # Send typing indicator from websocket2
                websocket2.send_json({
                    "type": "typing",
                    "is_typing": True
                })
                
                # websocket1 should receive typing indicator
                data = websocket1.receive_json()
                assert data["type"] == "typing"
                assert data["participant_id"] == participant2_id
                assert data["is_typing"] is True
    
    def test_websocket_participant_join_notification(self, client, active_session):
        """Test participant join notifications"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            # Skip session info
            websocket.receive_json()
            
            # Create new participant
            create_response = client.post(
                "/api/participants/",
                json={
                    "session_id": session_id,
                    "name": "New User",
                    "type": "human"
                }
            )
            new_participant_id = create_response.json()["id"]
            
            # Connect new participant
            with client.websocket_connect(
                f"/ws/session/{session_id}?participant_id={new_participant_id}"
            ):
                # Original websocket should receive join notification
                data = websocket.receive_json()
                assert data["type"] == "participant_joined"
                assert data["participant_id"] == new_participant_id
                assert data["participant_name"] == "New User"
    
    def test_websocket_session_completion(self, client, active_session):
        """Test session completion notification"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            # Skip session info
            websocket.receive_json()
            
            # Send task complete signal
            websocket.send_json({
                "type": "task_complete"
            })
            
            # Should receive session completed notification
            # Note: This might take a moment due to processing
            data = websocket.receive_json()
            assert data["type"] == "session_completed"
            assert "completion_code" in data
            assert data["triggered_by"]["participant_id"] == participant_id
    
    def test_websocket_message_history(self, client, active_session):
        """Test that message history is sent on connect"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        # Send some messages first
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            websocket.receive_json()  # Skip session info
            
            # Send a few messages
            for i in range(3):
                websocket.send_json({
                    "type": "chat",
                    "content": f"Message {i+1}"
                })
                websocket.receive_json()  # Skip broadcast
        
        # Connect again and check history
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            data = websocket.receive_json()
            assert data["type"] == "session_info"
            assert len(data["message_history"]) >= 3
            assert data["message_history"][0]["content"] == "Message 1"
    
    def test_websocket_health_check(self, client, active_session):
        """Test WebSocket health check mechanism"""
        session_id = active_session["session_id"]
        participant_id = active_session["participant_id"]
        
        with client.websocket_connect(
            f"/ws/session/{session_id}?participant_id={participant_id}"
        ) as websocket:
            websocket.receive_json()  # Skip session info
            
            # Wait for potential ping message (this is implementation dependent)
            # In a real test, we'd wait longer and check for ping messages
            # For now, just verify connection stays alive
            websocket.send_json({
                "type": "chat",
                "content": "Still connected"
            })
            
            data = websocket.receive_json()
            assert data["type"] == "chat"
            assert data["content"] == "Still connected"