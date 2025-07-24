#!/bin/bash
cd /Users/bryanacton/Documents/GitHub/team-llm/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000