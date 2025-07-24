#!/usr/bin/env python3
"""
Run an all-AI simulation for testing the Team-LLM platform
"""
import asyncio
import aiohttp
import json
import websockets
import sys
from datetime import datetime
from typing import Dict, List, Any
import random
import yaml

# Configuration
API_BASE_URL = "http://localhost:8000/api"
WS_BASE_URL = "ws://localhost:8000/ws"

# Test experiment configuration
TEST_EXPERIMENT = {
    "experimentName": "Restaurant Ranking Test",
    "description": "AI agents collaborate to rank restaurants",
    "version": 1,
    "roles": [
        {
            "name": "Alice",
            "type": "AI",
            "model": "mock",
            "persona": "You are analytical and value quality",
            "knowledge": {
                "Luigi's Italian": {
                    "food_quality": "excellent",
                    "price": "expensive",
                    "atmosphere": "romantic"
                }
            }
        },
        {
            "name": "Bob",
            "type": "AI", 
            "model": "mock",
            "persona": "You are practical and budget-conscious",
            "knowledge": {
                "Burger Palace": {
                    "food_quality": "good",
                    "price": "affordable",
                    "service": "fast"
                }
            }
        },
        {
            "name": "Charlie",
            "type": "AI",
            "model": "mock",
            "persona": "You are a food enthusiast who values authenticity",
            "knowledge": {
                "Thai Garden": {
                    "food_quality": "authentic",
                    "atmosphere": "cozy",
                    "variety": "extensive menu"
                }
            }
        }
    ],
    "scenario": {
        "type": "ranking",
        "duration": 300,
        "task": "Work together to rank these three restaurants (Luigi's Italian, Burger Palace, Thai Garden) from best to worst. Consider all factors and reach a consensus.",
        "completionTrigger": {
            "type": "keyword",
            "value": "task-complete"
        }
    },
    "conditions": [
        {
            "id": "test-condition",
            "name": "Test Condition",
            "description": "Basic test setup with all mock agents"
        }
    ]
}


class AISimulation:
    def __init__(self):
        self.session = None
        self.experiment_id = None
        self.session_id = None
        self.access_code = None
        self.ai_participants = []
        
    async def create_experiment(self):
        """Create a test experiment"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/experiments/import",
                json={
                    "yaml_content": yaml.dump(TEST_EXPERIMENT),
                    "validate_only": False
                },
                params={"created_by": "simulation"}
            ) as response:
                if response.status != 201:
                    text = await response.text()
                    raise Exception(f"Failed to create experiment: {text}")
                data = await response.json()
                self.experiment_id = data["id"]
                print(f"✅ Created experiment: {data['name']} (ID: {self.experiment_id})")
                
    async def create_session(self):
        """Create a session for the experiment"""
        # First get conditions
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/experiments/{self.experiment_id}/conditions"
            ) as response:
                conditions = await response.json()
                condition_id = conditions[0]["id"]
                
            # Create session
            async with session.post(
                f"{API_BASE_URL}/sessions/",
                json={"condition_id": condition_id}
            ) as response:
                if response.status != 201:
                    text = await response.text()
                    raise Exception(f"Failed to create session: {text}")
                data = await response.json()
                self.session_id = data["id"]
                self.access_code = data["access_code"]
                print(f"✅ Created session with access code: {self.access_code}")
                
    async def join_session_with_ai(self):
        """Have AI agents join the session"""
        async with aiohttp.ClientSession() as session:
            # First human must join to activate session
            async with session.post(
                f"{API_BASE_URL}/sessions/join",
                json={
                    "access_code": self.access_code,
                    "participant_name": "Observer",
                    "consent_given": True
                }
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Failed to join session: {text}")
                data = await response.json()
                observer_id = data["participant"]["id"]
                self.ai_participants = data["ai_participants"]
                print(f"✅ Session activated with {len(self.ai_participants)} AI agents")
                return observer_id
                
    async def simulate_conversation(self, observer_id: str):
        """Run the AI conversation via WebSocket"""
        uri = f"{WS_BASE_URL}/session/{self.session_id}?participant_id={observer_id}"
        
        print("\n🤖 Starting AI conversation...\n")
        print("-" * 50)
        
        async with websockets.connect(uri) as websocket:
            # Receive initial session info
            message = await websocket.recv()
            data = json.loads(message)
            
            # Send initial message to start conversation
            await websocket.send(json.dumps({
                "type": "chat",
                "content": "Hello team! Let's work together to rank these restaurants."
            }))
            
            # Monitor conversation
            message_count = 0
            start_time = datetime.now()
            
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    if data["type"] == "chat":
                        message_count += 1
                        print(f"[{data['participant_name']}]: {data['content']}")
                        
                        # Check for completion
                        if "task-complete" in data["content"].lower():
                            print("-" * 50)
                            print(f"\n✅ Task completed! Total messages: {message_count}")
                            break
                            
                    elif data["type"] == "session_completed":
                        print("-" * 50)
                        print(f"\n✅ Session completed! Completion code: {data['completion_code']}")
                        break
                        
                    elif data["type"] == "typing":
                        # Optionally show typing indicators
                        pass
                        
                except asyncio.TimeoutError:
                    # No message received in 30 seconds
                    duration = (datetime.now() - start_time).seconds
                    if duration > 300:  # 5 minute timeout
                        print("\n⏱️ Simulation timed out after 5 minutes")
                        break
                        
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    break
                    
    async def get_session_stats(self):
        """Get final session statistics"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/sessions/{self.session_id}/statistics"
            ) as response:
                stats = await response.json()
                print(f"\n📊 Session Statistics:")
                print(f"   - Participants: {stats['participant_count']}")
                print(f"   - Messages: {stats['message_count']}")
                print(f"   - Duration: {stats['duration_seconds']}s")
                
    async def run(self):
        """Run the complete simulation"""
        try:
            print("🚀 Starting AI Team Simulation...")
            print("=" * 50)
            
            await self.create_experiment()
            await self.create_session()
            observer_id = await self.join_session_with_ai()
            await self.simulate_conversation(observer_id)
            await self.get_session_stats()
            
            print("\n✨ Simulation complete!")
            
        except Exception as e:
            print(f"\n❌ Simulation failed: {e}")
            sys.exit(1)


async def main():
    """Main entry point"""
    simulation = AISimulation()
    await simulation.run()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Team-LLM All-AI Simulation Test       ║
    ╚═══════════════════════════════════════════╝
    
    This script will:
    1. Create a test experiment with 3 AI agents
    2. Start a session
    3. Have the AI agents discuss and rank restaurants
    4. Monitor until task completion
    
    Make sure the backend server is running on http://localhost:8000
    """)
    
    asyncio.run(main())