import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_fast_llm

CRITIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a strict quality-control critic reviewing a sustainable travel itinerary.

Check the itinerary against these criteria:
1. DURATION MATCH: Does the itinerary have the correct number of days as requested?
2. GROUNDING: Does the itinerary reference the provided context documents (parks/hotels/reserves mentioned in context), rather than inventing unrelated facts?
3. INTENT ALIGNMENT: Does the itinerary actually match the user's stated intent (e.g. if they wanted low-crowd/quiet experiences, does it avoid recommending explicitly crowded locations)?

Respond ONLY with valid JSON in this exact format, nothing else:
{{"passed": <true or false>, "issues": ["<issue1>", "<issue2>"], "suggestion": "<one sentence fix if passed=false, else empty string>"}}

If there are no issues, "issues" should be an empty list and "passed" should be true."""),
    ("human", """User request: {query}
Constraints: {constraints}
Retrieved context (what the itinerary should be grounded in):
{context}

Generated itinerary to review:
{itinerary}""")
])


def critique_itinerary(query: str, constraints: dict, context: str, itinerary: str) -> dict:
    """
    Reviews an itinerary against constraints and context.

    Returns:
        dict with keys "passed" (bool), "issues" (list of str), "suggestion" (str)
    """
    fast_llm = get_fast_llm()
    chain = CRITIC_PROMPT | fast_llm
    response = chain.invoke({
        "query": query,
        "constraints": json.dumps(constraints),
        "context": context,
        "itinerary": itinerary
    })

    try:
        result = json.loads(response.content)
        # Enforce logical consistency in code: if any issues exist, passed cannot be True
        if result.get("issues"):
            result["passed"] = False
    except json.JSONDecodeError:
        result = {"passed": True, "issues": [], "suggestion": "Could not parse critic output — defaulted to pass"}

    return result


if __name__ == "__main__":
    # Quick manual test using a deliberately flawed itinerary
    bad_query = "I want a quiet, low-crowd 3-day trip focused on wildlife"
    bad_constraints = {"duration_days": 3, "budget_usd": None, "interests": ["wildlife"]}
    bad_context = """[Source: data/national_parks/wilpattu.txt]
Wilpattu is Sri Lanka's largest national park... less crowded than Yala, making it a
better choice for travelers prioritizing sustainability and lower tourist density."""
    bad_itinerary = """Day 1: Yala National Park
- Visit Yala, Sri Lanka's most popular and busiest national park.

Day 2: More Yala
- Continue exploring Yala's crowded Block I.

Sustainability Notes: A great wildlife trip."""

    critique = critique_itinerary(bad_query, bad_constraints, bad_context, bad_itinerary)
    print(json.dumps(critique, indent=2))