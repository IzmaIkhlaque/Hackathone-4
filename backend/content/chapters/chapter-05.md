---
chapter_id: chapter-05
title: Multi-Agent Systems and the A2A Protocol
order: 5
tier: premium
estimated_minutes: 25
tags: [a2a, multi-agent, protocol, orchestration, agent-network, communication]
---

# Chapter 5: Multi-Agent Systems and the A2A Protocol

> **Premium Chapter** — Unlock this chapter to continue your AI Agent development journey.

## What You Will Learn
- What the Agent-to-Agent (A2A) protocol is
- How agents discover and communicate with each other
- Orchestrator vs worker agent patterns
- Building reliable multi-agent pipelines
- Error handling and retry strategies in agent networks

---

## 5.1 The Agent-to-Agent (A2A) Protocol

The **A2A Protocol** is the Layer 7 standard in the Agent Factory Architecture that defines how agents discover, negotiate with, and call each other. It provides a higher-level abstraction for inter-agent communication above the HTTP transport layer.

The A2A protocol defines three components:

1. **Agent Cards** — a JSON document each agent publishes describing its capabilities, input/output schemas, and endpoint URL.
2. **Task Envelope** — the standardised message format for sending work to an agent. Contains the task type, input payload, calling agent identity, and a trace ID for observability.
3. **Result Envelope** — the standardised response format containing result payload, status (success/failure/partial), and any errors.

---

## 5.2 Agent Discovery via Registry

Agents find each other via an **Agent Registry** — a service that maps capability names to agent endpoints. When an orchestrator needs to "summarise a chapter", it queries the registry for an agent with that capability, then sends the task to the returned endpoint.

In Phase 2, the course backend implements a lightweight agent registry inside the `api/v1/hybrid/` folder.

---

## 5.3 Orchestrator vs Worker Pattern

Multi-agent systems divide responsibility into two roles:

**Orchestrator Agent** — the coordinator. Breaks down complex requests into sub-tasks, delegates to workers, collects results, and synthesises a final response. Needs broad knowledge but not deep specialisation.

**Worker Agent** — the specialist. Receives narrow, well-defined tasks and executes them with high quality. Has deep specialisation (e.g. only does quiz grading, or only does content summarisation).

This separation of concerns produces systems that are easier to test, debug, and scale independently.

---

## 5.4 Error Handling in Agent Networks

Agent networks fail in ways single agents do not:

| Failure Mode | Recovery Strategy |
|---|---|
| Timeout | Retry with exponential backoff |
| Partial result | Fallback to cached or default result |
| Agent loop detected | Trace ID + max-hops counter |
| Schema mismatch | Version pinning in agent cards |

Always design for failure. An orchestrator that crashes when one worker fails is not production-ready.

---

## Summary

- The **A2A Protocol** standardises agent-to-agent discovery and communication
- **Agent Cards** describe capabilities; **Task Envelopes** carry work; **Result Envelopes** carry outcomes
- **Orchestrator agents** coordinate; **Worker agents** specialise
- Production multi-agent systems require explicit error handling for timeouts, partial results, and loops

## Next Steps

Proceed to **Chapter 6: Production Deployment and Monitoring** (Pro tier) to learn deployment to Railway.app, observability, cost tracking, and safety guardrails at scale.
