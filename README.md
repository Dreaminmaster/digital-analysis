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

This repo is now initialized as a **working enhanced scaffold**.

Implemented so far:

1. package layout and project configuration
2. architecture / upgrade / product strategy docs
3. baseline task contracts
4. task classifier + priceability checker + simple planner
5. execution layer (`http`, `gather`)
6. initial provider set:
   - Polymarket
   - U.S. Treasury
   - CNN Fear & Greed
   - CME FedWatch
7. baseline analysis engine and markdown report renderer
8. CLI skeleton
9. standard-library test suite passing

Near-term next priorities:

1. richer evidence contracts
2. contradiction engine and horizon grouping
3. provider expansion (Kalshi, Web, EDGAR, CFTC, Deribit, YFinance)
4. model adapters (cloud API + local model)
5. API/service layer and scheduled monitoring

## License

MIT
