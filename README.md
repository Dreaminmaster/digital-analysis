# Digital Analysis

A stronger, production-oriented evolution of the Digital Oracle idea.

This repository is designed as an **agent-native market intelligence system**:

- preserve the original project's strengths: low-dependency providers, structured market signals, transparent reasoning
- add missing layers: autonomous planning, signal scoring, contradiction analysis, LLM/model routing, report generation, and productization support

## Goals

1. **Replicate the quality bar** of the original market-signal collection approach
2. **Extend it into a true autonomous analyst architecture**
3. **Support multiple model backends**: cloud LLM APIs and local models
4. **Make it deployable as a product**: API service, analyst workspace, scheduled monitoring, and report delivery

## Architecture

```text
User Question
  -> Task Understanding
  -> Signal Planning
  -> Provider Execution
  -> Signal Normalization
  -> Autonomous Analysis Engine
  -> Model-Assisted Reasoning
  -> Report Generation
  -> Product/API/UI Delivery
```

See:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/UPGRADE_PLAN.md`](docs/UPGRADE_PLAN.md)
- [`docs/PRODUCT_STRATEGY.md`](docs/PRODUCT_STRATEGY.md)

## Repository Structure

```text
src/digital_analysis/
  config/             Runtime settings and model/provider config
  contracts/          Shared domain models
  providers/          External data source adapters
  planner/            Task understanding and signal planning
  execution/          Parallel execution, retries, caching, snapshots
  analysis/           Signal scoring, contradiction analysis, horizon grouping
  models/             LLM/API/local model adapters and routing
  reports/            Structured report builders and renderers
  product/            Product-facing service contracts and orchestration
  cli/                Command-line entrypoints
  tests/              Unit and integration tests
```

## Current Status

This repo is now a **working enhanced foundation** that preserves and extends the original market-signal approach.

Implemented so far:

1. package layout and project configuration
2. architecture / upgrade / product strategy docs
3. task contracts + evidence contracts
4. task classifier + priceability checker + simple planner
5. execution layer:
   - HTTP GET/POST
   - concurrent gather
   - snapshot record/replay
6. provider coverage now includes:
   - Polymarket
   - Kalshi
   - U.S. Treasury
   - CNN Fear & Greed
   - CME FedWatch
   - Web Search
   - SEC EDGAR
   - CoinGecko
   - BIS
   - CFTC
   - Deribit
   - World Bank
   - Yahoo Price
   - Stooq
   - YFinance Options
7. baseline autonomous analysis:
   - contradiction detection
   - horizon grouping
   - confidence scoring
   - scenario composition
8. report and synthesis layer:
   - markdown renderer
   - synthesis prompt builder
   - model-backed report synthesizer
9. model layer:
   - router
   - OpenAI-compatible adapter
   - Ollama adapter
10. orchestration and product-facing surface:
   - end-to-end orchestrator
   - analysis service
   - FastAPI app scaffold
   - CLI entrypoint
11. standard-library test suite passing

Near-term next priorities:

1. provider-driven evidence extraction from real fetched data
2. richer signal scoring and weighting
3. API deployment instructions and runtime wiring
4. scheduled monitoring / watchlists / persistence
5. stronger end-to-end examples using real providers and models

## License

MIT
