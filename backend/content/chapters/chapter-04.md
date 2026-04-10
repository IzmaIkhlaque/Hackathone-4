---
chapter_id: chapter-04
title: OpenAI Agents SDK
order: 4
tier: premium
estimated_minutes: 22
tags: [openai, sdk, swarm, orchestration, agents, multi-agent, handoffs]
---

# Chapter 4: OpenAI Agents SDK

> **Premium Chapter** — Unlock this chapter to continue your AI Agent development journey.

## What You Will Learn
- The OpenAI Agents SDK architecture and core primitives
- Swarm patterns for lightweight multi-agent orchestration
- Comparing OpenAI Agents SDK vs Claude Agent SDK
- Building handoff chains between specialist agents
- Real-world patterns: triage, parallelisation, and specialisation

---

## 4.1 OpenAI Agents SDK Overview

The **OpenAI Agents SDK** (formerly known as Swarm) is Anthropic's counterpart from OpenAI for building multi-agent systems. It provides a minimalist, lightweight framework centred on two concepts: **Agents** and **Handoffs**.

Unlike heavier frameworks like LangChain or AutoGen, the OpenAI Agents SDK has almost no abstraction overhead. An agent is just:

1. A model (e.g. `gpt-4o`)
2. A system prompt (instructions)
3. A list of tools (functions)
4. A list of agents it can hand off to

This simplicity is intentional. The framework trusts the model to make routing decisions rather than imposing rigid workflow graphs.

---

## 4.2 Swarm Pattern: Triage + Specialist Agents

The most common pattern in the OpenAI Agents SDK is the **Triage + Specialist** pattern:

```
User Message
     |
     v
[Triage Agent]
  - Reads the message
  - Decides which specialist is needed
  - Hands off to that specialist
     |
     +-----> [Content Agent] (handles chapter questions)
     |
     +-----> [Quiz Agent] (handles quiz requests)
     |
     +-----> [Progress Agent] (handles progress/streak queries)
```

Each specialist agent has focused tools and a specific system prompt. This pattern produces higher quality outputs than a single "do-everything" agent because each specialist can be tuned for its specific domain.

---

## 4.3 Parallelisation Pattern

For tasks that can run concurrently, the SDK supports running multiple agents in parallel and merging their outputs:

```python
# Run content fetch and user progress check in parallel
results = await asyncio.gather(
    content_agent.run(f"Summarise {chapter_id}"),
    progress_agent.run(f"Get progress for {user_id}"),
)
summary, progress = results
```

This reduces total latency when multiple independent pieces of information are needed before composing a final response.

---

## 4.4 Comparing Claude SDK vs OpenAI Agents SDK

| Feature | Claude Agent SDK | OpenAI Agents SDK |
|---|---|---|
| Model | Claude (Anthropic) | GPT-4o (OpenAI) |
| Philosophy | Rich primitives (Agent, Tool, Runner, Guardrails) | Minimalist (Agent + Handoff) |
| Memory | Built-in episodic memory support | Manual implementation |
| Guardrails | First-class support | Manual implementation |
| MCP Support | Native | Via OpenAI tools interface |
| Best for | Complex, safety-critical agents | Lightweight routing and orchestration |

In production systems, you may use **both** — Claude for reasoning-heavy tasks and GPT-4o for fast triage and routing. This is called a **heterogeneous multi-agent system**.

---

## Summary

- The OpenAI Agents SDK is minimalist: just Agents and Handoffs
- The **Triage + Specialist** pattern is the most common and effective multi-agent pattern
- Parallelisation reduces latency when tasks are independent
- Claude SDK and OpenAI Agents SDK are complementary tools in a production agent stack

## Next Steps

Proceed to **Chapter 5: Multi-Agent Systems and the A2A Protocol** — where you learn how agents from different frameworks communicate with each other using the Agent-to-Agent protocol.
