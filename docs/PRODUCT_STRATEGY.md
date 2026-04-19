# Product Strategy

## Product Thesis

Digital Analysis should evolve from a developer-facing market-signal toolkit into a **market intelligence platform** with three monetizable surfaces:

1. analyst workspace
2. monitoring and alerts
3. structured intelligence API

---

## Target Customers

### 1. Independent researchers / power users
Need structured macro and market reasoning.

### 2. Media / content teams
Need evidence-backed market narratives quickly.

### 3. Investment / research teams
Need repeatable signal collection and reporting.

### 4. Enterprises / strategy teams
Need event probability tracking and risk dashboards.

---

## Product Tiers

### Free / Community
- limited providers
- manual analysis runs
- markdown output only

### Pro
- larger model quotas
- scheduled monitoring
- saved watchlists
- exportable reports

### Team / Enterprise
- private deployments
- local model option
- custom providers
- audit logs / provenance store
- API access / SLAs

---

## Differentiation

This product should not compete as a generic chatbot.
Its edge is:
- market-pricing-first reasoning
- multi-source evidence
- contradiction-aware analysis
- transparent, inspectable outputs
- configurable model stack

---

## Delivery Modes

### 1. Interactive Workspace
User asks a question and explores evidence.

### 2. Recurring Briefing
Daily/weekly reports on tracked topics.

### 3. Triggered Alerting
When a threshold changes:
- event probability jumps
- IV spikes
- yield curve shifts
- insider selling clusters

### 4. API / Embedded Intelligence
Deliver JSON outputs to other products.

---

## LLM / Local Model Product Policy

Recommended support matrix:

### Cloud API mode
Best for:
- strongest reasoning
- best UX quality
- premium product tier

### Hybrid mode
Best for:
- cost-sensitive production
- use cloud only for final synthesis

### Local model mode
Best for:
- enterprise privacy
- on-prem deployments
- predictable unit economics at scale

---

## Core Product Objects

- User
- Organization
- Workspace
- AnalysisSession
- Watchlist
- TopicMonitor
- ReportArtifact
- EvidenceBundle
- ModelRun

---

## Commercial Roadmap

### Stage 1
Developer + research tool

### Stage 2
Analyst workspace with saved sessions and reports

### Stage 3
Monitoring + alerting platform

### Stage 4
API + enterprise deployment + white-label offering

---

## Key Product Risks

1. Overusing LLMs where deterministic analysis is better
2. Hiding evidence behind polished prose
3. Expanding into unsupported problem types with weak priceability
4. Treating all data sources as equally reliable
5. Losing transparency while productizing

The product must stay evidence-first.
