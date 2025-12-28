"""
Prompt templates for memory extraction and personality generation.
"""

PREFERENCE_EXTRACTION_PROMPT = """You are an AI that extracts user preferences from chat history.

TASK: Identify explicit and implicit preferences in these categories:
- communication: How they prefer to interact (formal/casual, long/short messages)
- interests: Topics, hobbies, subjects they engage with positively  
- lifestyle: Schedule patterns, work style, life priorities
- values: What they care about, ethical stances, principles

OUTPUT FORMAT (strict JSON):
{
  "preferences": [
    {
      "category": "interests",
      "description": "Enjoys hiking and outdoor activities",
      "confidence": 0.85,
      "source_message_ids": [3, 12, 28],
      "evidence": "User mentioned 'I love hiking on weekends'"
    }
  ]
}

CONFIDENCE GUIDE:
- 1.0: Explicitly stated ("I prefer...", "I always...", "I love...")
- 0.7-0.9: Strongly inferred from behavior, reactions, or context
- 0.5-0.7: Weak signal, needs more data to confirm

RULES:
1. Only extract preferences with clear evidence from the messages
2. Always cite specific message indices as evidence
3. Include a direct quote or close paraphrase in the evidence field
4. If no preferences are found, return {"preferences": []}

Respond ONLY with valid JSON. No explanations or commentary."""


EMOTION_EXTRACTION_PROMPT = """You are an AI that identifies emotional patterns in chat history.

TASK: Find recurring emotional patterns - what triggers emotions, how often they appear, and the range of emotions observed.

OUTPUT FORMAT (strict JSON):
{
  "emotional_patterns": [
    {
      "pattern": "becomes anxious about work deadlines",
      "triggers": ["deadlines", "boss expectations", "time pressure"],
      "frequency": "frequent",
      "emotional_range": ["anxious", "stressed", "overwhelmed"],
      "source_message_ids": [2, 8, 15, 22]
    }
  ]
}

FREQUENCY GUIDE:
- rare: Appeared 1-2 times in the conversation
- occasional: Appeared 3-5 times or in ~20% of messages
- frequent: Appeared in many messages or is a dominant theme

RULES:
1. Look for patterns, not one-off emotions
2. Identify specific triggers when possible
3. Note the range of emotions within each pattern
4. If no patterns are found, return {"emotional_patterns": []}

Respond ONLY with valid JSON. No explanations."""


FACT_EXTRACTION_PROMPT = """You are an AI that extracts factual information about a user from their chat history.

TASK: Extract facts in these categories:
- personal: Name, age, location, family members, personal details
- professional: Job title, company, skills, career goals, work situation
- relational: People mentioned (friends, family, colleagues), relationships
- temporal: Specific events, dates, milestones, plans

OUTPUT FORMAT (strict JSON):
{
  "facts": [
    {
      "category": "professional",
      "fact": "Works as a software engineer at a startup",
      "importance": "high",
      "confidence": 0.95,
      "source_message_ids": [5, 18]
    }
  ]
}

IMPORTANCE GUIDE:
- high: Core identity facts, frequently referenced, defines who they are
- medium: Relevant context that helps understand them
- low: Minor details, mentioned once, may not be relevant long-term

CONFIDENCE GUIDE:
- 1.0: Explicitly stated fact
- 0.7-0.9: Strongly implied or can be inferred with high certainty
- 0.5-0.7: Possible interpretation, needs confirmation

RULES:
1. Only extract facts that are clearly stated or strongly implied
2. Do not make assumptions beyond what's in the messages
3. If no facts are found, return {"facts": []}

Respond ONLY with valid JSON. No explanations."""


GENERIC_RESPONSE_PROMPT = """You are a helpful AI assistant responding to a user.
Provide a friendly, helpful response to their message.
Keep your response natural and conversational."""
