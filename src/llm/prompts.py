"""
Prompt templates for memory extraction and personality generation.
Uses Few-Shot Prompting for extractors and Linguistic Markers for personalities.
"""

# =============================================================================
# MEMORY EXTRACTION PROMPTS (Few-Shot with Examples)
# =============================================================================

PREFERENCE_EXTRACTION_PROMPT = """You are an AI that extracts user preferences from chat history.

TASK: Identify explicit and implicit preferences in these categories:
- communication: How they prefer to interact (formal/casual, long/short messages)
- interests: Topics, hobbies, subjects they engage with positively  
- lifestyle: Schedule patterns, work style, life priorities
- values: What they care about, ethical stances, principles

=== FEW-SHOT EXAMPLE ===

INPUT:
[0] I really prefer when people just get to the point. No fluff.
[1] Been getting into rock climbing lately, it's amazing!
[2] I always wake up at 5am to work out before my day starts.
[3] Honesty is everything to me. I can't stand liars.

OUTPUT:
{
  "preferences": [
    {
      "category": "communication",
      "description": "Prefers direct, concise communication without unnecessary elaboration",
      "confidence": 1.0,
      "source_message_ids": [0],
      "evidence": "User said 'I really prefer when people just get to the point. No fluff.'"
    },
    {
      "category": "interests",
      "description": "Enjoys rock climbing and physical activities",
      "confidence": 0.9,
      "source_message_ids": [1],
      "evidence": "User mentioned 'Been getting into rock climbing lately, it's amazing!'"
    },
    {
      "category": "lifestyle",
      "description": "Early riser with morning workout routine",
      "confidence": 1.0,
      "source_message_ids": [2],
      "evidence": "User stated 'I always wake up at 5am to work out'"
    },
    {
      "category": "values",
      "description": "Highly values honesty and transparency in relationships",
      "confidence": 1.0,
      "source_message_ids": [3],
      "evidence": "User explicitly said 'Honesty is everything to me'"
    }
  ]
}

=== END EXAMPLE ===

CONFIDENCE GUIDE:
- 1.0: Explicitly stated ("I prefer...", "I always...", "I love...")
- 0.7-0.9: Strongly inferred from behavior, reactions, or context
- 0.5-0.7: Weak signal, needs more data to confirm

RULES:
1. Only extract preferences with clear evidence from the messages
2. Always cite specific message indices as evidence
3. Include a direct quote or close paraphrase in the evidence field
4. If no preferences are found, return {"preferences": []}

Respond ONLY with valid JSON matching the format above. No explanations."""


EMOTION_EXTRACTION_PROMPT = """You are an AI that identifies emotional patterns in chat history.

TASK: Find recurring emotional patterns - what triggers emotions, how often they appear, and the range of emotions observed.

=== FEW-SHOT EXAMPLE ===

INPUT:
[0] Ugh, another deadline from my boss. I'm so stressed.
[1] Finally finished my project today! Feeling accomplished.
[2] The deadline pressure is killing me. Can't sleep.
[3] Managed to submit on time. Such relief!
[4] New deadline just dropped. Here we go again with the anxiety.

OUTPUT:
{
  "emotional_patterns": [
    {
      "pattern": "Experiences stress and anxiety around work deadlines",
      "triggers": ["deadlines", "boss pressure", "time constraints"],
      "frequency": "frequent",
      "emotional_range": ["stressed", "anxious", "overwhelmed"],
      "source_message_ids": [0, 2, 4]
    },
    {
      "pattern": "Feels accomplishment and relief after completing tasks",
      "triggers": ["finishing projects", "meeting deadlines", "task completion"],
      "frequency": "occasional",
      "emotional_range": ["accomplished", "relieved", "satisfied"],
      "source_message_ids": [1, 3]
    }
  ]
}

=== END EXAMPLE ===

FREQUENCY GUIDE:
- rare: Appeared 1-2 times in the conversation
- occasional: Appeared 3-5 times or in ~20% of messages
- frequent: Appeared in many messages or is a dominant theme

RULES:
1. Look for patterns, not one-off emotions
2. Identify specific triggers when possible
3. Note the full range of emotions within each pattern
4. If no patterns are found, return {"emotional_patterns": []}

Respond ONLY with valid JSON matching the format above."""


FACT_EXTRACTION_PROMPT = """You are an AI that extracts factual information about a user from their chat history.

TASK: Extract facts in these categories:
- personal: Name, age, location, family members, personal details
- professional: Job title, company, skills, career goals, work situation
- relational: People mentioned (friends, family, colleagues), relationships
- temporal: Specific events, dates, milestones, upcoming plans

=== FEW-SHOT EXAMPLE ===

INPUT:
[0] Just got back from my sister's wedding in Mumbai. What a week!
[1] Three years at this startup and I finally got promoted to Senior Engineer.
[2] My friend Rahul and I are planning a trek next month.
[3] Turning 28 next week, feeling old already.

OUTPUT:
{
  "facts": [
    {
      "category": "relational",
      "fact": "Has a sister who recently got married",
      "importance": "medium",
      "confidence": 1.0,
      "source_message_ids": [0]
    },
    {
      "category": "personal",
      "fact": "Has connection to Mumbai (sister's wedding location)",
      "importance": "low",
      "confidence": 0.8,
      "source_message_ids": [0]
    },
    {
      "category": "professional",
      "fact": "Senior Engineer at a startup, working there for 3 years",
      "importance": "high",
      "confidence": 1.0,
      "source_message_ids": [1]
    },
    {
      "category": "relational",
      "fact": "Has a friend named Rahul who they trek with",
      "importance": "medium",
      "confidence": 1.0,
      "source_message_ids": [2]
    },
    {
      "category": "temporal",
      "fact": "Planning a trek next month with friend",
      "importance": "medium",
      "confidence": 1.0,
      "source_message_ids": [2]
    },
    {
      "category": "personal",
      "fact": "Turning 28 years old soon",
      "importance": "high",
      "confidence": 1.0,
      "source_message_ids": [3]
    }
  ]
}

=== END EXAMPLE ===

IMPORTANCE GUIDE:
- high: Core identity facts, frequently referenced, defines who they are
- medium: Relevant context that helps understand them
- low: Minor detail, mentioned once, may not be relevant long-term

RULES:
1. Only extract facts that are clearly stated or strongly implied
2. Do not make assumptions beyond what's in the messages
3. If no facts are found, return {"facts": []}

Respond ONLY with valid JSON matching the format above."""


# =============================================================================
# PERSONALITY PROMPTS (Generic fallback)
# =============================================================================

GENERIC_RESPONSE_PROMPT = """You are a helpful AI assistant responding to a user.
Provide a friendly, helpful response to their message.
Keep your response natural and conversational.
Do not reference any prior context or memory about the user."""
