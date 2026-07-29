from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.router_agent import route_query
from agents.planner_agent import extract_constraints, gather_context, generate_itinerary
from agents.critic_agent import critique_itinerary

MAX_RETRIES = 2


class EcoGuideState(TypedDict):
    query: str
    category: str
    constraints: dict
    context: str
    itinerary: str
    critique: dict
    retry_count: int
    final_answer: str


def router_node(state: EcoGuideState) -> dict:
    """Node 1: Classifies the query into a category."""
    result = route_query(state["query"])
    print(f"🔀 [Router] Category: {result['category']}")
    return {"category": result["category"]}


def extract_node(state: EcoGuideState) -> dict:
    """Node 2: Extracts structured constraints from the query."""
    constraints = extract_constraints(state["query"])
    print(f"📋 [Extractor] Constraints: {constraints}")
    return {"constraints": constraints, "retry_count": 0}


def retrieve_node(state: EcoGuideState) -> dict:
    """Node 3: Gathers RAG context based on constraints."""
    context = gather_context(state["constraints"])
    print(f"📚 [Retriever] Gathered {len(context)} characters of context")
    return {"context": context}


def plan_node(state: EcoGuideState) -> dict:
    """Node 4: Generates the itinerary. Uses critic feedback if this is a retry."""
    query = state["query"]
    if state.get("critique") and not state["critique"].get("passed", True):
        feedback = state["critique"].get("suggestion", "")
        query = f"{query}\n\nIMPORTANT REVISION NEEDED: {feedback}"

    itinerary = generate_itinerary(query, state["constraints"], state["context"])
    print(f"🗺️  [Planner] Generated itinerary (attempt {state.get('retry_count', 0) + 1})")
    return {"itinerary": itinerary}


def critic_node(state: EcoGuideState) -> dict:
    """Node 5: Reviews the itinerary against constraints and context."""
    critique = critique_itinerary(state["query"], state["constraints"], state["context"], state["itinerary"])
    print(f"🔍 [Critic] Passed: {critique['passed']} | Issues: {critique['issues']}")
    return {"critique": critique, "retry_count": state.get("retry_count", 0) + 1}


def finalize_node(state: EcoGuideState) -> dict:
    """Node 6: Produces the final answer shown to the user."""
    if state["critique"].get("passed", True):
        final = state["itinerary"]
    else:
        final = state["itinerary"] + "\n\n(Note: This itinerary may not fully satisfy all constraints after multiple revision attempts.)"
    print("✅ [Finalizer] Final answer prepared")
    return {"final_answer": final}


def should_retry(state: EcoGuideState) -> str:
    """Conditional edge: decides whether to retry planning or finalize."""
    if state["critique"].get("passed", True):
        return "finalize"
    elif state.get("retry_count", 0) >= MAX_RETRIES:
        print("⚠️  Max retries reached — finalizing with best effort")
        return "finalize"
    else:
        return "plan"


def build_graph():
    """Builds and compiles the LangGraph workflow."""
    workflow = StateGraph(EcoGuideState)

    workflow.add_node("router", router_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("router")
    workflow.add_edge("router", "extract")
    workflow.add_edge("extract", "retrieve")
    workflow.add_edge("retrieve", "plan")
    workflow.add_edge("plan", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_retry,
        {"finalize": "finalize", "plan": "plan"}
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()


def run_ecoguide(query: str) -> dict:
    """
    Public entry point: runs the full multi-agent workflow for a given query.

    Args:
        query: the user's raw question/request

    Returns:
        The complete final state dict (includes final_answer, critique, etc.)
    """
    app_graph = build_graph()
    initial_state = {"query": query}
    return app_graph.invoke(initial_state)