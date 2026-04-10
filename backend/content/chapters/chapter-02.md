---
chapter_id: chapter-02
title: Claude Agent SDK Deep Dive
order: 2
tier: free
estimated_minutes: 20
tags: [claude, sdk, tools, memory, handoffs, agents, anthropic]
---

# Chapter 2: Claude Agent SDK Deep Dive

## What You Will Learn
- How the Claude Agent SDK structures an agent
- Tool definitions: schemas, handlers, and safety
- Memory types: in-context, external, and episodic
- Handoffs: passing control between agents
- Building your first tool-using agent

---

## 2.1 Overview of the Claude Agent SDK

The **Claude Agent SDK** (also called the Anthropic Agents SDK) is a Python library that provides the primitives needed to build production agents on top of Claude models. It sits at **Layer 5** of the Agent Factory Architecture.

The three core primitives are:

| Primitive | What it does |
|---|---|
| **Agent** | Defines an agent: its model, system prompt, tools, and handoff targets |
| **Tool** | A function the agent can call to interact with the real world |
| **Runner** | Executes the agent loop: sends messages, processes tool calls, loops until done |

A minimal agent looks like this in concept:

```python
from anthropic_agents import Agent, Tool, Runner

def get_weather(city: str) -> str:
    return f"It is 22°C and sunny in {city}."

weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={"city": {"type": "string", "description": "City name"}},
    handler=get_weather,
)

agent = Agent(
    model="claude-sonnet-4-6",
    system="You are a helpful weather assistant.",
    tools=[weather_tool],
)

result = Runner.run(agent, "What's the weather in Karachi?")
print(result.final_output)
```

The runner automatically handles the loop: Claude decides to call `get_weather`, the SDK executes it, Claude receives the result, and produces a final answer.

---

## 2.2 Tool Definitions In Depth

A **Tool** in the Claude Agent SDK is a Python function wrapped with a schema. The schema tells Claude *when* and *how* to use the tool. Getting schemas right is critical — a vague description leads to incorrect tool calls.

### Anatomy of a Good Tool

```python
Tool(
    name="search_content",
    description=(
        "Search the course content for a keyword. "
        "Use this when the student asks about a specific concept "
        "that might be in the course materials."
    ),
    parameters={
        "query": {
            "type": "string",
            "description": "The search keyword or phrase",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return (default 5)",
        },
    },
    required=["query"],
    handler=search_content_handler,
)
```

### Tool Safety Rules

1. **Never give an agent a tool it cannot safely use autonomously.** If the tool can delete data, require human-in-the-loop confirmation.
2. **Return structured data, not prose.** Tools should return JSON-serialisable dicts. Claude will compose the prose.
3. **Handle errors explicitly.** Return `{"error": "reason"}` on failure — do not raise exceptions that crash the runner.

---

## 2.3 Memory in Claude Agents

Claude has a context window — a fixed-length conversation history that acts as short-term memory. For longer-running agents, you need additional memory strategies:

### In-Context Memory
The simplest form: the entire conversation history lives inside Claude's context window. Works for short tasks (under ~50 turns). After that, the oldest messages fall out.

### External Memory (Retrieval)
For long-term facts and user history, store data externally (PostgreSQL, Redis, vector store) and **retrieve** it at the start of each agent run. Example:

```python
user_profile = await db.fetch_user_profile(user_id)
agent_input = f"User profile: {user_profile}\n\nUser question: {question}"
```

### Episodic Memory
Store summaries of past agent runs. At the start of a new run, retrieve the N most relevant past episodes and inject them into the system prompt. This enables an agent to say "Last time you asked about MCP, we discussed X..." and provide continuity across sessions.

In Phase 2, this course implements episodic memory using the `streaks` and `progress` tables already in the database.

---

## 2.4 Handoffs: Multi-Agent Coordination

A **handoff** is when one agent passes control to another specialist agent. This is the foundation of multi-agent systems.

```
User Query
    |
    v
Triage Agent --> "This is a quiz question"
    |
    v
Quiz Master Agent --> calls /quiz/{id} API --> grades answer
    |
    v
Motivation Agent --> celebrates the result
```

In the Claude Agent SDK, handoffs are defined by listing other agents as targets:

```python
quiz_agent = Agent(name="quiz_master", ...)
motivation_agent = Agent(name="motivator", ...)

triage_agent = Agent(
    name="triage",
    handoffs=[quiz_agent, motivation_agent],
)
```

Handoffs preserve the full conversation context — the receiving agent sees the entire history.

---

## 2.5 The Agent Loop in Detail

Understanding the internal loop is essential for debugging agents:

```
1. Receive user message
2. Build context: system prompt + conversation history + tool schemas
3. Send to Claude API
4. Claude returns: either a TEXT response or a TOOL_USE block
5. If TOOL_USE:
   a. Extract tool name and arguments
   b. Execute the tool handler
   c. Append tool result to conversation history
   d. Go to step 3 (loop continues)
6. If TEXT: return final response to user
```

The loop runs until Claude produces a text response (or a max-iterations safety limit is hit). In production, always set `max_turns=20` or similar to prevent runaway loops and unexpected costs.

---

## 2.6 Guardrails and Output Validation

Production agents need guardrails — rules that prevent unsafe or incorrect outputs:

- **Input guardrails**: Validate user input before sending to the agent (e.g. reject prompt injection attempts)
- **Output guardrails**: Validate the agent's final response (e.g. ensure it contains no PII, stays on topic)
- **Tool guardrails**: Validate tool arguments before execution (e.g. check that a file path is safe)

The Claude Agent SDK supports both synchronous and asynchronous guardrail functions that run before and after each agent step.

---

## Summary

- The Claude Agent SDK provides **Agent**, **Tool**, and **Runner** as its three core primitives
- Tool descriptions must be **specific about when to use them** — vague descriptions cause incorrect calls
- Memory has three layers: **in-context** (context window), **external** (DB/Redis), **episodic** (past run summaries)
- **Handoffs** allow specialist agents to collaborate on complex tasks
- The agent loop runs until Claude emits a final text response — always set a `max_turns` limit
- **Guardrails** protect against unsafe inputs, outputs, and tool arguments

## Next Steps

Proceed to **Chapter 3: MCP and Agent Skills** — where you learn how the Model Context Protocol provides tools and knowledge to agents as a standardised service.
