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
from pathlib import Path
from dotenv import load_dotenv
import os
from restaurant_task_config import AGENT_CONFIGS

# Load environment variables
backend_env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(backend_env_path)

API_BASE_URL = "http://localhost:8000/api"
WS_BASE_URL = "ws://localhost:8000/ws"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

async def run_simulation():
    """Main simulation runner"""
    
    # Setup
    session_id = setup_experiment()
    participants = create_participants(session_id)
    
    print("\n" + "="*60)
    print("🚧 CURRENT STATUS: Agents connect but don't converse")
    print("📝 NEXT STEP: Implement conversation logic below")
    print("="*60 + "\n")
    
    # TODO: Next agent should implement the conversation here
    # 
    # The basic structure should be:
    # 1. Connect all agents via WebSocket
    # 2. Have first agent (Alex) start the conversation
    # 3. Each agent listens for messages
    # 4. When appropriate, agent responds using OpenAI API
    # 5. Continue until consensus reached
    #
    # Key points:
    # - WebSocket URL: f"{WS_BASE_URL}/chat/{session_id}?participant_id={participant_id}"
    # - Message format: {"type": "chat", "content": "message here"}
    # - Use agent's personality and knowledge from AGENT_CONFIGS
    # - Keep messages short and conversational
    
    print("⚠️  Conversation logic not implemented yet!")
    print("See test-ai-agents.py for WebSocket connection code")
    print("See Agent 950's guidance for conversation approach")
    
    # Complete session
    complete_response = requests.post(
        f"{API_BASE_URL}/sessions/{session_id}/complete",
        json={
            "trigger_type": "simulation_end",
            "trigger_value": "not_implemented",
            "final_outcome": {}
        }
    )
    print(f"\n✅ Session completed: {complete_response.status_code}")

def main():
    """Entry point"""
    print("AI Restaurant Discussion Simulation")
    print("="*40)
    
    # Check prerequisites
    if not OPENAI_API_KEY:
        print("❌ ERROR: OpenAI API key not found!")
        print("Make sure backend/.env contains OPENAI_API_KEY")
        return
    
    print(f"✅ OpenAI API key found")
    print(f"✅ Backend should be running at {API_BASE_URL}")
    print()
    
    # Run simulation
    asyncio.run(run_simulation())

if __name__ == "__main__":
    main()