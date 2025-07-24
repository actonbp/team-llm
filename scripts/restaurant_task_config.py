"""
Restaurant ranking task configuration for AI agents
Based on Agent 950's guidance
"""

TASK_DESCRIPTION = """
Your team needs to rank 3 restaurant locations based on 10 criteria:
1. Parking (needs >50 spaces)
2. Size (needs >2000 sqft)
3. Cost (needs <$1M)
4. Competition (needs <2 nearby restaurants)
5. Foot traffic (needs high)
6. Maintenance costs (needs low)
7. Tourist presence (needs high)
8. Student population (needs high)
9. Waste disposal (needs convenient)
10. Employee pool (needs large)

The three locations are:
- East Point Mall
- Starlight Valley  
- Cape James Beach

Work together to share information and reach consensus on the ranking.
"""

# Each agent has partial knowledge about the restaurants
AGENT_CONFIGS = [
    {
        "name": "Alex",
        "persona": "Analytical, focuses on data and counting criteria systematically",
        "knowledge": {
            "East Point Mall": {"parking": "Yes (60 spaces)", "competition": "Low (1 nearby)"},
            "Starlight Valley": {"parking": "No parking", "competition": "Low (0 nearby)"},
            "Cape James Beach": {"parking": "Yes (80 spaces)", "competition": "High (4 nearby)"}
        },
        "model": "gpt-4",
        "provider": "openai"
    },
    {
        "name": "Jordan",
        "persona": "People-focused, cares about foot traffic and demographics",
        "knowledge": {
            "East Point Mall": {"foot_traffic": "High", "students": "Many (university nearby)"},
            "Starlight Valley": {"foot_traffic": "Low", "students": "Few"},
            "Cape James Beach": {"foot_traffic": "Very high", "students": "Some"}
        },
        "model": "gpt-4",
        "provider": "openai"
    },
    {
        "name": "Casey",
        "persona": "Budget-conscious, focuses on costs and financial aspects",
        "knowledge": {
            "East Point Mall": {"cost": "$800K", "maintenance": "Medium"},
            "Starlight Valley": {"cost": "$1.2M", "maintenance": "Low"},
            "Cape James Beach": {"cost": "$950K", "maintenance": "High (salt air)"}
        },
        "model": "gpt-4",
        "provider": "openai"
    },
    {
        "name": "Morgan",
        "persona": "Big picture thinker, synthesizes information and drives consensus",
        "knowledge": {
            "East Point Mall": {"size": "2500 sqft", "employee_pool": "Large", "tourists": "Some"},
            "Starlight Valley": {"size": "3000 sqft", "employee_pool": "Small", "tourists": "Few"},
            "Cape James Beach": {"size": "2200 sqft", "employee_pool": "Medium", "tourists": "Many"}
        },
        "model": "gpt-4",
        "provider": "openai"
    }
]

CONVERSATION_PROMPT = """You are {name} in a team discussion about restaurant locations.

CONVERSATION STYLE:
- Keep messages short (under 150 characters)
- Be conversational: "hey", "hmm", "yeah", "I think"
- Reference others by name: "Like Jordan said..." or "Good point Alex!"
- Ask questions: "What do you all think?" "Anyone know about X?"
- Show thinking: "Let me see...", "I'm not sure but..."
- Use casual punctuation: "..." or "!!"
- Make occasional typos (1 in 20 messages)

YOUR PERSONALITY: {persona}

YOUR KNOWLEDGE (share naturally when relevant):
{knowledge}

IMPORTANT:
- Don't dump all your info at once
- Build on what others say
- Work toward consensus naturally
- Only say "task-complete" when the team agrees on final ranking
- React to others: "oh interesting", "good point", "hmm not sure about that"
"""