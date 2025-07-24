#!/usr/bin/env python3
"""
Test script for running a multi-agent experiment with AI participants.
This demonstrates the basic functionality of the platform.
"""

import asyncio
import json
import time
from datetime import datetime
import requests
import websockets
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
WS_BASE_URL = "ws://localhost:8000/ws"

# Test experiment configuration
TEST_EXPERIMENT = {
    "name": f"AI Agent Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "description": "Testing multi-agent conversation with AI participants",
    "config": {
        "duration_minutes": 10,
        "min_participants": 2,
        "max_participants": 4,
        "ai_participants": [
            {
                "name": "Creative Assistant",
                "role": "A creative and imaginative AI that loves brainstorming",
                "personality": "enthusiastic, creative, supportive",
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            },
            {
                "name": "Analytical Thinker",
                "role": "A logical AI that focuses on facts and analysis",
                "personality": "logical, precise, methodical",
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            },
            {
                "name": "Devil's Advocate",
                "role": "An AI that challenges ideas constructively",
                "personality": "skeptical, questioning, constructive",
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
        ],
        "initial_prompt": "Let's discuss: What would be the most impactful invention for the next decade?",
        "moderation": {
            "enabled": True,
            "rules": ["Keep discussion respectful", "Stay on topic"]
        }
    }
}


class ExperimentRunner:
    def __init__(self):
        self.experiment_id = None
        self.session_id = None
        self.access_code = None
        
    def create_experiment(self) -> Dict[str, Any]:
        """Create a new experiment."""
        print("Creating experiment...")
        response = requests.post(
            f"{API_BASE_URL}/experiments",
            json=TEST_EXPERIMENT
        )
        response.raise_for_status()
        experiment = response.json()
        self.experiment_id = experiment["id"]
        print(f"✓ Created experiment: {experiment['name']} (ID: {self.experiment_id})")
        return experiment
    
    def start_session(self) -> Dict[str, Any]:
        """Start a new session for the experiment."""
        print("\nStarting session...")
        response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={
                "experiment_id": self.experiment_id,
                "planned_duration_minutes": 10
            }
        )
        response.raise_for_status()
        session = response.json()
        self.session_id = session["id"]
        self.access_code = session["access_code"]
        print(f"✓ Started session: {self.access_code} (ID: {self.session_id})")
        return session
    
    async def join_ai_participant(self, ai_config: Dict[str, Any], participant_num: int):
        """Join an AI participant to the session."""
        participant_name = ai_config["name"]
        print(f"\nJoining AI participant {participant_num}: {participant_name}")
        
        # First, join via API to get participant ID
        response = requests.post(
            f"{API_BASE_URL}/participants",
            json={
                "session_id": self.session_id,
                "name": participant_name,
                "type": "AI",
                "ai_config": ai_config
            }
        )
        response.raise_for_status()
        participant = response.json()
        participant_id = participant["id"]
        
        # Connect via WebSocket
        ws_url = f"{WS_BASE_URL}/session/{self.session_id}?participant_id={participant_id}"
        async with websockets.connect(ws_url) as websocket:
            print(f"✓ {participant_name} connected to WebSocket")
            
            # Listen for messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    data = json.loads(message)
                    
                    # Log received messages
                    if data.get("type") == "chat" and data.get("participant", {}).get("name"):
                        sender = data["participant"]["name"]
                        content = data["content"]
                        print(f"\n[{sender}]: {content}")
                        
                except asyncio.TimeoutError:
                    # No message received, continue
                    pass
                except websockets.exceptions.ConnectionClosed:
                    print(f"\n✗ {participant_name} disconnected")
                    break
                except Exception as e:
                    print(f"\n✗ {participant_name} error: {e}")
                    break
    
    async def monitor_session(self):
        """Monitor the session as a researcher."""
        print("\nConnecting monitor...")
        ws_url = f"{WS_BASE_URL}/session/{self.session_id}?participant_id=monitor"
        
        async with websockets.connect(ws_url) as websocket:
            print("✓ Monitor connected")
            
            start_time = time.time()
            duration_seconds = 60  # Run for 1 minute as a demo
            
            while time.time() - start_time < duration_seconds:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    # Handle different message types
                    if data.get("type") == "session_info":
                        participant_count = len(data.get("participants", []))
                        print(f"\nSession info: {participant_count} participants")
                    elif data.get("type") == "participant_joined":
                        print(f"\n→ {data.get('participant_name', 'Unknown')} joined")
                    elif data.get("type") == "participant_left":
                        print(f"\n← {data.get('participant_name', 'Unknown')} left")
                        
                except asyncio.TimeoutError:
                    pass
                except Exception as e:
                    print(f"\nMonitor error: {e}")
                    break
            
            print(f"\n\nDemo completed! Session ran for {int(time.time() - start_time)} seconds")
    
    def complete_session(self):
        """Mark the session as completed."""
        print("\nCompleting session...")
        response = requests.put(
            f"{API_BASE_URL}/sessions/{self.session_id}/complete",
            json={"completed_by": "test_script"}
        )
        response.raise_for_status()
        print("✓ Session completed")
    
    async def run_experiment(self):
        """Run the full experiment flow."""
        print("=" * 60)
        print("MULTI-AGENT AI EXPERIMENT TEST")
        print("=" * 60)
        
        try:
            # Setup
            self.create_experiment()
            self.start_session()
            
            print(f"\n🔗 Access the researcher dashboard at:")
            print(f"   http://localhost:5173/researcher")
            print(f"   Session access code: {self.access_code}")
            
            # Get AI participants from config
            ai_participants = TEST_EXPERIMENT["config"]["ai_participants"]
            
            # Run AI participants and monitor concurrently
            tasks = []
            
            # Add monitor task
            tasks.append(self.monitor_session())
            
            # Add AI participant tasks
            for i, ai_config in enumerate(ai_participants[:3]):  # Limit to 3 for demo
                tasks.append(self.join_ai_participant(ai_config, i + 1))
            
            # Wait for all tasks (will run for the monitor duration)
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Cleanup
            self.complete_session()
            
            print("\n" + "=" * 60)
            print("TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


async def main():
    """Main entry point."""
    runner = ExperimentRunner()
    await runner.run_experiment()


if __name__ == "__main__":
    print("Starting test script...")
    print("Make sure the backend is running at http://localhost:8000")
    print("Make sure you have set OPENAI_API_KEY in backend/.env")
    input("\nPress Enter to continue...")
    
    asyncio.run(main())