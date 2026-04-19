# Architecture

## Positioning

Digital Analysis is a **stronger successor architecture** to the market-signal skill pattern.
It keeps the original principle — use market pricing as primary evidence — but upgrades the system from a provider toolkit into a **full autonomous analyst platform**.

## End-to-End Flow

```text
User Question
  -> Task Understanding
  -> Priceability Check
  -> Signal Planning
  -> Provider Execution
  -> Signal Normalization
  -> Analysis Engine
  -> Model-Assisted Interpretation
  -> Report Generation
  -> Product Delivery
```

---

## 1. Task Understanding Layer

Responsibilities:
- parse user question
- identify asset / event / geography / time horizon
- decide whether the question is directly or indirectly priceable
- classify task type: geopolitical, recession, bubble, asset allocation, options risk, etc.

Outputs:
- normalized task object
- target answer type: probability / directional judgment / scenario matrix / watchlist
- confidence requirements

---

## 2. Signal Planning Layer

Responsibilities:
- choose relevant direct and proxy signals
- score candidate signals by:
  - relevance
  - horizon match
  - information increment
  - expected data reliability
- produce execution plan with fallback sources

Upgrades beyond the original:
- planner should be executable code, not only prompt instructions
- planner should support iterative replanning when evidence is weak or contradictory

---

## 3. Provider Execution Layer

Responsibilities:
- parallel fetch
- retry / timeout / rate limiting
- cache / snapshots / replay
- provenance capture: source URL, timestamp, latency, status

Upgrades beyond the original:
- execution metadata becomes first-class
- support online mode, cached mode, offline replay mode
- provider health scoring and stale-data detection

---

## 4. Signal Normalization Layer

Responsibilities:
- convert raw provider responses into consistent domain objects
- define common signal interfaces:
  - probability signal
n  - price trend signal
  - volatility signal
  - curve signal
  - positioning signal
  - insider signal
  - macro background signal

Upgrades beyond the original:
- signals should expose both raw facts and semantic interpretation hints
- normalized schema should support cross-source comparison

---

## 5. Autonomous Analysis Engine

Responsibilities:
- translate market facts into interpretable evidence
- group signals by time horizon
- detect resonance and contradiction
- calculate weighted evidence summaries
- produce scenario trees and confidence bands

Core submodules:
- signal scoring engine
- contradiction engine
- horizon grouping engine
- confidence engine
- evidence gap detector

Upgrades beyond the original:
- move core reasoning from prompt-only to code-assisted analytical pipeline
- AI becomes a partner, not the only place where logic lives

---

## 6. Model Layer

Responsibilities:
- route requests to appropriate models
- support cloud APIs and local models
- allow hybrid workflows:
  - planner with fast model
  - synthesis with strong model
  - local privacy mode when needed

Backends:
- Cloud API adapters: OpenAI-compatible, Anthropic-style, vendor-specific
- Local model adapters: llama.cpp / Ollama / vLLM-style serving
- Deterministic non-LLM modules for tasks that do not require generation

Routing policy examples:
- cheap model for query decomposition
- strong model for contradiction interpretation
- local model for confidential enterprise data
- no model call when deterministic report assembly is enough

---

## 7. Report Layer

Responsibilities:
- generate structured outputs:
  - executive summary
  - evidence tables
  - contradiction analysis
  - scenario matrix
  - monitoring checklist
- render to:
  - markdown
  - JSON
  - API response schema
  - dashboard widgets

---

## 8. Product Layer

Responsibilities:
- expose the system as:
  - analyst chat workspace
  - API service
  - scheduled monitor
  - alert/report product
- add user/org/project concepts
- persist analyses, watchlists, and report history

Commercial surfaces:
- B2B analyst workspace
- API for quant/media/research teams
- portfolio/risk monitoring product
- white-label embedded market-intelligence layer

---

## 9. Quality Principles

1. Preserve transparency: every conclusion must link back to priced signals.
2. Preserve modularity: provider, planner, model, analysis, and report layers are separable.
3. Preserve auditability: every output should retain evidence provenance.
4. Upgrade autonomy carefully: automate routing and analysis, but never hide evidence.
5. Productize without losing rigor: commercial UX should simplify delivery, not reduce analytical quality.
