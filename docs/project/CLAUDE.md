# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Native MVP: Doctoral thesis project implementing an ecosystem for teaching-learning programming with generative AI. Features 6 AI agents enabling **process-based evaluation** (not product-based) and **N4-level cognitive traceability**.

**Architecture**: C4 Extended Model + Clean Architecture + Repository Pattern
**Stack**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic, React+TypeScript frontend

## Quick Start Commands

```bash
# Setup
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt
python scripts/init_database.py
cp .env.example .env

# Run
python scripts/run_api.py                    # API at http://localhost:8000
python examples/ejemplo_basico.py            # Verify backend works
cd frontEnd && npm install && npm run dev    # Frontend at http://localhost:3000

# Test
pytest tests/ -v --cov                       # All tests with coverage
pytest tests/test_agents.py -v               # Single file
pytest -m "unit" -v                          # By marker

# Docker
docker-compose up -d                         # Full stack
make dev                                     # Development shortcuts
```

## Architecture: The 6 AI Agents

| Agent | Purpose | File |
|-------|---------|------|
| **T-IA-Cog** | Cognitive Tutor (Socratic guidance) | `agents/tutor.py` |
| **E-IA-Proc** | Process Evaluator (not product) | `agents/evaluator.py` |
| **S-IA-X** | Professional Simulators (PO, SM, IT, IR, CX, DSO) | `agents/simulators.py` |
| **AR-IA** | Risk Analyst (5 dimensions) | `agents/risk_analyst.py` |
| **GOV-IA** | Governance (blocks total delegation) | `agents/governance.py` |
| **TC-N4** | N4 Traceability (cognitive path capture) | `agents/traceability.py` |

**Request Flow**: FastAPI → AIGateway → CRPE (classify) → GOV-IA (check) → Agent → TC-N4 (trace) → AR-IA (risks) → Response

## Critical Implementation Rules

### 1. Thread Safety (MUST FOLLOW)

All singletons use double-checked locking:
```python
_instance = None
_lock = threading.Lock()

def get_instance():
    global _instance
    if _instance is None:          # Fast path (no lock)
        with _lock:                 # Slow path (with lock)
            if _instance is None:
                _instance = create_instance()
    return _instance
```

**Affected files**: `llm/factory.py`, `core/cache.py`, `llm/openai_provider.py`

### 2. ORM vs Pydantic Field Mappings (CRITICAL)

| Pydantic | ORM | Reason |
|----------|-----|--------|
| `metadata` | `trace_metadata` | SQLAlchemy reserved |
| `timestamp` | `created_at` | BaseModel convention |
| Enum values | lowercase strings | DB storage |

```python
# ✅ CORRECT
trace.trace_metadata  # NOT trace.metadata
[t for t in traces if t.trace_level == "n4_cognitivo"]  # lowercase!
```

### 3. Required Fields (Common Validation Errors)

```python
# CognitiveTrace: ALWAYS include session_id
CognitiveTrace(session_id="...", student_id="...", ...)

# Risk: ALWAYS include dimension
Risk(dimension=RiskDimension.COGNITIVE, risk_type=..., ...)
```

### 4. LLM Provider Configuration

```bash
# .env file - NOT code!
LLM_PROVIDER=openai  # or mock, gemini
OPENAI_API_KEY=sk-proj-...

# MUST restart server after .env changes
```

## Key Directory Structure

```
src/ai_native_mvp/
├── api/                    # FastAPI REST layer
│   ├── main.py             # App + middleware setup
│   ├── deps.py             # Dependency injection
│   ├── routers/            # Endpoints (15+ routers)
│   └── monitoring/metrics.py  # Prometheus instrumentation
├── core/
│   ├── ai_gateway.py       # Central orchestrator (STATELESS)
│   ├── cognitive_engine.py # CRPE reasoning engine
│   └── cache.py            # LRU cache with TTL
├── agents/                 # 6 AI-Native submodels
├── models/                 # Pydantic schemas
├── llm/                    # Provider abstraction (mock, openai, gemini)
└── database/
    ├── models.py           # ORM models (14 tables)
    ├── repositories.py     # Repository pattern
    └── config.py           # DB connection + pooling
```

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `no such table: sessions` | `python scripts/init_database.py` |
| `ImportError: CognitiveState` | Import from `core.cognitive_engine`, not `models.trace` |
| `UnicodeEncodeError` (Windows) | Add UTF-8 wrapper at script top |
| Port 8000 in use | `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` |
| LLM still using Mock | Check `.env`, restart server |

## Testing Infrastructure

```bash
# Markers available
pytest -m "unit"        # Unit tests
pytest -m "integration" # Integration tests
pytest -m "cognitive"   # Cognitive engine
pytest -m "agents"      # Agent tests

# Coverage requirement: 70% minimum (pytest.ini)
```

**Key fixtures** in `tests/conftest.py`: `mock_llm_provider`, `sample_trace_*`, `sample_risk_*`

## Environment Variables

```bash
# Required for production
LLM_PROVIDER=openai|gemini|mock
OPENAI_API_KEY=sk-...           # If using OpenAI
GEMINI_API_KEY=AIza...          # If using Gemini (FREE!)
JWT_SECRET_KEY=<secure-random>
ENVIRONMENT=production          # Enables strict validation

# Optional
RATE_LIMIT_PER_MINUTE=60
LLM_CACHE_ENABLED=true
CACHE_SALT=<institutional-secret>
ALLOWED_ORIGINS=https://app.example.com
```

## Adding New Features

### New Agent
1. Create in `agents/`, follow existing pattern (stateless)
2. Integrate via `AIGateway` orchestration
3. Add tests in `tests/test_agents.py`
4. Include `dimension` field when creating Risk instances

### New API Endpoint
1. Create DTO schemas in `api/schemas/`
2. Create router in `api/routers/`
3. Use `Depends()` for dependency injection
4. Return `APIResponse[T]` for consistency
5. Register router in `api/main.py`

### New Database Model
1. Add ORM in `database/models.py` (inherit Base + BaseModel)
2. Add repository methods in `database/repositories.py`
3. Use `trace_metadata` not `metadata` (reserved word)

## Prometheus Metrics

Endpoint: `GET /metrics`

Key metrics:
- `ai_native_interactions_total` - By agent, status
- `ai_native_llm_call_duration_seconds` - LLM latency histogram
- `ai_native_cache_hit_rate_percent` - Cache efficiency
- `ai_native_risks_detected_total` - By type, level, dimension
- `ai_native_http_request_duration_seconds` - API latency

## Documentation Index

| Document | Purpose |
|----------|---------|
| README.md | Project overview, quick start |
| README_API.md | REST API comprehensive guide |
| DEPLOYMENT_DOCKER.md | Docker deployment |
| AUDITORIA_ARQUITECTURA_BACKEND_SENIOR.md | Architecture audit (8.2/10) |

## Language Conventions

- **Code**: English (variables, functions)
- **Docstrings**: Spanish (aligned with thesis)
- **Commits**: Spanish/English accepted
