---
chapter_id: chapter-06
title: Production Deployment and Monitoring
order: 6
tier: pro
estimated_minutes: 28
tags: [deployment, monitoring, production, railway, safety, observability, cost]
---

# Chapter 6: Production Deployment and Monitoring

> **Pro Chapter** — This chapter is available to Pro tier subscribers.

## What You Will Learn
- Deploying FastAPI agents to Railway.app
- Observability: logging, tracing, and metrics for agent systems
- Cost tracking and budget guardrails
- Safety guardrails at scale
- Blue-green deployments for zero-downtime agent updates

---

## 6.1 Deploying to Railway.app

Railway.app is the recommended deployment platform for this course because it supports Docker-based deployments with zero configuration. Our `Dockerfile` in the backend folder is all that is needed.

Steps to deploy:

1. Connect your GitHub repository to Railway
2. Railway auto-detects the `Dockerfile` and builds the container
3. Set your environment variables (DATABASE_URL, R2 credentials) in the Railway dashboard
4. Railway assigns a public URL — update the `server.url` in `openapi.yaml`

The free/starter plan supports 500 compute hours per month, sufficient for a course companion handling up to 10,000 requests per day.

---

## 6.2 Observability for Agent Systems

Standard web app monitoring is not enough for agent systems. You need to track:

- **Token usage per agent run** — to control costs
- **Tool call success rate** — to detect failing integrations
- **Agent loop depth** — to catch runaway agents before they become expensive
- **Handoff chains** — to trace the full path of a multi-agent request

The recommended stack for Phase 2/3 observability is:
- **Structured JSON logging** via Python's `logging` module
- **Trace IDs** passed through the full request chain
- **Langfuse or Arize** for LLM-specific observability (token counts, latency, cost per run)

---

## 6.3 Cost Guardrails

In Phase 2, when LLM calls are added for premium features, cost guardrails become critical:

```python
MAX_TOKENS_PER_REQUEST = 4000
MAX_REQUESTS_PER_USER_PER_DAY = 50

async def check_budget(user_id: str) -> bool:
    daily_usage = await get_daily_token_usage(user_id)
    return daily_usage < MAX_TOKENS_PER_REQUEST * MAX_REQUESTS_PER_USER_PER_DAY
```

Always enforce budget limits **before** making LLM API calls, not after.

---

## 6.4 Safety Guardrails at Scale

Production agent safety requires multiple layers:

- **Input validation**: Strip prompt injection attempts before they reach the agent
- **Output filtering**: Scan responses for PII, harmful content, or hallucinated facts
- **Rate limiting**: Prevent abuse with per-user and per-IP rate limits
- **Audit logging**: Log every agent action to an append-only store for compliance

---

## Summary

- Railway.app deploys Docker-based FastAPI services with minimal configuration
- Agent observability requires **token tracking**, **tool success rates**, and **trace IDs**
- Cost guardrails must run **before** LLM calls, not after
- Safety at scale needs input validation, output filtering, rate limiting, and audit logging

## Course Complete

Congratulations — you have completed the AI Agent Development course. You now have the knowledge to build Digital FTEs using the Agent Factory Architecture, Claude Agent SDK, MCP, and production deployment patterns.
