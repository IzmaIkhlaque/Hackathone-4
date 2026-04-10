# Course Companion FTE — Cost Analysis

## Phase 1: Zero-Backend-LLM Architecture

| Component | Monthly Cost (10K users) | Notes |
|---|---|---|
| Cloudflare R2 | ~$5 | $0.015/GB + reads |
| Neon PostgreSQL | $0 | Free tier |
| Railway.app | ~$5 | Starter plan |
| Domain + SSL | ~$1 | Amortized |
| **TOTAL** | **~$11/month** | |
| **Cost per user** | **$0.001** | |

## ChatGPT Usage
- $0 to developer
- Users use their own ChatGPT subscription
- This is the key advantage of Zero-Backend-LLM

## Phase 2 Preview (Hybrid — Premium Users Only)
| Feature | Model | Tokens/Request | Cost/Request |
|---|---|---|---|
| Adaptive Path | Claude Sonnet | ~2,000 | $0.018 |
| LLM Assessment | Claude Sonnet | ~1,500 | $0.014 |

## Cost Comparison: Digital FTE vs Human Tutor
| | Human Tutor | Course Companion FTE |
|---|---|---|
| Monthly Cost | $2,000-$5,000 | $11-$41 |
| Students | 20-50 | Unlimited |
| Availability | 40 hrs/week | 168 hrs/week |
| Cost per session | $25-100 | $0.001 |

---

## Detailed R2 Cost Breakdown

Cloudflare R2 pricing (as of 2026):
- Storage: $0.015/GB/month
- Class A operations (write): $4.50 per million
- Class B operations (read): $0.36 per million

| Scenario | Storage | Monthly Reads | Monthly Cost |
|---|---|---|---|
| 1K users, 10 reads/user/day | 10 MB content | 300K reads | ~$0.11 |
| 10K users, 10 reads/user/day | 10 MB content | 3M reads | ~$1.08 |
| 100K users, 10 reads/user/day | 10 MB content | 30M reads | ~$10.80 |

Note: In-memory cache (5-min TTL) reduces R2 reads by ~80%, making 100K user scenario cost ~$2/month in R2 reads.

## Neon PostgreSQL Free Tier Limits

| Resource | Free Tier Limit | Usage at 10K Users |
|---|---|---|
| Compute hours | 191.9 hrs/month | ~20 hrs (auto-suspend) |
| Storage | 0.5 GB | ~50 MB estimated |
| Branches | 10 | 1 used |
| Projects | 1 | 1 used |

The free tier is sufficient through Phase 1 and likely through Phase 2. Upgrade to Pro ($19/month) when storage exceeds 0.5 GB.

## Phase 3 Cost Projection (Full Next.js + LLM Premium)

| Component | Monthly Cost (50K users) |
|---|---|
| Railway.app (Pro) | $20 |
| Neon PostgreSQL (Pro) | $19 |
| Cloudflare R2 | ~$15 |
| Claude API (premium users only, 10% of users) | ~$90 |
| Domain + CDN | ~$5 |
| **TOTAL** | **~$149/month** |
| **Revenue (10% premium × $9/mo)** | **$4,500/month** |
| **Gross margin** | **~97%** |
