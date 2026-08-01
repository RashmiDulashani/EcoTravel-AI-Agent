# 🌿 EcoTravel   AI - Agentic AI-Based Eco-Tourism Planner for Sri Lanka

An agentic AI application that plans sustainable, multi-day travel itineraries for Sri Lanka, grounded in a domain-specific knowledge base and built on a multi-agent architecture with Retrieval-Augmented Generation (RAG).

**✈️ Live demo:** {EcoTravel AI on Streamlit](https://ecotravel-ai-agent.streamlit.app/)

---

## 📋 Project Overview

Sri Lanka has many eco-tourism destinations, such as national parks, forest reserves, UNESCO World Heritage Sites, eco-friendly hotels, and community-based tourism projects. However, planning a trip that is both environmentally friendly and practical can be difficult because travelers often do not have all the information they need, such as wildlife safety rules, crowd levels, eco-friendly accommodation, and realistic travel times between places.

EcoTravel AI addresses this by combining:
- A **domain-specific RAG knowledge base** of Sri Lankan eco-tourism content
- A **multi-agent pipeline** (Router → Planner → Critic) that classifies, plans, retrieves, and self-corrects itineraries
- **Two deliberately different LLMs** (Groq for fast/cheap tasks, OpenRouter for deep reasoning)
- A **Streamlit interface** for interactive, transparent trip planning

---

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                    │
│   Sidebar (preferences)  │  Chat interface  │  Result panels    │
└───────────────────────────────┬─────────────────────────────────┘
                                │ user query
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 LangGraph Orchestrator (orchestrator.py)             │
│                                                                      │
│   ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌────────┐       │
│   │  Router  │──▶| Extract    |──▶│ Retrieve  │──▶│  Plan  │──┐    |
│   │  Agent   │    |Constraints|    │  (RAG)    │    │ Agent  │  │    │
│   └──────────┘    └───────────┘    └───────────┘    └────────┘  │    │
│                                                        ▲        ▼    │
│                                                        │  ┌────────┐ │
│                                                        │  │ Critic │ │
│                                                        │  │ Agent  │ │
│                                                        │  └───┬────┘ │
│                                                        │      │      │
│                                          retry if failed      │      │
│                                          (max 2 attempts)◄────┘      │
│                                                                │     │
│                                                                ▼     │
│                                                          ┌──────────┐│
│                                                          │ Finalize ││
│                                                          └──────────┘│
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Layer (rag/)                           │
│  ingest.py: Documents → Chunks → Embeddings → ChromaDB          │
│  retriever.py: Query → Embedding → Similarity Search → Context  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Knowledge Base (data/) — 21+ documents             │
│  national_parks/ · forest_reserves/ · eco_hotels/ · unesco/     │
│  wildlife_rules/ · sustainable_tourism/                         │
└─────────────────────────────────────────────────────────────────┘

              LLM Layer (utils/llm.py)
   ┌──────────────────────┐    ┌──────────────────────────┐
   │  Groq                │    │  OpenRouter              │
   │  llama-3.1-8b-instant│    │  claude-haiku-4.5        │
   │  (Router + Critic)   │    │  (Planner)               │
   └──────────────────────┘    └──────────────────────────┘
```

---

## 🧠 Agentic Design Patterns Implemented

| Pattern | Location | Description |
|---|---|---|
| **Router** | `agents/router_agent.py` | Classifies each incoming user query into one of four categories (`parks`, `accommodation`, `planning`, `general`) using a low-cost LLM call, before any heavier processing happens. |
| **Planning / Task Decomposition** | `agents/planner_agent.py` | Decomposes a trip request into three explicit sub-steps: (1) extract structured constraints (duration, budget, interests) from free text, (2) retrieve relevant context per interest, (3) generate a grounded itinerary — rather than attempting the whole task in a single LLM call. |
| **Reflection / Self-Critique** | `agents/critic_agent.py` | Reviews the Planner's output against three explicit criteria (duration match, grounding in retrieved context, intent alignment) and returns structured pass/fail feedback with a suggested fix. |
| **Orchestrator (supporting pattern)** | `orchestrator.py` | A LangGraph state machine coordinates the above agents, including a conditional edge that routes a failed itinerary back to the Planner with the Critic's feedback, capped at 2 retries to guarantee termination. |

---

## 🔄 Agent-to-Agent Communication

Agents do not call each other directly. They read from and write to a single shared, typed state object (`EcoGuideState`, defined in `orchestrator.py`), which LangGraph passes between nodes. This is the structured "message" that agents exchange.

### Sequence / Message-Flow Diagram

```
User Query
   │
   ▼
┌─────────────┐   {category}                         
│ Router Agent│──────────────────┐
└─────────────┘                  │
                                 ▼
                          ┌─────────────────┐  {duration_days, interests}
                          │ Extract Node    │──────────────┐
                          └─────────────────┘              │
                                                           ▼
                                                  ┌─────────────────┐  {context: retrieved chunks}
                                                  │ Retrieve Node   │────────────┐
                                                  └─────────────────┘            │
                                                                                 ▼
                                                                        ┌─────────────────┐  {itinerary}
                                                                        │  Planner Agent  │──────────┐
                                                                        └─────────────────┘          │
                                                                                                     ▼
                                                                                             ┌─────────────────┐
                                                                                             │  Critic Agent   │
                                                                                             └─────────────────┘
                                                                                                       │
                                                                             {passed: false, issues, suggestion}
                                                                                                       │
                                                              ┌────────────────────────────────────────┘
                                                              ▼
                                                    Planner Agent re-runs with
                                                    injected critic feedback
                                                    (max 2 retries, then finalize)
                                                              │
                                                              ▼
                                                    {final_answer} → Streamlit UI
```
---

## ⚙️ Model Selection Strategy

Two different LLMs are used deliberately for different sub-tasks, configured in `utils/llm.py`.

| Sub-task | Model (Provider) | Latency | Cost | Context Window | Reasoning Quality | Why Chosen |
|---|---|---|---|---|---|---|
| Intent routing / classification | Llama 3.1 8B Instant (Groq) | Extremely low (~200–500ms) | Very low - Groq's cheapest tier | 128K tokens | Adequate for simple classification, not used for complex reasoning | Routing decisions ("is this about parks or hotels?") are low-complexity and latency-sensitive; Groq's custom LPU hardware makes this the fastest option for this role |
| Reflection / self-critique | Llama 3.1 8B Instant (Groq) | Extremely low | Very low | 128K tokens | Sufficient for checklist-style evaluation | Critiquing against 3 explicit criteria is a bounded, structured judgment task - doesn't need frontier-model reasoning, and running it cheaply matters since it can be called multiple times per retry loop |
| Trip planning / final itinerary generation | Claude Haiku 4.5 (OpenRouter) | Moderate (~1–3s) | Low-moderate - Haiku-tier pricing | 200K tokens | Strong - handles multi-constraint synthesis (budget + duration + interests + sustainability) noticeably better than the 8B model | Itinerary generation requires balancing multiple constraints and producing coherent, non-generic prose grounded in retrieved context - worth the extra cost/latency over the fast model |

**Design principle:** the same model is never used for everything. Cheap/fast tasks (routing, critique) use Groq; the single most reasoning-intensive task (planning) uses the stronger OpenRouter model.
---

## 📚 RAG Pipeline

### Ingestion (`rag/ingest.py`)
1. **Document loading** - `DirectoryLoader` + `TextLoader` (and optionally `PyPDFLoader` for PDF sources) recursively load all documents from `data/`.
2. **Chunking** - `RecursiveCharacterTextSplitter` with `chunk_size=1000`, `chunk_overlap=200`. This size preserves a full idea per chunk (roughly one paragraph) without diluting embedding precision; the 200-character overlap (~20%) prevents important sentences from being cut across chunk boundaries.
3. **Embedding** - `sentence-transformers/all-MiniLM-L6-v2`: a small (~80MB), CPU-friendly model producing 384-dimensional vectors, chosen for fast inference and low storage cost at acceptable quality for this knowledge base size.
4. **Vector store** - ChromaDB, persisted to `data/chroma_db/` (excluded from git via `.gitignore`; rebuilt automatically on first run in deployment — see `app.py`).

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11 (newer versions, e.g. 3.13+, may lack pre-built wheels for `numpy`/`chromadb` dependencies)
- Groq API key ([console.groq.com](https://console.groq.com))
- OpenRouter API key ([openrouter.ai](https://openrouter.ai))

### Local Setup
```bash
git clone https://github.com/RashmiDulashani/EcoTravel-AI-Agent.git
cd EcoGuide-AI-Agent

py -3.11 -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file at the project root:
```
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

Run the app:
```bash
streamlit run app.py
```

### Deployment (Streamlit Community Cloud)
1. Push the repository to GitHub (`.env` excluded via `.gitignore`)
2. On [share.streamlit.io](https://share.streamlit.io), deploy from the repo, branch `main`, main file `app.py`
3. Set Python version to **3.11** in Advanced Settings
4. Add secrets in TOML format:
   ```toml
   GROQ_API_KEY="your_key"
   OPENROUTER_API_KEY="your_key"
   ```
5. On first load, the app automatically builds the Chroma vector store (since `data/chroma_db/` is gitignored and doesn't exist in a fresh deployment) - this takes 1–2 minutes on first run only.

---

## ⚠️ Known Limitations

- **No travel feasibility check:** The system does not check whether all recommended destinations can realistically be visited within the available trip time.
- **Limited knowledge base:** The knowledge base contains only 21 documents, so information about many cities and tourist locations is missing.
- **No fact verification**: The Critic Agent does not verify details such as travel times, opening hours, ticket prices, or other real-world facts.
- **Limited revision attempts:** The system revises an itinerary a maximum of two times before returning the best available result.
- **Limited itinerary details:** Because the source documents are short, the generated itineraries may lack detailed information such as exact prices, schedules, or timings.

## 🚀 Future Improvements

- Add a fourth Critic check for geographic feasibility relative to a stated base location
- Expand the knowledge base with dedicated documents for major cities and towns
- Ingest richer source material (official tourism board PDFs) to increase specificity without hallucination
- Add a ReAct-style tool-use pattern (e.g. a distance/travel-time lookup tool) to ground geographic reasoning in real data rather than LLM judgment alone

---

## 🧰 Tech Stack

- **Orchestration:** LangGraph
- **LLM Framework:** LangChain
- **LLM Providers:** Groq (llama-3.1-8b-instant), OpenRouter (claude-haiku-4.5)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **Vector Store:** ChromaDB
- **UI:** Streamlit
- **Deployment:** Streamlit Community Cloud

---

## 📁 Project Structure

```
EcoGuide-AI-Agent/
├── agents/
│   ├── router_agent.py
│   ├── planner_agent.py
│   └── critic_agent.py
├── rag/
│   ├── ingest.py
│   └── retriever.py
├── utils/
│   └── llm.py
├── scripts/
│   └── create_sample_docs.py
├── data/
│   ├── national_parks/
│   ├── forest_reserves/
│   ├── eco_hotels/
│   ├── unesco/
│   ├── wildlife_rules/
│   ├── sustainable_tourism/
│   └── chroma_db/          (gitignored, auto-built)
├── orchestrator.py
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```