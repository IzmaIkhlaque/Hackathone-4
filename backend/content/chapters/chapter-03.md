---
chapter_id: chapter-03
title: MCP and Agent Skills
order: 3
tier: free
estimated_minutes: 18
tags: [mcp, skills, protocol, tools, agents, context, model-context-protocol]
---

# Chapter 3: MCP and Agent Skills

## What You Will Learn
- What the Model Context Protocol (MCP) is and why it exists
- The difference between Tools, Resources, and Prompts in MCP
- How to build and register an MCP server
- What Agent Skills are and how SKILL.md files work
- How the ChatGPT App uses Skills to route tasks

---

## 3.1 What Is the Model Context Protocol?

**Model Context Protocol (MCP)** is an open standard that defines how AI agents discover and call external capabilities. Think of it as a USB-C port for AI — a single standardised interface that works with any model and any tool provider.

Before MCP, every AI framework had its own way of defining tools. LangChain had one format, AutoGen had another, Claude had a third. Integrating a new tool meant rewriting the adapter for each framework.

MCP solves this by defining three universal building blocks:

| Building Block | What it is | Example |
|---|---|---|
| **Tool** | A function the agent can call | `search_database(query)` |
| **Resource** | A piece of data the agent can read | A file, a database row, a URL |
| **Prompt** | A reusable message template | "Explain {concept} to a {level} student" |

Any MCP-compatible agent (Claude, GPT-4, Gemini) can connect to any MCP server and use its Tools, Resources, and Prompts automatically.

---

## 3.2 MCP in the Agent Factory Architecture

In the 8-layer Agent Factory, MCP sits at **Layer 4**:

```
L5 Claude Agent SDK (executes the agent loop)
        |
        v
L4 MCP Server (provides tools and knowledge)
        |
        v
L3 FastAPI (HTTP interface, our Phase 1 backend)
```

Our FastAPI backend IS the MCP server's data source. When an agent calls the MCP `get_chapter` tool, the MCP server calls our `/content/chapters/{id}` endpoint, and returns the markdown to the agent.

This layering means:
- The agent never calls our FastAPI directly
- All agent interactions go through the MCP server
- Changing the backend only requires updating the MCP server, not the agent

---

## 3.3 Building an MCP Server

An MCP server in Python is a small service that registers tools and serves them over a JSON-RPC interface. Here is the structure of an MCP server for our course:

```python
from mcp import MCPServer, tool, resource

server = MCPServer(name="course-companion-mcp")

@tool(description="Fetch a chapter's content from the course backend")
async def get_chapter(chapter_id: str) -> str:
    """Returns the full markdown content of a chapter."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BACKEND_URL}/api/v1/content/chapters/{chapter_id}",
            headers={"X-User-ID": "mcp-server"}
        )
        return resp.text

@tool(description="Submit quiz answers and get a grade")
async def submit_quiz(quiz_id: str, user_id: str, answers: list) -> dict:
    """Submits answers to the backend and returns score and feedback."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/quiz/{quiz_id}/submit",
            json={"user_id": user_id, "answers": answers}
        )
        return resp.json()

server.run()
```

Each `@tool` decorator registers the function as an MCP tool with an auto-generated schema from the type hints and docstring. The MCP server handles all protocol-level serialisation.

---

## 3.4 MCP Resources

Resources differ from tools in that they are **data sources, not actions**. A resource is something the agent reads, not calls.

```python
@resource(uri="course://chapters/{chapter_id}/summary")
async def chapter_summary(chapter_id: str) -> str:
    """Returns the first 200 words of a chapter for preview."""
    content = await get_chapter_content(chapter_id)
    words = content.split()[:200]
    return " ".join(words)
```

The agent can list all available resources and decide which ones are relevant to the current task — similar to how a human researcher decides which books to read before answering a question.

---

## 3.5 Agent Skills and SKILL.md Files

**Agent Skills** are reusable task modules that define a specific behaviour pattern for an agent. They are stored as `SKILL.md` files and loaded into the agent's system prompt.

A SKILL.md file contains:
1. **Frontmatter**: name, version, and trigger phrases
2. **Purpose**: what the skill does and when to activate it
3. **Workflow**: step-by-step instructions the agent follows
4. **Response templates**: exact language to use in responses

This course uses four skills:

| Skill | Trigger Phrases | Purpose |
|---|---|---|
| `concept-explainer` | "explain", "what is", "how does" | Ground explanations in course content |
| `quiz-master` | "quiz me", "test me", "practice" | Guide through quizzes with encouragement |
| `socratic-tutor` | "I'm stuck", "help me think" | Guide to answers through questions |
| `progress-motivator` | "my progress", "streak", "stats" | Celebrate achievements with real data |

### How Skills Work at Runtime

When a student sends a message, the triage logic in the system prompt pattern-matches the message against each skill's trigger phrases. The matching skill's workflow becomes the agent's instruction set for that turn.

```
Student: "Can you quiz me on Chapter 1?"
    |
    v
Trigger match: "quiz me" -> quiz-master skill activates
    |
    v
Step 1: Call GET /quiz/quiz-01
Step 2: Present question 1 with options A/B/C/D
Step 3: Wait for answer
Step 4: Submit to POST /quiz/quiz-01/submit
Step 5: Give feedback
```

This structured workflow ensures the agent behaves consistently, regardless of how the student phrases their request.

---

## 3.6 Designing Good Skills

A well-designed skill has three properties:

**1. Single Responsibility** — each skill does one thing well. The quiz-master skill does not explain concepts; it runs quizzes. The concept-explainer does not grade — it explains. Mixing concerns creates unpredictable behaviour.

**2. Clear Termination** — every skill has a defined endpoint. The quiz-master skill ends when the final question is graded and the score is displayed. Without a clear end state, agents can loop indefinitely.

**3. API-Grounded** — skills should always get data from the backend API, never from Claude's parametric memory (training data). The course content in Claude's training data may be outdated or incorrect. The API is always authoritative.

---

## Summary

- **MCP (Model Context Protocol)** is the standardised interface between agents and external capabilities
- MCP defines three building blocks: **Tools** (actions), **Resources** (data), and **Prompts** (templates)
- In the Agent Factory, MCP sits at Layer 4 and routes agent requests to our FastAPI Layer 3 backend
- **SKILL.md files** define reusable agent behaviours with trigger phrases, workflows, and response templates
- Good skills are **single-responsibility**, have **clear termination**, and are **API-grounded**

## Next Steps

You have completed all three free chapters. To continue learning:
- **Chapter 4** (Premium): OpenAI Agents SDK — Swarm patterns and multi-agent orchestration
- **Chapter 5** (Premium): Multi-Agent Systems and the A2A Protocol
- **Chapter 6** (Pro): Production Deployment and Monitoring
