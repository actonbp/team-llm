#!/usr/bin/env python3
"""
The ONE script to run AI agent simulation.
This creates 4 AI agents discussing restaurant locations.

Current Status: Infrastructure works, agents connect, but don't converse yet.
Next Agent: Make them talk naturally using OpenAI API.
"""

import asyncio
import json
import requests
import time
import websockets
import random
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Dict, List
from restaurant_task_config import AGENT_CONFIGS, CONVERSATION_PROMPT, TASK_DESCRIPTION

# Load environment variables
backend_env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(backend_env_path)

API_BASE_URL = "http://localhost:8000/api"
WS_BASE_URL = "ws://localhost:8000/ws"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Try to import OpenAI
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    print("WARNING: OpenAI package not installed. Install with: pip install openai")
    openai_client = None

def setup_experiment():
    """Create experiment, condition, and session"""
    print("Setting up experiment...")
    
    # Create experiment
    exp_response = requests.post(f"{API_BASE_URL}/experiments/", json={
        "name": f"AI Restaurant Discussion - {time.strftime('%Y-%m-%d %H:%M')}",
        "description": "4 AI agents discuss restaurant locations",
        "config": {
            "duration_minutes": 10,
            "min_participants": 4,
            "max_participants": 4,
            "task": "restaurant_ranking"
        }
    })
    exp_response.raise_for_status()
    experiment = exp_response.json()
    experiment_id = experiment["id"]
    
    # Get or create condition
    cond_response = requests.get(f"{API_BASE_URL}/experiments/{experiment_id}/conditions/")
    conditions = cond_response.json()
    
    if conditions:
        condition_id = conditions[0]["id"]
    else:
        cond_response = requests.post(
            f"{API_BASE_URL}/experiments/{experiment_id}/conditions/",
            json={
                "name": "Default",
                "description": "Standard restaurant task",
                "parameters": {"agents": 4}
            }
        )
        condition_id = cond_response.json()["id"]
    
    # Create session
    session_response = requests.post(f"{API_BASE_URL}/sessions/", json={
        "condition_id": condition_id,
        "team_size": 4,
        "required_humans": 0,
        "session_config": {
            "task_description": "Rank 3 restaurant locations based on 10 criteria"
        }
    })
    session_response.raise_for_status()
    session = session_response.json()
    session_id = session["id"]
    
    # Start session
    start_response = requests.post(f"{API_BASE_URL}/sessions/{session_id}/start")
    start_response.raise_for_status()
    
    print(f"✅ Created session: {session_id}")
    return session_id

def create_participants(session_id):
    """Create AI participants"""
    participants = []
    
    for agent in AGENT_CONFIGS:
        response = requests.post(f"{API_BASE_URL}/participants/", json={
            "session_id": session_id,
            "name": agent["name"],
            "is_ai": True,
            "participant_type": "ai",
            "ai_config": {
                "provider": agent["provider"],
                "model": agent["model"],
                "api_key": OPENAI_API_KEY,
                "persona": agent["persona"],
                "knowledge": agent["knowledge"]
            }
        })
        response.raise_for_status()
        participant = response.json()
        participants.append({
            "id": participant["id"],
            "name": agent["name"],
            "agent_config": agent
        })
        print(f"✅ Created participant: {agent['name']}")
    
    return participants


class AIAgent:
    """Represents an AI agent in the conversation"""
    
    def __init__(self, participant_info: dict, session_id: str):
        self.id = participant_info["id"]
        self.name = participant_info["name"]
        self.config = participant_info["agent_config"]
        self.session_id = session_id
        self.websocket = None
        self.conversation_history = []
        self.last_message_time = None
        
    async def connect(self):
        """Connect to WebSocket"""
        url = f"{WS_BASE_URL}/chat/{self.session_id}?participant_id={self.id}"
        self.websocket = await websockets.connect(url)
        print(f"✅ {self.name} connected to WebSocket")
        
    async def listen(self, message_handler):
        """Listen for messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await message_handler(self, data)
        except websockets.exceptions.ConnectionClosed:
            print(f"❌ {self.name} disconnected")
            
    async def send_message(self, content: str):
        """Send a chat message"""
        message = {
            "type": "chat",
            "content": content
        }
        await self.websocket.send(json.dumps(message))
        self.last_message_time = time.time()
        
    async def generate_response(self, conversation_context: List[dict]) -> str:
        """Generate a response using OpenAI API"""
        if not openai_client:
            # Fallback for testing without OpenAI
            responses = [
                f"Hi everyone! I'm {self.name}.",
                "That's a good point!",
                "I agree with that.",
                "What about the parking situation?",
                "We should consider all the criteria.",
            ]
            return random.choice(responses)
            
        # Build conversation history for context
        messages = [
            {"role": "system", "content": CONVERSATION_PROMPT.format(
                name=self.name,
                persona=self.config["persona"],
                knowledge=json.dumps(self.config["knowledge"], indent=2)
            )},
            {"role": "system", "content": f"Task: {TASK_DESCRIPTION}"}
        ]
        
        # Add recent conversation (last 10 messages)
        for msg in conversation_context[-10:]:
            if msg["sender"] == self.name:
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": f"{msg['sender']}: {msg['content']}"})
        
        try:
            response = openai_client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                max_tokens=150,
                temperature=0.9
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Error generating response for {self.name}: {e}")
            return f"Sorry, I'm having trouble responding... ({self.name})"
            
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()

async def run_simulation():
    """Main simulation runner"""
    
    # Setup
    session_id = setup_experiment()
    participants = create_participants(session_id)
    
    print("\n" + "="*60)
    print("🎭 Starting AI Restaurant Discussion")
    print("="*60 + "\n")
    
    # Create AI agents
    agents = [AIAgent(p, session_id) for p in participants]
    
    # Shared conversation state
    conversation_history = []
    transcript = []
    consensus_reached = False
    turn_count = 0
    max_turns = 40  # Prevent infinite loops
    
    async def message_handler(agent: AIAgent, data: dict):
        """Handle incoming messages"""
        msg_type = data.get("type")
        
        if msg_type == "chat":
            sender_name = data.get("participant_name", "Unknown")
            content = data.get("content", "")
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Don't process our own messages
            if sender_name == agent.name:
                return
                
            # Add to conversation history
            conversation_history.append({
                "sender": sender_name,
                "content": content,
                "timestamp": timestamp
            })
            
            # Add to transcript
            transcript.append(f"[{timestamp}] {sender_name}: {content}")
            print(f"[{timestamp}] {sender_name}: {content}")
            
            # Check for consensus keywords
            if any(word in content.lower() for word in ["agree on", "consensus", "final ranking", "task-complete"]):
                nonlocal consensus_reached
                consensus_reached = True
    
    try:
        # Connect all agents
        print("🔌 Connecting agents...")
        for agent in agents:
            await agent.connect()
            
        # Start listening tasks for all agents
        listen_tasks = []
        for agent in agents:
            task = asyncio.create_task(agent.listen(message_handler))
            listen_tasks.append(task)
            
        # Give connections time to establish
        await asyncio.sleep(1)
        
        # Start conversation with Alex
        print("\n💬 Starting conversation...\n")
        opener = "Hey team! Let's work on ranking these restaurant locations. Should we start by sharing what we know about each place?"
        await agents[0].send_message(opener)
        transcript.append(f"[{datetime.now().strftime('%H:%M:%S')}] {agents[0].name}: {opener}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {agents[0].name}: {opener}")
        
        # Conversation loop
        last_speaker_idx = 0
        while not consensus_reached and turn_count < max_turns:
            # Wait for natural pause
            await asyncio.sleep(random.uniform(2, 4))
            
            # Choose next speaker (round-robin with some randomness)
            next_speaker_idx = (last_speaker_idx + random.randint(1, 3)) % len(agents)
            agent = agents[next_speaker_idx]
            
            # Skip if agent spoke too recently
            if agent.last_message_time and time.time() - agent.last_message_time < 3:
                continue
                
            # Generate and send response
            response = await agent.generate_response(conversation_history)
            if response:
                await agent.send_message(response)
                timestamp = datetime.now().strftime("%H:%M:%S")
                conversation_history.append({
                    "sender": agent.name,
                    "content": response,
                    "timestamp": timestamp
                })
                transcript.append(f"[{timestamp}] {agent.name}: {response}")
                print(f"[{timestamp}] {agent.name}: {response}")
                last_speaker_idx = next_speaker_idx
                turn_count += 1
                
        # Wait a bit for final messages
        await asyncio.sleep(3)
        
        # Complete session
        print("\n" + "="*60)
        if consensus_reached:
            print("✅ Consensus reached!")
        else:
            print("⏱️ Time limit reached")
            
        # Save transcript
        transcript_path = Path(__file__).parent / f"transcript_{session_id[:8]}.txt"
        with open(transcript_path, "w") as f:
            f.write("AI Restaurant Discussion Transcript\n")
            f.write("="*40 + "\n\n")
            f.write("\n".join(transcript))
            
        print(f"📝 Transcript saved to: {transcript_path}")
        
        complete_response = requests.post(
            f"{API_BASE_URL}/sessions/{session_id}/complete",
            json={
                "trigger_type": "consensus" if consensus_reached else "time_limit",
                "trigger_value": str(turn_count),
                "final_outcome": {
                    "turns": turn_count,
                    "consensus": consensus_reached
                }
            }
        )
        print(f"✅ Session completed: {complete_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
        
    finally:
        # Clean up connections
        for agent in agents:
            await agent.close()
            
        # Cancel listen tasks
        for task in listen_tasks:
            task.cancel()

def main():
    """Entry point"""
    print("AI Restaurant Discussion Simulation")
    print("="*40)
    
    # Check prerequisites
    if not OPENAI_API_KEY:
        print("⚠️ WARNING: OpenAI API key not found!")
        print("The simulation will use mock responses.")
        print("To use real AI, add OPENAI_API_KEY to backend/.env")
        print()
    elif not openai_client:
        print("⚠️ WARNING: OpenAI package not installed!")
        print("Install with: pip install openai")
        print("The simulation will use mock responses.")
        print()
    else:
        print(f"✅ OpenAI API key found and client initialized")
    
    print(f"✅ Backend should be running at {API_BASE_URL}")
    print()
    
    # Run simulation
    asyncio.run(run_simulation())

if __name__ == "__main__":
    main()