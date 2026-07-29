import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_fast_llm

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a routing classifier for an eco-tourism assistant about Sri Lanka.
Classify the user's query into EXACTLY ONE of these categories:

- parks: questions about national parks, forest reserves, wildlife, UNESCO natural sites
- accommodation: questions about eco-hotels, lodges, where to stay
- planning: requests for a full itinerary, multi-day trip, or trip plan with constraints (budget, duration)
- general: general sustainable tourism questions, rules, etiquette, or anything unclear

Respond ONLY with valid JSON in this exact format, nothing else:
{{"category": "<one of the four categories>", "reasoning": "<one short sentence why>"}}
"""),
    ("human", "{query}")
])


def route_query(query: str) -> dict:
    """
    Classifies a user query into a category using the Router Agent.

    Args:
        query: the user's raw question/request

    Returns:
        dict with keys "category" and "reasoning"
    """
    fast_llm = get_fast_llm()
    chain = ROUTER_PROMPT | fast_llm
    response = chain.invoke({"query": query})

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"category": "general", "reasoning": "Failed to parse LLM output, defaulted to general"}

    return result


if __name__ == "__main__":
    # Quick manual test when running this file directly
    test_queries = [
        "Where can I see elephants?",
        "What's a good eco-friendly hotel near Sigiriya?",
        "Plan me a 5-day sustainable trip with a $500 budget",
    ]
    for q in test_queries:
        result = route_query(q)
        print(f"Query: {q}")
        print(f"→ {result}\n")