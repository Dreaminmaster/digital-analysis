# Upgrade Plan

This document answers: **if we want to build a stronger version than the original market-signal library, what should be added?**

## Guiding Principle

Do not replace the original strengths. Extend them.

Keep:
- market-pricing-first philosophy
- provider-based data access
- low dependency bias where practical
- transparent structured outputs

Add:
- autonomous planning
- coded analysis engine
- multi-model routing
- product/service layer
- commercial packaging

---

## Phase 0 — Preserve Quality Baseline

Before large expansion, establish a quality baseline:
- standard Python package layout
- CI and test strategy
- style/lint/type policy
- snapshot testing discipline
- provider contract tests
- deterministic analysis test cases

Deliverables:
- `pyproject.toml`
- `tests/`
- provider fixtures
- analysis golden outputs

---

## Phase 1 — Domain Contracts

Add explicit contracts for:
- TaskSpec
- Signal
- Evidence
- AnalysisResult
- Scenario
- ReportArtifact
- ModelRequest / ModelResponse

Why:
- original code has strong provider objects, but no full end-to-end analysis contract
- contracts make planner, analysis, and reports composable

---

## Phase 2 — Planner Module

Add modules:
- question parser
- task classifier
- signal candidate registry
- planning policy
- fallback planner

Why:
- original signal routing lives mostly in prompt instructions
- a stronger system needs executable planning logic

Planner outputs should include:
- selected signals
- rejected signals and reasons
- fallback signals
- expected time horizon coverage
- evidence sufficiency target

---

## Phase 3 — Analysis Engine

Add modules:
- signal scoring engine
- contradiction detector
- horizon alignment engine
- evidence gap detector
- confidence engine
- scenario composer

Why:
- this is the main missing capability preventing true autonomous analysis

Expected behavior:
- if data is weak, request more evidence
- if signals disagree, explain disagreement instead of averaging blindly
- if horizons differ, separate short-, medium-, and long-term conclusions

---

## Phase 4 — Model Routing Layer

Add support for three operating modes:

### A. API-first mode
Use cloud LLMs for:
- question decomposition
- contradiction interpretation
- narrative generation

### B. Hybrid mode
Use deterministic planner + local/cloud model synthesis.

### C. Local/private mode
Use local models for:
- private enterprise deployment
- low-cost continuous report generation
- air-gapped or policy-sensitive environments

Add model router responsibilities:
- select model by task difficulty and privacy sensitivity
- select generation vs extraction vs classification mode
- fail over to alternate model/backend
- keep token/cost accounting

---

## Phase 5 — Product Service Layer

Add service-facing modules:
- analysis session service
- watchlist service
- scheduled monitoring service
- report delivery service
- evidence store / provenance store

Why:
- original project is a skill/toolkit; stronger version should support product workflows

---

## Phase 6 — Commercial Productization

Build three product surfaces:

### 1. Analyst Workspace
A chat + evidence + report UI for human analysts.

### 2. Monitoring Product
Track topics continuously:
- recession risk
- war risk
- sector bubble risk
- portfolio watchlist

### 3. API Product
Offer structured outputs via API:
- probability estimate
- evidence package
- market signal snapshot
- scenario matrix

---

## Modules To Add

Recommended package additions:

```text
src/digital_analysis/
  contracts/
    tasks.py
    signals.py
    evidence.py
    reports.py
    models.py

  planner/
    classifier.py
    priceability.py
    registry.py
    planner.py
    fallback.py

  analysis/
    scorer.py
    contradiction.py
    horizons.py
    confidence.py
    scenarios.py
    engine.py

  models/
    base.py
    router.py
    api_openai.py
    api_anthropic.py
    local_ollama.py
    local_llamacpp.py

  reports/
    builder.py
    markdown.py
    json_renderer.py

  product/
    sessions.py
    watchlists.py
    monitoring.py
    delivery.py
```

---

## How To Do True Autonomous Analysis

A stronger version must not stop at tool invocation. It should loop:

1. build initial task model
2. plan signals
3. fetch evidence
4. analyze sufficiency
5. detect contradiction or missing coverage
6. replan and fetch more if needed
7. only then synthesize final judgment

That loop is the core of autonomy.

---

## How To Keep Quality High While Expanding

1. Separate deterministic logic from LLM prose.
2. Test planners and analysis engines with frozen fixtures.
3. Require provenance on every output.
4. Version contracts carefully.
5. Keep model adapters replaceable.
6. Prefer graceful degradation when a provider fails.
