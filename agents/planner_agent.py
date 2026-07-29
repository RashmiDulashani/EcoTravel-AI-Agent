import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_fast_llm, get_reasoning_llm
from rag.retriever import get_retriever

EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Extract structured trip planning constraints from the user's request.
Respond ONLY with valid JSON, no other text, in this exact format:
{{"duration_days": <number or null if not specified>, "budget_usd": <number or null if not specified>, "interests": ["<interest1>", "<interest2>", ...]}}

Interests should be chosen from: wildlife, hiking, beaches, culture, relaxation, birdwatching, rainforest, hotels
If duration or budget isn't mentioned, use null. Always include at least one interest."""),
    ("human", "{query}")
])

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a sustainable trip planning expert for Sri Lanka.
Using ONLY the provided context documents, create a day-by-day itinerary that matches the user's constraints.
Prioritize sustainability: mention eco-certifications, low-impact activities, and community-based tourism where relevant in the context.
If the context doesn't cover something, do not invent specific facts — speak generally instead.

Respond in this format:
Day 1: <title>
- <activity details, 2-3 sentences, referencing which park/hotel/reserve>

Day 2: <title>
...continue for the full duration.

End with a "Sustainability Notes" section (2-3 sentences) summarizing how this itinerary minimizes environmental impact."""),
    ("human", """User request: {query}

Constraints: {constraints}

Retrieved context:
{context}""")
])

DEFAULT_INTEREST_FALLBACK = ["wildlife"]


def extract_constraints(query: str) -> dict:
    """Extracts duration, budget, and interests from a free-text trip request."""
    fast_llm = get_fast_llm()
    chain = EXTRACT_PROMPT | fast_llm
    response = chain.invoke({"query": query})

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"duration_days": None, "budget_usd": None, "interests": DEFAULT_INTEREST_FALLBACK}


def gather_context(constraints: dict, k_per_interest: int = 3) -> str:
    """Runs a retrieval query for each interest and combines results into one context string."""
    retriever = get_retriever(k=k_per_interest)

    all_chunks = []
    for interest in constraints.get("interests", DEFAULT_INTEREST_FALLBACK):
        query = f"eco-tourism {interest} in Sri Lanka"
        docs = retriever.invoke(query)
        for doc in docs:
            all_chunks.append(f"[Source: {doc.metadata['source']}]\n{doc.page_content}")

    return "\n\n".join(all_chunks)


def generate_itinerary(query: str, constraints: dict, context: str) -> str:
    """Generates a day-by-day itinerary grounded in the retrieved context."""
    reasoning_llm = get_reasoning_llm()
    chain = PLANNER_PROMPT | reasoning_llm
    response = chain.invoke({
        "query": query,
        "constraints": json.dumps(constraints),
        "context": context
    })
    return response.content


def plan_trip(query: str) -> dict:
    """
    Full planning pipeline in one call: extract -> retrieve -> generate.
    Convenience function for testing this file standalone.

    Returns:
        dict with keys "constraints", "context", "itinerary"
    """
    constraints = extract_constraints(query)
    context = gather_context(constraints)
    itinerary = generate_itinerary(query, constraints, context)

    return {"constraints": constraints, "context": context, "itinerary": itinerary}


if __name__ == "__main__":
    test_query = "Plan me a 3-day trip focused on wildlife and hiking"
    result = plan_trip(test_query)

    print("Constraints:", result["constraints"])
    print("\n--- Itinerary ---")
    print(result["itinerary"])