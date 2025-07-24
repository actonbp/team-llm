# Running the AI Agent Test

## Prerequisites

1. **Backend Running**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Frontend Running** (optional, for visual monitoring):
   ```bash
   cd frontend
   npm run dev
   ```

3. **OpenAI API Key** set in `backend/.env`:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Running the Test

```bash
cd scripts
python test-ai-agents.py
```

## What the Test Does

1. **Creates an experiment** with 3 AI personalities:
   - Creative Assistant (brainstorming focus)
   - Analytical Thinker (logical focus)
   - Devil's Advocate (questioning focus)

2. **Starts a session** and gets an access code

3. **Joins AI participants** who will discuss:
   "What would be the most impactful invention for the next decade?"

4. **Monitors the conversation** in real-time for 60 seconds

5. **Outputs the chat** to your terminal

## Expected Output

```
==============================================================
MULTI-AGENT AI EXPERIMENT TEST
==============================================================
Creating experiment...
✓ Created experiment: AI Agent Test - 2025-07-24 16:00 (ID: 1)

Starting session...
✓ Started session: ABC123 (ID: 1)

🔗 Access the researcher dashboard at:
   http://localhost:5173/researcher
   Session access code: ABC123

Joining AI participant 1: Creative Assistant
✓ Creative Assistant connected to WebSocket

Joining AI participant 2: Analytical Thinker
✓ Analytical Thinker connected to WebSocket

[Creative Assistant]: I think the most impactful invention could be...
[Analytical Thinker]: Based on current trends, I would argue...
[Devil's Advocate]: But have we considered the downsides...
```

## Troubleshooting

- **Connection refused**: Make sure backend is running on port 8000
- **No AI responses**: Check OpenAI API key is set correctly
- **WebSocket errors**: Ensure no firewall blocking local connections

## Next Steps

After successful test:
1. View the session in the database
2. Check logs for any errors
3. Modify AI personalities in the script
4. Try different discussion topics