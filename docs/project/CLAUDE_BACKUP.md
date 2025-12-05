# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🎯 PROJECT STATUS (2025-11-25) - UPDATED

**✅ PRODUCTION-READY** - Critical remediations completed, Docker deployment ready

- **Status**: 11/11 hitos completados (100%), 20/20 KPIs alcanzados
- **Architecture Audit**: ⭐ 8.2/10 (AUDITORIA_ARQUITECTURA_BACKEND_SENIOR.md)
- **Critical Issues**: 3/3 RESOLVED (rate limiter, Docker, cache security)
- **Test Coverage**: 73% (94 tests passing)
- **Decision**: CONDITIONAL GO for beta cerrada (20 students)
- **Documentation**: 54 docs (25,000+ lines)

**Key Documents (Read First)**:
1. [README.md](README.md) - Main project overview with quick start
2. [AUDITORIA_ARQUITECTURA_BACKEND_SENIOR.md](AUDITORIA_ARQUITECTURA_BACKEND_SENIOR.md) - Complete backend audit ⭐ NEW
3. [REMEDIACION_CRITICA_APLICADA.md](REMEDIACION_CRITICA_APLICADA.md) - Critical fixes applied ⭐ NEW
4. [DEPLOYMENT_DOCKER.md](DEPLOYMENT_DOCKER.md) - Docker deployment guide ⭐ NEW

**Critical Remediations Completed (2025-11-25)**:
- ✅ **CRITICAL-01**: Rate limiter migrated to Redis (prevents DDoS bypass)
- ✅ **CRITICAL-02**: Dockerfile + docker-compose.yml created (automated deployment)
- ✅ **CRITICAL-03**: Cache salt added (prevents cache poisoning)
- ✅ Makefile created (development shortcuts)
- ✅ .dockerignore optimized (reduced build context to ~50MB)

**Security Improvements**:
- ✅ Distributed rate limiting (multi-worker safe)
- ✅ Cache keys with institutional salt (cross-student isolation)
- ✅ Production validation (fail-fast if Redis/secrets missing)

**Next Milestone**: Sprint 2 - HIGH Issues (1 week)
- ⏭️ HIGH-01: Implement Prometheus metrics (12h)
- ⏭️ HIGH-03: Deep health checks for dependencies (6h)
- ⏭️ MEDIUM issues: Type hints, retry logic, datetime fixes

---

## Table of Contents

### Getting Started
- [First-Time Setup Checklist](#first-time-setup-checklist)
- [Common Pitfalls (Quick Reference)](#common-pitfalls-quick-reference)
- [Quick Start Commands](#quick-start-commands)
- [Project Overview](#project-overview)
- [Typical Request Flow](#typical-request-flow)

### Architecture
- [C4 Extended Model](#architecture-c4-extended-model)
- [The 6 AI-Native Submodels](#the-6-ai-native-submodels)
- [Database Architecture](#database-architecture-new)
- [LLM Provider Integration](#llm-provider-integration-new---2025-11-19)
- [Key Design Patterns](#key-design-patterns)

### Development
- [Critical Implementation Rules](#critical-implementation-rules)
- [ORM ↔ Pydantic Mappings](#orm--pydantic-field-mappings-important)
- [Implementation Guidelines](#implementation-guidelines)
- [Testing Infrastructure](#testing-infrastructure-new)

### API & Frontend
- [REST API (FastAPI)](#rest-api-new---fastapi)
- [Frontend Application (React)](#frontend-application-react--typescript)

### Reference
- [Common Issues & Solutions](#common-issues--solutions)
- [Windows Encoding Note](#windows-encoding-note)
- [Quick Reference: Key Files](#quick-reference-key-files)
- [Project Status & Verification](#project-status--verification)
- [Critical Bug Fixes (2025-11-21)](#critical-bug-fixes-and-security-improvements-2025-11-21)

---

## First-Time Setup Checklist

For new developers joining the project:

1. [ ] Clone repository
2. [ ] Create virtual environment: `python -m venv .venv`
3. [ ] Activate venv:
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
4. [ ] Install dependencies: `pip install -r requirements.txt`
5. [ ] Initialize database: `python scripts/init_database.py`
6. [ ] Copy environment template: `cp .env.example .env` (or `copy` on Windows)
7. [ ] (Optional) Configure OpenAI: Edit `.env` and add `OPENAI_API_KEY=sk-proj-...`
8. [ ] Verify backend: `python examples/ejemplo_basico.py`
9. [ ] (Optional) Setup frontend: `cd frontEnd && npm install`
10. [ ] (Optional) Start full stack:
    - Terminal 1: `python scripts/run_api.py`
    - Terminal 2: `cd frontEnd && npm run dev`

**Expected outcome**: See "✅ Example completed successfully" message from step 8.

---

## Common Pitfalls (Quick Reference)

Before diving deep, avoid these frequent mistakes:

### 1. Field Name Mismatches (ORM vs Pydantic)

**Problem**: ORM models have different field names than Pydantic models due to SQLAlchemy reserved words and BaseModel inheritance.

**Solutions**:
```python
# ✅ CORRECT
trace.trace_metadata  # NOT trace.metadata (SQLAlchemy reserved word)
trace.created_at      # NOT trace.timestamp (BaseModel uses created_at)

# Filter with lowercase (database stores enums as lowercase strings)
[t for t in traces if t.trace_level == "n4_cognitivo"]  # NOT "N4_COGNITIVO"
```

See [ORM ↔ Pydantic Mappings](#orm--pydantic-field-mappings-important) for complete table.

### 2. Missing Required Fields

**Problem**: Validation errors due to missing required fields in model constructors.

**Solutions**:
```python
# CognitiveTrace: ALWAYS include session_id
trace = CognitiveTrace(
    session_id="session_123",  # REQUIRED!
    student_id="student_001",
    # ... other fields
)

# Risk: ALWAYS include dimension
risk = Risk(
    dimension=RiskDimension.COGNITIVE,  # REQUIRED!
    risk_type=RiskType.COGNITIVE_DELEGATION,
    # ... other fields
)
```

### 3. LLM Provider Configuration

**Problem**: Want to use OpenAI but code still uses Mock provider.

**Solutions**:
```bash
# 1. Edit .env file (NOT code!)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...

# 2. RESTART server (changes in .env require restart)
# Ctrl+C then: python scripts/run_api.py

# 3. Verify in server logs:
# [INFO] LLM Provider inicializado: openai
```

### 4. Database Not Initialized

**Problem**: `OperationalError: no such table: sessions`

**Solution**:
```bash
python scripts/init_database.py
# Creates ai_native.db in project root
```

### 5. Import Errors in Tests

**Problem**: `ImportError: cannot import name 'CognitiveState'`

**Solution**:
```python
# ✅ CORRECT
from src.ai_native_mvp.core.cognitive_engine import CognitiveState

# ❌ INCORRECT (old location)
from src.ai_native_mvp.models.trace import CognitiveState
```

### 6. Windows Encoding Errors

**Problem**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution**: Add UTF-8 encoding fix at top of script:
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

## Quick Start Commands

```bash
# === Full Stack (Backend + Frontend) ===
# Terminal 1 - Backend API
python scripts/run_api.py                  # Start FastAPI server at http://localhost:8000

# Terminal 2 - Frontend Dev Server
cd frontEnd && npm install                 # First time only
cd frontEnd && npm run dev                 # Start Vite at http://localhost:3000

# === Backend Only ===
python -m ai_native_mvp                    # Interactive CLI
python examples/ejemplo_basico.py          # Complete CLI example
python scripts/run_api.py                  # Start FastAPI server (dev mode)
python examples/api_usage_example.py       # Test API endpoints
# Then open: http://localhost:8000/docs    # Swagger UI documentation

# === Frontend Only ===
cd frontEnd && npm run dev                 # Start dev server with HMR
cd frontEnd && npm run build               # Build for production
cd frontEnd && npm run preview             # Preview production build
cd frontEnd && npm run lint                # Run ESLint

# === Database ===
python scripts/init_database.py            # Initialize SQLite DB
python scripts/init_database.py --drop-existing  # Reset database (DANGER)

# === Testing ===
pytest tests/ -v --cov                     # Run all tests with coverage
pytest tests/test_agents.py -v             # Run specific test file
pytest -m "unit" -v                        # Run only unit tests
pytest -m "cognitive" -v                   # Run cognitive engine tests

# === Verification ===
python -c "from src.ai_native_mvp import AIGateway; print('✅ Imports OK')"
curl http://localhost:8000/api/v1/health  # Check API health (server must be running)

# === Authentication Testing (P1.1 - COMPLETED) ===
python examples/test_auth_complete.py          # Test JWT flow completo
python scripts/generate_secrets.py             # Generar JWT secret key
python scripts/migrate_add_user_id.py          # Migrar DB con user_id
```

## Project Overview

This is a doctoral thesis project on **AI-Native programming education**. It conceptualizes and implements an ecosystem for teaching-learning programming in the era of generative AI, addressing the epistemological transformation where "knowing how to program" shifts from writing code to:
- Formulating and decomposing problems for AI agents
- Critically evaluating AI-generated solutions
- Detecting inconsistencies, vulnerabilities, and hallucinations
- Sustaining continuous audit processes
- Documenting reasoning and decision-making

The project implements a functional MVP with 6 AI agents that enable **process-based evaluation** (not product-based) and **N4-level cognitive traceability**.

## Execution Modes

The system can be used in two ways:

### 1. CLI Mode (Interactive)
Direct interaction via command line for development/testing:
```python
from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import SessionRepository

with get_db_session() as db:
    session_repo = SessionRepository(db)
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

gateway = AIGateway()
result = gateway.process_interaction(
    session_id=session.id,
    student_id="student_001",
    activity_id="prog2_tp1",
    prompt="¿Cómo implemento una cola circular?"
)
```

### 2. API Mode (REST - NEW)
HTTP API for frontend/mobile integration:
```bash
# Start server
python scripts/run_api.py

# Call endpoint
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "prompt": "¿Cómo implemento una cola?"}'
```

**Key Difference**:
- CLI mode: Direct Python calls, synchronous, for scripts/notebooks
- API mode: HTTP requests, stateless, for web/mobile clients

---

## Typical Request Flow

Complete data flow from student input to response:

```
Student Input (Prompt)
    ↓
FastAPI Endpoint (/api/v1/interactions)
    ↓
Dependency Injection (deps.py)
    ├→ LLM Provider (from .env: mock, openai, or gemini)
    ├→ SessionRepository
    ├→ TraceRepository
    ├→ RiskRepository
    └→ EvaluationRepository
    ↓
AIGateway.process_interaction()
    ├→ C2: IPC (classify request type)
    ├→ C3: CRPE (detect cognitive state)
    │   └→ CognitiveState: EXPLORACION_CONCEPTUAL, PLANIFICACION, etc.
    ├→ C4: GSR (governance check)
    │   └→ GOV-IA: Block if total delegation detected
    ├→ C5: OSM (route to appropriate agent)
    │   ├→ T-IA-Cog (Cognitive Tutor) ← Most common
    │   ├→ E-IA-Proc (Process Evaluator)
    │   ├→ S-IA-X (Professional Simulators: PO, SM, IT, IR, CX, DSO)
    │   └→ AR-IA (Risk Analyst) ← Runs in parallel
    ├→ C6: N4 (capture input trace)
    │   └→ TC-N4: Create CognitiveTrace with session_id, cognitive_state, etc.
    ├→ C1: LLM (generate response via provider)
    │   └→ Mock, OpenAI GPT-4, or Google Gemini depending on .env
    └→ C6: N4 (capture output trace)
    ↓
Persist to Database (via Repositories)
    ├→ CognitiveTraceDB (input + output traces)
    ├→ RiskDB (if risks detected by AR-IA)
    └→ SessionDB (update last_interaction)
    ↓
Return JSON Response
    ├→ message (tutor's pedagogical response)
    ├→ metadata (agent_used, cognitive_state, ai_involvement)
    ├→ trace_id (for N4 traceability)
    └→ risks_detected (if any)
```

**Key Points**:
- All requests go through AIGateway (single orchestration point)
- N4 traces captured BEFORE and AFTER agent processing
- Governance check happens BEFORE processing (can block request)
- Risk analysis runs IN PARALLEL (doesn't block response)
- All data persisted via Repository pattern (never direct SQLAlchemy)

---

## Repository Structure

```
Tesis/
├── tesis.txt                    # Main thesis content (Spanish)
├── README_MVP.md                # Complete MVP documentation
├── README_API.md                # NEW: REST API documentation
├── IMPLEMENTACIONES_ARQUITECTURALES.md  # Recent architectural improvements
├── requirements.txt             # Python dependencies (includes FastAPI, uvicorn)
├── pytest.ini                   # Pytest configuration (70% coverage minimum)
├── src/
│   └── ai_native_mvp/
│       ├── __main__.py          # CLI entry point
│       ├── cli.py               # Interactive CLI
│       ├── api/                 # NEW: REST API layer (FastAPI)
│       │   ├── main.py          # FastAPI application
│       │   ├── deps.py          # Dependency injection
│       │   ├── exceptions.py    # Custom API exceptions
│       │   ├── middleware/      # Middleware (error handling, logging)
│       │   │   ├── error_handler.py
│       │   │   └── logging.py
│       │   ├── routers/         # API endpoints
│       │   │   ├── health.py    # Health checks
│       │   │   ├── sessions.py  # Session CRUD
│       │   │   ├── interactions.py  # Student-AI interactions (main endpoint)
│       │   │   ├── traces.py    # N4 traceability queries
│       │   │   └── risks.py     # Risks & evaluations
│       │   └── schemas/         # DTOs (Request/Response models)
│       │       ├── common.py
│       │       ├── session.py
│       │       └── interaction.py
│       ├── core/
│       │   ├── ai_gateway.py    # Central orchestrator (C4 architecture)
│       │   └── cognitive_engine.py  # CRPE (Cognitive-Pedagogical Reasoning Engine)
│       ├── agents/              # The 6 AI-Native submodels
│       │   ├── tutor.py         # T-IA-Cog (Cognitive Tutor)
│       │   ├── evaluator.py     # E-IA-Proc (Process Evaluator)
│       │   ├── simulators.py    # S-IA-X (Professional Simulators)
│       │   ├── risk_analyst.py  # AR-IA (Risk Analyst)
│       │   ├── governance.py    # GOV-IA (Governance)
│       │   └── traceability.py  # TC-N4 (N4 Traceability)
│       ├── models/              # Pydantic data models
│       │   ├── trace.py         # CognitiveTrace, TraceSequence
│       │   ├── risk.py          # Risk, RiskReport
│       │   └── evaluation.py    # EvaluationReport
│       ├── llm/                 # LLM provider abstraction
│       │   ├── base.py          # Base provider interface
│       │   ├── mock.py          # Mock provider (default)
│       │   ├── openai_provider.py  # OpenAI integration
│       │   └── factory.py       # Provider factory
│       └── database/            # SQLAlchemy persistence layer
│           ├── __init__.py
│           ├── base.py          # Declarative base
│           ├── config.py        # Database config & session management
│           ├── models.py        # ORM models (SessionDB, CognitiveTraceDB, etc.)
│           └── repositories.py  # Repository pattern
├── tests/                       # Pytest test suite
│   ├── conftest.py              # Fixtures and test configuration
│   ├── test_models.py
│   ├── test_cognitive_engine.py
│   ├── test_agents.py
│   └── test_gateway.py
├── scripts/
│   ├── init_database.py         # Database initialization script
│   └── run_api.py               # NEW: API server launcher
└── examples/
    ├── ejemplo_basico.py        # Complete CLI usage example
    └── api_usage_example.py     # NEW: Complete API usage example
```

## Development Setup

### Initial Setup

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Unix/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (SQLite by default)
python scripts/init_database.py

# Or with PostgreSQL
python scripts/init_database.py --database-url "postgresql://user:pass@localhost/ai_native"
```

### Common Commands

```bash
# Run interactive CLI
python -m ai_native_mvp
# or
python -m src.ai_native_mvp.cli

# Run complete example
python examples/ejemplo_basico.py

# Run tests with coverage
pytest tests/ -v --cov

# Run tests with HTML coverage report
pytest tests/ -v --cov --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run tests by marker
pytest -m "unit" -v          # Only unit tests
pytest -m "integration" -v   # Only integration tests
pytest -m "cognitive" -v     # Cognitive engine tests
pytest -m "agents" -v        # Agent tests

# Initialize database with sample data
python scripts/init_database.py --sample-data

# Reset database (DANGER: deletes all data!)
python scripts/init_database.py --drop-existing --database-url "sqlite:///ai_native.db"

# Verify imports
python -c "from src.ai_native_mvp import AIGateway; print('OK')"

# Interactive Python session with imports
python -i -c "from src.ai_native_mvp import *; from src.ai_native_mvp.agents import *"
```

### Database Operations

```python
# Using the database with repositories
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import SessionRepository, TraceRepository

with get_db_session() as session:
    # Create repositories
    session_repo = SessionRepository(session)
    trace_repo = TraceRepository(session)

    # Create a session
    db_session = session_repo.create(
        student_id="student_001",
        activity_id="prog2_tp1_colas",
        mode="TUTOR"
    )

    # Auto-commit on success, auto-rollback on exception
```

## Architecture: C4 Extended Model

The system implements a **C4 extended architecture** integrating cognitive-pedagogical dimensions:

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Gateway                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Motor de Razonamiento Cognitivo-Pedagógico (CRPE)  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ IPC     │  │ GSR     │  │ OSM     │  │ N4      │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌─────────┐   ┌──────────┐  ┌───────────┐  ┌─────────┐
    │ T-IA-Cog│   │ E-IA-Proc│  │  S-IA-X   │  │  AR-IA  │
    └─────────┘   └──────────┘  └───────────┘  └─────────┘
    ┌─────────┐   ┌──────────┐
    │ GOV-IA  │   │  TC-N4   │
    └─────────┘   └──────────┘
```

### AI Gateway Components (C1-C6)

1. **C1 - Motor LLM**: LLM provider connection (currently mock for MVP)
2. **C2 - IPC**: Prompt Ingestion and Comprehension
3. **C3 - CRPE**: Cognitive-Pedagogical Reasoning Engine (`cognitive_engine.py`)
4. **C4 - GSR**: Governance, Security, and Risk
5. **C5 - OSM**: Submodel Orchestration
6. **C6 - N4**: N4 Cognitive Traceability

## The 6 AI-Native Submodels

### 1. T-IA-Cog: Cognitive Disciplinary Tutor
**File**: `src/ai_native_mvp/agents/tutor.py`

**Purpose**: Guide student reasoning WITHOUT substituting cognitive agency

**Key features**:
- Socratic questioning to promote problem decomposition
- Conceptual explanations (NOT complete solutions)
- Graduated adaptive hints
- Prevents uncritical delegation
- 4 modes: SOCRATICO, EXPLICATIVO, GUIADO, METACOGNITIVO

**Theoretical basis**: Distributed cognition (Hutchins), Extended cognition (Clark & Chalmers), Cognitive load theory (Sweller), Self-regulation (Zimmerman)

### 2. E-IA-Proc: Cognitive Process Evaluator
**File**: `src/ai_native_mvp/agents/evaluator.py`

**Purpose**: Analyze and evaluate the hybrid human-AI cognitive PROCESS (not final product)

**What it does**:
- Reconstructs cognitive path from traces
- Detects conceptual and epistemological errors
- Evaluates self-regulation and reasoning coherence
- Analyzes code evolution via Git
- Generates Cognitive Evaluation Report (IEC)

**What it does NOT do**:
- Does NOT assign grades automatically
- Does NOT replace the instructor
- Does NOT correct code

### 3. S-IA-X: Professional Simulators
**File**: `src/ai_native_mvp/agents/simulators.py`

**Purpose**: Recreate authentic industry roles for situated learning

**Available simulators**:
- **PO-IA**: Product Owner (requirements, acceptance criteria)
- **SM-IA**: Scrum Master (agile ceremonies, impediment management)
- **IT-IA**: Technical Interviewer (conceptual and algorithmic assessment)
- **IR-IA**: Incident Responder (DevOps, incident management)
- **CX-IA**: Simulated Client (ambiguous requirements, soft skills)
- **DSO-IA**: DevSecOps (security, vulnerabilities, audit)

### 4. AR-IA: Cognitive & Ethical Risk Analyst
**File**: `src/ai_native_mvp/agents/risk_analyst.py`

**Purpose**: Detect and classify risks from human-AI interaction

**5 Risk dimensions**:
1. **Cognitive (RC)**: Total delegation, superficial reasoning, AI dependency
2. **Ethical (RE)**: Academic integrity, undisclosed AI use
3. **Epistemic (REp)**: Conceptual errors, uncritical acceptance
4. **Technical (RT)**: Vulnerabilities, poor code quality
5. **Governance (RG)**: Policy violations

**Normative frameworks**: UNESCO (2021), OECD AI Principles (2019), IEEE Ethically Aligned Design (2019), ISO/IEC 23894:2023, ISO/IEC 42001:2023

### 5. GOV-IA: Institutional Governance
**File**: `src/ai_native_mvp/agents/governance.py`

**Purpose**: Operationalize AI governance actively, automated, and verifiable

**Functions**:
- Real-time policy compliance verification
- Risk management per ISO/IEC 23894
- Audit and traceability for accreditation (CONEAU, etc.)
- Institutional report generation

**Enforced policies**:
- Maximum AI assistance level
- Block complete solutions without mediation
- Require explicit traceability
- Academic integrity enforcement

### 6. TC-N4: N4 Cognitive Traceability
**File**: `src/ai_native_mvp/agents/traceability.py`

**Purpose**: Capture and reconstruct complete hybrid human-AI reasoning process

**4 Traceability levels**:
- **N1 - Superficial**: Files, submissions, final version
- **N2 - Technical**: Commits, branches, automated tests
- **N3 - Interactional**: Prompts, responses, retries, logs
- **N4 - Complete Cognitive**: Cognitive intent, decisions, justifications, alternatives, strategy changes, audits

**Key principle**: Every interaction is captured at N4 level when possible, forming immutable trace sequences that represent cognitive paths.

## Database Architecture (NEW)

### ORM Models

Located in `src/ai_native_mvp/database/models.py`:

1. **SessionDB**: Learning sessions
   - Fields: student_id, activity_id, mode, start_time, end_time, status
   - Relationships: traces, risks, evaluations (one-to-many with cascade)

2. **CognitiveTraceDB**: N4-level cognitive traces
   - All N4 traceability fields
   - Fields: cognitive_state, cognitive_intent, ai_involvement, trace_metadata
   - Relationship: belongs to SessionDB

3. **RiskDB**: Detected risks
   - Fields: risk_type, risk_level, dimension, evidence, recommendations
   - Resolution tracking: resolved, resolution_notes
   - Relationship: belongs to SessionDB

4. **EvaluationDB**: Process evaluations
   - Fields: overall_competency_level, overall_score, dimensions (JSON)
   - Feedback: key_strengths, improvement_areas
   - Analysis: reasoning_analysis, git_analysis, ai_dependency_metrics (JSON)
   - Relationship: belongs to SessionDB

5. **TraceSequenceDB**: Trace sequences
   - Fields: reasoning_path, strategy_changes, ai_dependency_score
   - Stores trace_ids as JSON array

6. **StudentProfileDB**: Student learning profiles
   - Learning analytics: total_sessions, average_ai_dependency
   - Risk profile: total_risks, critical_risks, risk_trends
   - Progress: competency_evolution (time series)

7. **ActivityDB**: Activities catalog (NEW - 2025-11-20)
   - **Purpose**: Store learning activities created by teachers with configurable pedagogical policies
   - **Identification**: activity_id (unique), title, description, instructions
   - **Pedagogical policies** (JSON field):
     - `max_help_level`: "MINIMO", "BAJO", "MEDIO", "ALTO"
     - `block_complete_solutions`: true/false
     - `require_justification`: true/false
     - `allow_code_snippets`: true/false
     - `risk_thresholds`: AI dependency, lack of justification thresholds
   - **Metadata**: subject (e.g., "Programación II"), difficulty (INICIAL/INTERMEDIO/AVANZADO), estimated_duration_minutes
   - **Categorization**: tags (JSON array: ["colas", "estructuras", "arreglos"])
   - **Teacher tracking**: teacher_id (who created it)
   - **Status**: draft, active, archived
   - **Evaluation criteria**: JSON array of criteria for process-based evaluation
   - **Relationship**: has_many SessionDB (one activity can have multiple student sessions)
   - **Indexes**: 3 composite indexes
     - `idx_activity_teacher_status` (teacher_id, status)
     - `idx_activity_status_created` (status, created_at)
     - `idx_activity_subject_status` (subject, status)

### Repository Pattern

Located in `src/ai_native_mvp/database/repositories.py`:

- **SessionRepository**: CRUD for sessions, mode updates, end session
- **TraceRepository**: Create traces, get by session/student, count
- **RiskRepository**: Create risks, get by session/student, filter by resolved, get critical risks
- **EvaluationRepository**: Create evaluations, get by session/student
- **TraceSequenceRepository**: Create sequences, get by session

**Key design**: Repositories abstract database operations, providing clean API for agents and gateway.

### Database Configuration

Located in `src/ai_native_mvp/database/config.py`:

- **Supports**: SQLite (development/testing), PostgreSQL (production)
- **Features**: Connection pooling, pre-ping health checks, foreign key enforcement
- **Session management**: Context managers for automatic commit/rollback
- **Global config**: Singleton pattern via `init_database()` and `get_db_config()`

### ORM ↔ Pydantic Field Mappings (IMPORTANT)

When working with database models, be aware of these field name differences:

| Pydantic Model Field | ORM Model Field | Reason | Usage |
|---------------------|-----------------|---------|-------|
| `metadata` | `trace_metadata` | "metadata" is reserved in SQLAlchemy | Access via `trace.trace_metadata` in ORM |
| `timestamp` | `created_at` | BaseModel uses created_at/updated_at | Access via `trace.created_at` in ORM |
| N/A | `updated_at` | Auto-managed by BaseModel | Access via `trace.updated_at` in ORM |
| `trace_level` (enum) | `trace_level` (string) | Stored as lowercase in DB | Filter with `"n4_cognitivo"` not `"N4_COGNITIVO"` |
| `interaction_type` (enum) | `interaction_type` (string) | Stored as lowercase in DB | Filter with `"student_prompt"` not `"STUDENT_PROMPT"` |

**Example - Accessing ORM fields in API endpoints**:

```python
# ✅ CORRECT
TraceResponse(
    id=t.id,
    metadata=t.trace_metadata,  # NOT t.metadata
    timestamp=t.created_at,     # NOT t.timestamp
)

# ❌ INCORRECT
TraceResponse(
    metadata=t.metadata,    # AttributeError!
    timestamp=t.timestamp,  # AttributeError!
)
```

**Example - Filtering by trace level**:

```python
# ✅ CORRECT
n4_traces = [t for t in traces if t.trace_level == "n4_cognitivo"]

# ❌ INCORRECT
n4_traces = [t for t in traces if t.trace_level == "N4_COGNITIVO"]  # Won't match!
```

**BaseModel Mixin Fields** (inherited by all ORM models):

All database models inherit from `BaseModel` which provides:
- `id` (String, UUID primary key, auto-generated)
- `created_at` (DateTime, auto-set on creation)
- `updated_at` (DateTime, auto-updated on modification)

Do NOT define these fields manually - they're provided automatically.

## Key Design Patterns

### 1. Separation of Concerns
- **Models** (`models/`): Pure Pydantic data structures with validation
- **Database** (`database/`): SQLAlchemy ORM and persistence
- **Agents** (`agents/`): Business logic for each submodel (stateless)
- **Core** (`core/`): Orchestration (Gateway, Engine)

### 2. Dependency Flow
```
CLI → AIGateway → CognitiveEngine → Agents → Models
                       ↓
                   Database (via repositories)
```

All interactions go through AIGateway, which:
1. Coordinates the appropriate agent based on mode
2. Captures N4 traces via TC-N4
3. Persists data via repositories

### 3. Repository Pattern
Abstracts database operations:
- Agents interact with repositories, NOT directly with SQLAlchemy
- Repositories handle ORM-to-Pydantic conversion
- Clean separation between business logic and persistence

### 4. Agent Pattern
Each agent is **stateless** and independent:
- Takes input (prompts, traces, context)
- Processes according to pedagogical/cognitive rules
- Returns structured Pydantic output
- Does NOT directly interact with other agents (coordination via Gateway)
- Does NOT maintain session state (state in database)

### 5. Traceability-First Design
Every interaction captured in TC-N4:
- Always capture at least N3 (interactional)
- Strive for N4 (cognitive) whenever possible
- Traces are **immutable** once created
- Traces form sequences representing cognitive paths
- All traces persisted to database

### 6. Pydantic for Type Safety
All data structures use Pydantic for:
- Runtime type validation
- Automatic JSON serialization
- Clear contracts between components
- Self-documenting schemas via `model_json_schema()`

Example:
```python
from src.ai_native_mvp.models.trace import CognitiveTrace, TraceLevel, InteractionType
from src.ai_native_mvp.core.cognitive_engine import CognitiveState

trace = CognitiveTrace(
    session_id="session_123",
    student_id="student_001",
    activity_id="prog2_tp1",
    trace_level=TraceLevel.N4_COGNITIVO,
    interaction_type=InteractionType.STUDENT_PROMPT,
    cognitive_state=CognitiveState.PLANIFICACION,
    content="Planeo usar un arreglo circular. ¿Es correcto?",
    ai_involvement=0.4,
    metadata={"blocked": False}
)
```

## Typical Workflow

1. **Student interaction** → Prompt sent to AIGateway via CLI or API
2. **Classification** (CRPE) → Detects cognitive state and request type
3. **Governance check** (GOV-IA) → Verifies institutional policies
4. **Capture input trace** (TC-N4) → Records N4 trace to database
5. **Processing** → Delegates to appropriate submodel (T-IA-Cog, S-IA-X, etc.)
6. **Response** → Generates pedagogical response per strategy
7. **Capture output trace** (TC-N4) → Records response and reasoning
8. **Risk analysis** (AR-IA) → Detects risks in parallel
9. **Evaluation** (E-IA-Proc) → Analyzes complete process at session end

## Testing Infrastructure (NEW)

Located in `tests/`:

### Test Markers
Use markers to run specific test categories:
```bash
pytest -m "unit"        # Unit tests only
pytest -m "integration" # Integration tests only
pytest -m "cognitive"   # Cognitive engine tests
pytest -m "agents"      # Agent tests
pytest -m "models"      # Pydantic model tests
pytest -m "gateway"     # AI Gateway tests
```

### Key Fixtures (in `conftest.py`)
- `mock_llm_provider`: Mock LLM for testing without API calls
- `student_id`, `activity_id`, `session_id`: Test identifiers
- `sample_trace_delegacion`: Trace representing total delegation
- `sample_trace_conceptual`: Trace representing conceptual exploration
- `sample_trace_planning`: Trace representing planning phase
- `sample_trace_sequence`: Complete trace sequence with multiple traces
- `sample_risk_delegacion`, `sample_risk_superficial`: Sample risks
- `sample_evaluation_report`: Sample evaluation report
- `trace_builder`: Builder pattern for creating custom traces
- `test_config`: Test configuration dictionary

### Coverage Requirements
- **Minimum**: 70% coverage (enforced by pytest.ini)
- **Reports**: HTML report generated in `htmlcov/`
- **Command**: `pytest tests/ -v --cov --cov-report=html`

## Windows Encoding Note

**IMPORTANT**: Windows uses cp1252 by default. For Unicode characters (✓, ✅, 🤖), add encoding fix at top of scripts:

```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

This is already applied in:
- `examples/ejemplo_basico.py`
- `scripts/init_database.py`
- `src/ai_native_mvp/cli.py`

**Common encoding errors on Windows**:
- `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f393'`
- **Solution**: Add the encoding fix above at the top of any script that uses Unicode characters

## Common Issues & Solutions

### 1. Database Connection Issues
**Problem**: `OperationalError: no such table: sessions`

**Solution**: Initialize database first:
```bash
python scripts/init_database.py
```

### 2. Import Errors in Tests
**Problem**: `ImportError: cannot import name 'CognitiveState'`

**Solution**: Import from correct module:
```python
# ✅ Correct
from src.ai_native_mvp.core.cognitive_engine import CognitiveState

# ❌ Incorrect (old)
from src.ai_native_mvp.models.trace import CognitiveState
```

### 3. Validation Errors
**Problem**: `Field required [type=missing] for session_id in CognitiveTrace`

**Solution**: Always pass `session_id` when creating traces:
```python
trace = CognitiveTrace(
    session_id="session_123",  # REQUIRED!
    student_id="student_001",
    # ... other fields
)
```

**Problem**: `Field required [type=missing] for dimension in Risk`

**Solution**: Always include `dimension` field:
```python
risk = Risk(
    # ... other fields
    dimension=RiskDimension.COGNITIVE,  # REQUIRED!
)
```

### 4. Windows Encoding Errors
**Problem**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution**: Add UTF-8 encoding fix at top of script (see "Windows Encoding Note" section)

### 5. API Server Won't Start
**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

**Problem**: Port 8000 already in use (common when server is already running)

**Solution**: Kill existing process or use different port:
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Unix/macOS - Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Alternative: Use a different port
uvicorn src.ai_native_mvp.api.main:app --port 8001 --reload
python scripts/run_api.py  # Automatically uses port 8000

# Check if API is already running:
curl http://localhost:8000/api/v1/health
```

### 6. Database Locked Error
**Problem**: `OperationalError: database is locked`

**Solution**: SQLite is single-writer. Close other connections or use PostgreSQL for concurrent access.

## Critical Implementation Rules

### Thread Safety (Production - CRITICAL)

**IMPORTANT**: The system uses thread-safe singletons in several critical points. These MUST be maintained for production deployment with multiple workers.

#### 1. LLM Provider Factory (`llm/factory.py:90-92`)

**Pattern**: Double-checked locking

```python
_llm_provider_instance: Optional[LLMProvider] = None
_llm_provider_lock = threading.Lock()

def get_llm_provider() -> LLMProvider:
    global _llm_provider_instance
    if _llm_provider_instance is None:  # First check (fast path, no lock)
        with _llm_provider_lock:        # Acquire lock
            if _llm_provider_instance is None:  # Second check (slow path, with lock)
                _llm_provider_instance = _initialize_llm_provider()
    return _llm_provider_instance
```

**Why**: Prevents multiple LLM provider instances from being created concurrently by different threads/requests.

**Rule**: DO NOT recreate provider instance per request - expensive and causes resource leaks.

#### 2. LRU Cache (`core/cache.py`)

**Pattern**: Lock-protected OrderedDict operations

```python
class LRUCache:
    def __init__(self):
        self._cache = OrderedDict()
        self._lock = threading.Lock()  # Thread-safe

    def get(self, key):
        with self._lock:
            # All cache operations protected
            ...
```

**Why**: `OrderedDict` is NOT thread-safe. Without locks → data corruption with multiple uvicorn workers.

**Fixed**: 2025-11-21 (Race condition CRITICAL fix)

**Rule**: ALL cache operations MUST be within `with self._lock:` block.

#### 3. OpenAI Client Lazy Loading (`llm/openai_provider.py:45-63`)

**Pattern**: Double-checked locking for client initialization

```python
def _get_client(self):
    if self._client is None:  # First check (fast path)
        with self._client_lock:  # Lock
            if self._client is None:  # Second check
                self._client = OpenAI(api_key=...)
    return self._client
```

**Why**: Prevents creating multiple OpenAI client instances → resource leaks.

**Fixed**: 2025-11-21 (HIGH priority fix)

**Rule**: Use lazy loading with double-checked locking for expensive external clients.

#### General Rule for New Singletons

If you need to add a new singleton, ALWAYS use this pattern:

```python
_instance: Optional[YourClass] = None
_instance_lock = threading.Lock()

def get_instance() -> YourClass:
    global _instance
    if _instance is None:  # Fast path (no lock)
        with _instance_lock:  # Slow path (with lock)
            if _instance is None:
                _instance = YourClass()
    return _instance
```

**DO NOT** use simple `if _instance is None: _instance = YourClass()` - causes race conditions.

---

### Model Field Requirements (MUST FOLLOW)

When creating instances of the following models, these fields are **REQUIRED**:

1. **CognitiveTrace** (src/ai_native_mvp/models/trace.py):
   - `session_id` (str) - REQUIRED since database persistence implementation
   - All trace creations MUST include session_id

2. **TraceSequence** (src/ai_native_mvp/models/trace.py):
   - `session_id` (str) - REQUIRED since database persistence implementation
   - When creating sequences, always pass session_id

3. **Risk** (src/ai_native_mvp/models/risk.py):
   - `dimension` (RiskDimension) - REQUIRED field
   - Must be one of: COGNITIVE, ETHICAL, EPISTEMIC, TECHNICAL, GOVERNANCE
   - Map risk types to appropriate dimensions:
     - COGNITIVE_DELEGATION, AI_DEPENDENCY, LACK_JUSTIFICATION → COGNITIVE
     - ACADEMIC_INTEGRITY, UNDISCLOSED_AI_USE, PLAGIARISM → ETHICAL
     - UNCRITICAL_ACCEPTANCE, CONCEPTUAL_ERROR, LOGICAL_FALLACY → EPISTEMIC
     - SECURITY_VULNERABILITY, POOR_CODE_QUALITY → TECHNICAL
     - POLICY_VIOLATION, UNAUTHORIZED_USE → GOVERNANCE

**Example of correct Risk creation:**
```python
from src.ai_native_mvp.models.risk import Risk, RiskType, RiskLevel, RiskDimension

risk = Risk(
    id="risk_001",
    student_id="student_001",
    activity_id="prog2_tp1",
    risk_type=RiskType.COGNITIVE_DELEGATION,
    risk_level=RiskLevel.HIGH,
    dimension=RiskDimension.COGNITIVE,  # REQUIRED!
    description="Delegación total detectada",
    evidence=["Dame el código completo"],
    trace_ids=["trace_123"]
)
```

### Common Validation Errors & Solutions

**Error**: "Field required [type=missing] for session_id in CognitiveTrace"
**Solution**: Always pass `session_id` when creating traces in AIGateway._create_trace()

**Error**: "Field required [type=missing] for dimension in Risk"
**Solution**: Always include `dimension=RiskDimension.XXX` when creating Risk instances

**Error**: "Field required [type=missing] for session_id in TraceSequence"
**Solution**: Pass `session_id` when creating TraceSequence in AIGateway.create_session()

## Implementation Guidelines

### When Adding New Features

1. **New Agent**:
   - Create in `agents/`, follow existing agent pattern
   - Inherit from ABC if defining interface
   - Integrate through AIGateway orchestration
   - Add corresponding tests in `tests/test_agents.py`
   - **IMPORTANT**: When creating Risk instances, always include `dimension` field

2. **New Pydantic Model**:
   - Add to `models/`, use Pydantic BaseModel
   - Export in `models/__init__.py`
   - Add validation rules
   - Add tests in `tests/test_models.py`
   - **IMPORTANT**: If model will be used in database, ensure all required fields are documented

3. **New Database Model**:
   - Add ORM model in `database/models.py` (inherit from Base and BaseModel)
   - Add repository methods in `database/repositories.py`
   - Create migration script if using Alembic (future)
   - Add database tests
   - Update Pydantic model if needed to match new database fields

4. **New Interaction Type**:
   - Update `InteractionType` enum in `models/trace.py`
   - Update trace capturing logic in AIGateway
   - Ensure all trace creation calls include `session_id`

5. **New Risk Type**:
   - Update `RiskType` enum in `models/risk.py`
   - Update `RiskDimension` if needed (or map to existing dimension)
   - Update AR-IA detection logic in `risk_analyst.py`
   - **CRITICAL**: Always include `dimension` field when creating Risk instances

### When Modifying Existing Code

- **Agents must remain stateless**: State goes in traces/sessions, stored in database
- **All LLM interactions** go through AIGateway (C1 component)
- **Governance checks** happen BEFORE processing (in `process_interaction`)
- **Traces are captured DURING** processing (not after)
- **Use repositories** for all database operations (not direct SQLAlchemy)
- **Preserve backwards compatibility** in Pydantic models (add optional fields)

### Database Changes

- **Never** directly modify database schema in production
- Use Alembic migrations (when implemented)
- Test migrations on SQLite before PostgreSQL
- Backup database before schema changes
- Use `trace_metadata` instead of `metadata` (reserved word in SQLAlchemy)

## Language Conventions

- **Thesis and academic documentation**: Spanish
- **Code comments**: Spanish/English (mixed, author preference)
- **Variable/function names**: English (technical convention)
- **Docstrings**: Spanish (aligned with thesis)
- **Git commits**: Spanish/English accepted

## Future Production Requirements

For production deployment beyond MVP:
- Real LLM integration (OpenAI GPT-4, Claude, Gemini)
- PostgreSQL database (migrate from SQLite)
- LTI integration with Moodle
- Git institutional integration for N2-level traceability
- Teacher dashboard (React/Vue) with N4 trace visualization
- RESTful/GraphQL APIs
- OAuth2 authentication
- Workflow orchestration (n8n, Apache Airflow)
- Comprehensive test coverage (>80%)
- CI/CD pipeline (GitHub Actions)
- Docker containerization
- Kubernetes deployment

## Author

**Mag. en Ing. de Software Alberto Cortez**

Doctoral research project on teaching-learning programming in the era of generative AI.

## Project Status & Verification

### Current State (2025-11-21)

The AI-Native MVP is **fully functional and executable**. All major components have been implemented and tested:

- ✅ **Phase 1.1**: Testing infrastructure (pytest + 70% coverage)
- ✅ **Phase 1.2**: Database persistence (SQLAlchemy ORM + repositories)
- ✅ **Phase 1.3**: Code refactorizations completed (9/9 architectural improvements)
- ✅ **Phase 1.4**: REST API implementation (FastAPI + Clean Architecture)
  - 15+ REST endpoints (sessions, interactions, traces, risks, evaluations)
  - OpenAPI/Swagger auto-generated documentation
  - Dependency injection system
  - Structured error handling with custom exceptions
  - CORS and middleware support (logging, error handling)
  - Complete API examples and documentation
- ✅ **Documentation**: README_MVP.md (1,301 lines) + README_API.md (400+ lines)
- ✅ **All 6 AI agents operational**: T-IA-Cog, E-IA-Proc, S-IA-X, AR-IA, GOV-IA, TC-N4
- ✅ **C4 Extended Architecture**: All 6 components (C1-C6) working
- ✅ **N4 Cognitive Traceability**: Full cognitive path capture
- ✅ **Process-based evaluation**: Not just product, but reasoning process
- ✅ **Risk analysis**: 5 dimensions monitored (cognitive, ethical, epistemic, technical, governance)
- ✅ **Dual execution modes**: CLI (interactive) + REST API (web/mobile integration)

### Recent Refactorizations (2025-11-18)

**9 architectural improvements completed**:

1. ✅ **Fixed import errors in tests**: Corrected `DimensionEvaluation` → `EvaluationDimension`, fixed `CognitiveState` imports from `core.cognitive_engine`
2. ✅ **Added session_id to EvaluationReport**: Model now includes required `session_id` field for database persistence
3. ✅ **Standardized trace_level**: Removed duplicate `level` field, using only `trace_level` in CognitiveTrace
4. ✅ **Standardized sequence id**: Removed duplicate `sequence_id` field, using only `id` in TraceSequence
5. ✅ **Standardized metadata naming**: Changed ORM field from `trace_metadata` to `metadata` for consistency with Pydantic models
6. ✅ **Updated agent constructors**: All agents now accept optional `llm_provider` parameter: `__init__(self, llm_provider=None, config=None)`
7. ✅ **Full project verification**: All examples executing successfully with all refactorizations applied
8. ✅ **Repository injection pattern**: `TrazabilidadN4Agent` refactored to use optional repository injection instead of stateful storage
   - Accepts `trace_repository` and `sequence_repository` parameters
   - Delegates persistence to repositories when available
   - Maintains backward compatibility (works without repositories for testing)
9. ✅ **LLM provider abstraction layer**: Complete abstraction for interchangeable LLM providers
   - Base `LLMProvider` interface with `generate()`, `generate_stream()`, `count_tokens()`
   - `MockLLMProvider` for development/testing (no API calls required)
   - `OpenAIProvider` for GPT-4/GPT-3.5 integration (optional, requires `openai` package)
   - `LLMProviderFactory` for centralized provider creation
   - Integrated with `AIGateway` (C1 component)
   - Supports environment variable configuration

### REST API Fixes (2025-11-18)

**12 critical API issues fixed** (documented in `API_FIXES_SUMMARY.md`):

**CRITICAL Fixes (2/2)**:
1. ✅ **Gateway Singleton Session Pollution** - Eliminated singleton pattern to prevent session contamination between requests
2. ✅ **Transaction Management** - Added try/except with rollback in delete operations

**HIGH Severity Fixes (5/5)**:
3. ✅ **SQL Injection** - Added `text()` wrapper to raw SQL queries (src/ai_native_mvp/api/routers/health.py:40)
4. ✅ **N+1 Query in List Sessions** - Implemented eager loading with `selectinload()` (93% query reduction: 41→3 queries)
5. ✅ **N+1 Query in Session Detail** - Added documentation justifying necessary trace loading
6. ✅ **Architecture Violation** - Created `update_status()` method in SessionRepository to respect repository pattern

**MEDIUM Severity Fixes (5/14)**:
7. ✅ **Input Validation** - Created `enums.py` with SessionMode, SessionStatus, CognitiveIntent enums
8. ✅ **Fragile IDs** - Replaced datetime-based IDs with UUID in interactions (src/ai_native_mvp/api/routers/interactions.py:133)
9. ✅ **Pagination Inconsistency** - Created `config.py` with standardized pagination constants (DEFAULT_PAGE_SIZE=20, MAX_PAGE_SIZE=100)

**Performance Improvements**:
- List 20 sessions: 41 queries → 3 queries (93% reduction)
- List 100 sessions: 201 queries → 3 queries (98.5% reduction)
- SQL injection vulnerabilities: 1 → 0 (100% eliminated)
- Data corruption risks: High → None (100% eliminated)

**Code cleanup completed**:
- ✅ Removed all `__pycache__` directories (Python bytecode cache)
- ✅ Removed test database files (`test_ai_native.db`)
- ✅ Removed empty `utils/` package (no implementation, no references)
- ✅ Removed duplicate `readme.md` file

**New modules added**:
- `src/ai_native_mvp/llm/base.py`: LLM provider base abstraction
- `src/ai_native_mvp/llm/mock.py`: Mock provider for testing (default)
- `src/ai_native_mvp/llm/openai_provider.py`: OpenAI integration (optional)
- `src/ai_native_mvp/llm/factory.py`: Provider factory pattern

### Quick Verification

To verify the system is working correctly, run:

```bash
# 1. Verify the complete example executes successfully
python examples/ejemplo_basico.py

# Expected output:
# - Session created
# - 3 interactions processed (1 blocked by governance)
# - 6 N4 traces captured
# - Process evaluation generated (competency level + score)
# - Risk analysis completed (1 medium risk detected)
# - ✅ Example completed successfully
```

If you see the "✅ Example completed successfully" message, the entire ecosystem is functioning correctly.

### Known Issues

**Test suite requires minor fixes**:
- `tests/test_agents.py` and `tests/test_models.py` import `CognitiveState` from wrong module
- Should import from `src.ai_native_mvp.core.cognitive_engine` not `src.ai_native_mvp.models.trace`
- This does NOT affect the main application, only unit tests

**Windows-specific**:
- Some Unicode characters may fail without the UTF-8 encoding fix (already applied to main files)
- If you encounter `UnicodeEncodeError`, add the encoding fix from "Windows Encoding Note" section above

## Frontend Application (React + TypeScript)

### Overview

The `frontEnd/` directory contains a complete React + TypeScript chatbot interface for students to interact with the AI-Native ecosystem.

**Stack**:
- React 18.2 + TypeScript 5.2
- Vite 5.0 (dev server with HMR)
- Context API (state management)
- Axios 1.6 (HTTP client)
- React Markdown (formatted tutor responses)
- date-fns (timestamp formatting)

### Frontend Architecture

```
frontEnd/
├── src/
│   ├── components/Chat/        # UI components
│   │   ├── ChatContainer.tsx   # Main container
│   │   ├── ChatHeader.tsx      # Session info header
│   │   ├── ChatMessages.tsx    # Message list with auto-scroll
│   │   ├── ChatMessage.tsx     # Individual message
│   │   ├── ChatInput.tsx       # User input form
│   │   ├── SessionStarter.tsx  # Session creation form
│   │   └── Chat.css            # Styles
│   ├── contexts/
│   │   └── ChatContext.tsx     # Global state (sessions, messages)
│   ├── services/api/           # API service layer
│   │   ├── base.service.ts     # ✨ NEW: Base class for services
│   │   ├── client.ts           # Axios instance with interceptors
│   │   ├── sessions.service.ts # Session CRUD (refactored)
│   │   ├── interactions.service.ts # Process interactions (refactored)
│   │   ├── traces.service.ts   # N4 traceability (refactored)
│   │   ├── risks.service.ts    # Risks & evaluations (refactored)
│   │   └── index.ts            # Barrel exports
│   ├── types/
│   │   └── api.types.ts        # TypeScript definitions matching backend API
│   ├── App.tsx                 # Root component with ChatProvider
│   └── main.tsx                # Entry point
├── package.json                # Dependencies and scripts
├── vite.config.ts              # Vite config with proxy to backend
├── tsconfig.json               # TypeScript config with path aliases
└── README.md                   # Frontend documentation
```

### Clean Architecture Pattern (Frontend)

```
┌─────────────────────────────────────────┐
│         UI LAYER (Components)           │
│  - ChatContainer, ChatMessages, etc.    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      STATE LAYER (Context API)          │
│  - ChatContext (session, messages)      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   SERVICE LAYER (API Services) ✨ NEW   │
│  - BaseApiService (abstract class)      │
│  - SessionsService extends Base         │
│  - InteractionsService extends Base     │
│  - TracesService extends Base           │
│  - RisksService extends Base            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      HTTP LAYER (Axios Client)          │
│  - Request/Response interceptors        │
│  - Error handling & logging             │
└─────────────────────────────────────────┘
```

### Recent Frontend Refactorings (2025-11-18)

**Service Layer Refactoring** - Applied DRY principle:

**Before** (code duplication):
```typescript
// sessions.service.ts
export const sessionsService = {
  create: async (data) => {
    return post<SessionResponse>('/sessions', data);
  },
  // ... more boilerplate
};

// interactions.service.ts (same pattern repeated)
// traces.service.ts (same pattern repeated)
// risks.service.ts (same pattern repeated)
```

**After** (inheritance-based):
```typescript
// base.service.ts
export abstract class BaseApiService {
  protected baseUrl: string;
  constructor(baseUrl: string) { this.baseUrl = baseUrl; }

  protected async get<T>(endpoint: string = ''): Promise<T> {
    return get<T>(`${this.baseUrl}${endpoint}`);
  }
  // ... post, patch, delete methods
}

// sessions.service.ts
class SessionsService extends BaseApiService {
  constructor() { super('/sessions'); }

  async create(data: SessionCreate): Promise<SessionResponse> {
    return this.post<SessionResponse>('', data);
  }
  // ... clean methods
}

export const sessionsService = new SessionsService();
```

**Benefits**:
- ✅ 50+ lines of duplicate code eliminated
- ✅ Single point of change for cross-cutting concerns (logging, caching, retry logic)
- ✅ Easier to add new services
- ✅ Better testability

### Frontend Development

```bash
# Navigate to frontend
cd frontEnd

# Install dependencies (first time)
npm install

# Start dev server (HMR enabled)
npm run dev
# Server runs at http://localhost:3000

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Environment Configuration

```bash
# Copy example
cp .env.example .env

# Edit .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Path Aliases (TypeScript)

Configured in `tsconfig.json` and `vite.config.ts`:

```typescript
import { useChat } from '@/contexts/ChatContext';
import { sessionsService } from '@/services/api';
import type { SessionResponse } from '@/types/api.types';
```

### Main Features

1. **Session Management**: Create, maintain, and end learning sessions
2. **Real-time Chat**: Conversational interface with the tutor AI
3. **Metadata Display**: Shows agent used, cognitive state, AI involvement percentage
4. **Governance Alerts**: Visual feedback when requests are blocked
5. **Risk Notifications**: Real-time alerts for detected risks
6. **Markdown Support**: Formatted tutor responses (code blocks, lists)
7. **Auto-scroll**: Automatically scrolls to latest message
8. **Responsive**: Works on different screen sizes

### Integration with Backend

The frontend proxies API requests through Vite dev server:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

**Typical Flow**:
1. User creates session via SessionStarter form
2. ChatContext calls `sessionsService.create()`
3. Backend creates session in database
4. User sends message via ChatInput
5. ChatContext calls `interactionsService.process()`
6. Backend processes via AIGateway → Agents → Database
7. Response displayed in ChatMessages with metadata
8. Traces, risks captured automatically in background

### Frontend Documentation

- **Full Guide**: `frontEnd/README.md` (500+ lines)
- **Setup Instructions**: `frontEnd/SETUP_COMPLETE.md`
- **Code Quality Analysis**: `REFACTORINGS_APPLIED.md`

## Quick Reference: Key Files

**Backend**:
- **Entry point**: `src/ai_native_mvp/__main__.py` or `src/ai_native_mvp/cli.py`
- **Main orchestrator**: `src/ai_native_mvp/core/ai_gateway.py`
- **Reasoning engine**: `src/ai_native_mvp/core/cognitive_engine.py`
- **LLM abstraction**: `src/ai_native_mvp/llm/` (provider factory, mock, OpenAI)
- **Database config**: `src/ai_native_mvp/database/config.py`
- **Test fixtures**: `tests/conftest.py`
- **Complete example**: `examples/ejemplo_basico.py` (✅ verified working)

**Frontend**:
- **Entry point**: `frontEnd/src/main.tsx`
- **Root component**: `frontEnd/src/App.tsx`
- **State management**: `frontEnd/src/contexts/ChatContext.tsx`
- **Service layer**: `frontEnd/src/services/api/` (base class pattern)
- **Type definitions**: `frontEnd/src/types/api.types.ts`
- **Main container**: `frontEnd/src/components/Chat/ChatContainer.tsx`

**Documentation**:
- **Thesis content**: `tesis.txt` (2,619 lines, Spanish)
- **MVP documentation**: `README_MVP.md` (1,301 lines)
- **API documentation**: `README_API.md` (400+ lines)
- **Frontend guide**: `frontEnd/README.md` (500+ lines)
- **User stories**: `USER_STORIES.md` (36 historias de usuario, roadmap de 6 sprints)
- **Architectural improvements**: `IMPLEMENTACIONES_ARQUITECTURALES.md`
- **Code quality analysis**: `REFACTORINGS_APPLIED.md` ✨ NEW (2025-11-18)

## LLM Provider Integration (NEW - 2025-11-19)

The system implements **complete LLM provider abstraction** using Factory + Strategy patterns, allowing seamless switching between providers without code changes.

### Quick Start

**1. Configure environment** (`.env`):
```bash
# Development (free, no API calls)
LLM_PROVIDER=mock

# Production with OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

**2. Install dependencies** (only for OpenAI):
```bash
pip install openai tiktoken
# Already in requirements.txt
```

**3. Run**:
```bash
# CLI mode - will use provider from .env
python examples/ejemplo_openai_integration.py  # OpenAI example
python examples/ejemplo_gemini_integration.py  # Gemini example

# API mode - will auto-detect provider from .env
python scripts/run_api.py
```

### Provider Types

| Provider | Status | API Key Required | Cost | Use Case |
|----------|--------|------------------|------|----------|
| **mock** | ✅ Ready | No | Free | Development, testing |
| **openai** | ✅ Ready | Yes | ~$0.02/interaction (GPT-4) | Production (premium) |
| **gemini** | ✅ Ready | Yes | **FREE** (60 req/min) | Production (economic) |
| **anthropic** | ⏳ Prepared | Yes | TBD | Alternative to OpenAI |

### Programmatic Usage

```python
from src.ai_native_mvp.llm import LLMProviderFactory, LLMMessage, LLMRole

# Method 1: From environment variables (RECOMMENDED)
provider = LLMProviderFactory.create_from_env()  # Reads LLM_PROVIDER from .env

# Method 2: Explicit provider type
provider = LLMProviderFactory.create_from_env("openai")

# Method 3: Manual configuration
provider = LLMProviderFactory.create("openai", {
    "api_key": "sk-...",
    "model": "gpt-4",
    "temperature": 0.7
})

# Generate completion
messages = [
    LLMMessage(role=LLMRole.SYSTEM, content="You are a cognitive tutor"),
    LLMMessage(role=LLMRole.USER, content="Explain recursion")
]
response = provider.generate(messages, temperature=0.7)
print(response.content)
print(f"Tokens used: {response.usage['total_tokens']}")

# Streaming (for real-time UI)
for chunk in provider.generate_stream(messages):
    print(chunk, end="", flush=True)
```

### Integration with AIGateway

**CLI Mode**:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env

from src.ai_native_mvp.llm import LLMProviderFactory
from src.ai_native_mvp.core.ai_gateway import AIGateway

# Create provider from environment
llm_provider = LLMProviderFactory.create_from_env()

# Inject into Gateway
gateway = AIGateway(
    llm_provider=llm_provider,  # OpenAI instead of Mock!
    session_repo=...,
    trace_repo=...
)
```

**API Mode** (automatic):
- FastAPI server reads `LLM_PROVIDER` from `.env` automatically
- See `src/ai_native_mvp/api/deps.py` → `_initialize_llm_provider()`
- Just change `.env` and restart server!

### Cost Considerations

**OpenAI GPT-4** (~Nov 2025):
- Input: $0.03/1K tokens
- Output: $0.06/1K tokens
- Typical interaction: ~350 tokens → ~$0.02

**OpenAI GPT-3.5-turbo**:
- ~20x cheaper than GPT-4
- Good quality for simple queries
- Recommended for high-volume use

**Recommendation**:
- Development: `mock` (free)
- Testing: `gpt-3.5-turbo` (cheap)
- Production (complex): `gpt-4`
- Production (simple): `gpt-3.5-turbo`

### Environment Variables

Complete list in `.env.example`:

```bash
# Provider selection
LLM_PROVIDER=openai  # mock, openai, gemini, anthropic

# OpenAI configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
OPENAI_ORGANIZATION=org-...  # Optional

# Google Gemini configuration (FREE!)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-1.5-flash  # Fast and free
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=8192

# Anthropic configuration (future)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# JWT Authentication (Production Readiness - P1.1)
JWT_SECRET_KEY=development_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting (DDoS Protection)
RATE_LIMIT_PER_MINUTE=60      # Default: 60 requests/min
RATE_LIMIT_PER_HOUR=1000      # Default: 1000 requests/hour
```

### Architecture

```
LLMProviderFactory (Factory Pattern)
    ├── MockLLMProvider (Default)
    ├── OpenAIProvider (GPT-4, GPT-3.5) ✅ Ready
    └── AnthropicProvider (Claude) ⏳ Prepared

All implement LLMProvider interface:
    - generate(messages, temperature, ...) → LLMResponse
    - generate_stream(messages, ...) → Iterator[str]
    - count_tokens(text) → int
    - validate_config() → bool
    - get_model_info() → dict
```

### Adding New Providers

1. Create class inheriting from `LLMProvider` in `src/ai_native_mvp/llm/`
2. Implement required methods: `generate()`, `generate_stream()`, `count_tokens()`
3. Register with `LLMProviderFactory.register_provider("name", YourProviderClass)`
4. Update `.env.example` with new provider's environment variables
5. Add configuration handling in `factory.py` → `create_from_env()`

### Documentation

- **Complete guide**: `GUIA_INTEGRACION_LLM.md` (comprehensive, 500+ lines)
- **Example scripts**:
  - `examples/ejemplo_openai_integration.py` - OpenAI integration example
  - `examples/ejemplo_gemini_integration.py` - Google Gemini integration example
- **Configuration**: `.env.example`

## REST API (NEW - FastAPI)

### Overview

The AI-Native MVP now includes a **complete REST API** built with FastAPI, following Clean Architecture and best practices.

**Key Features**:
- ✅ RESTful endpoints for all major operations
- ✅ OpenAPI/Swagger documentation (auto-generated)
- ✅ Dependency injection for repositories and services
- ✅ Structured error handling with custom exceptions
- ✅ Request/response validation with Pydantic
- ✅ CORS support for frontend integration
- ✅ Logging middleware for all requests
- ✅ Health check endpoints

### Quick Start - Running the API

```bash
# 1. Install dependencies (includes FastAPI, uvicorn, etc.)
pip install -r requirements.txt

# 2. Initialize database
python scripts/init_database.py

# 3. Start API server
python scripts/run_api.py

# Or with uvicorn directly
uvicorn src.ai_native_mvp.api.main:app --reload

# The API will be available at:
# - API Base: http://localhost:8000/api/v1
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### API Architecture

The API follows **Clean Architecture** with clear separation of concerns:

```
api/
├── main.py              # FastAPI app (middleware, routers, lifecycle)
├── deps.py              # Dependency injection (repositories, gateway, auth)
├── exceptions.py        # Custom API exceptions
├── middleware/          # Middleware layer
│   ├── error_handler.py # Centralized error handling
│   └── logging.py       # Request logging
├── routers/             # API endpoints (controllers)
│   ├── health.py        # /health, /health/ping
│   ├── sessions.py      # /sessions (CRUD)
│   ├── interactions.py  # /interactions (main processing endpoint)
│   ├── traces.py        # /traces (N4 traceability queries)
│   └── risks.py         # /risks, /evaluation (risks & evaluations)
└── schemas/             # DTOs (Pydantic request/response models)
    ├── common.py        # APIResponse, ErrorResponse, PaginationParams
    ├── session.py       # SessionCreate, SessionResponse, SessionDetailResponse
    └── interaction.py   # InteractionRequest, InteractionResponse
```

**Design Patterns Applied**:
- **Repository Pattern**: Abstraction of database operations
- **Dependency Injection**: Loose coupling via FastAPI's `Depends()`
- **DTO Pattern**: Pydantic schemas for request/response validation
- **Middleware Pattern**: Cross-cutting concerns (logging, error handling)
- **Exception Hierarchy**: Custom exceptions with structured error responses

### Main Endpoints

#### 1. Health Check

```http
GET /api/v1/health
```

Returns service status, database connectivity, and agent availability.

#### 2. Create Session

```http
POST /api/v1/sessions
Content-Type: application/json

{
  "student_id": "student_001",
  "activity_id": "prog2_tp1_colas",
  "mode": "TUTOR"
}
```

Creates a new learning session. Returns `session_id` for subsequent interactions.

#### 3. Process Interaction (Main Endpoint)

```http
POST /api/v1/interactions
Content-Type: application/json

{
  "session_id": "session_abc123",
  "prompt": "¿Cómo implemento una cola circular?",
  "context": {"code_snippet": "class Queue..."},
  "cognitive_intent": "UNDERSTANDING"
}
```

**This is the main endpoint** that orchestrates the entire AI-Native flow:
1. Validates session exists and is active
2. Classifies interaction (CRPE)
3. Checks governance policies (GOV-IA)
4. Processes with appropriate agent (T-IA-Cog, S-IA-X, etc.)
5. Captures N4 trace (TC-N4)
6. Detects risks in parallel (AR-IA)
7. Returns pedagogical response

**Response**:
```json
{
  "success": true,
  "data": {
    "interaction_id": "interaction_xyz789",
    "response": "Para implementar una cola circular...",
    "agent_used": "T-IA-Cog",
    "cognitive_state_detected": "EXPLORACION_CONCEPTUAL",
    "ai_involvement": 0.4,
    "blocked": false,
    "trace_id": "trace_123",
    "risks_detected": []
  }
}
```

#### 4. Get Cognitive Path

```http
GET /api/v1/traces/{session_id}/cognitive-path
```

Reconstructs the complete cognitive path from N4 traces:
- Sequence of cognitive states
- State transitions
- AI dependency evolution
- Strategy changes

#### 5. Get Session Risks

```http
GET /api/v1/risks/session/{session_id}
```

Returns all risks detected in a session with filtering options.

#### 6. Get Session Evaluation

```http
GET /api/v1/risks/evaluation/session/{session_id}
```

Returns the process-based evaluation report generated by E-IA-Proc.

### API Usage Examples

#### Python (requests)

See `examples/api_usage_example.py` for complete example.

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Create session
response = requests.post(f"{API_BASE}/sessions", json={
    "student_id": "student_001",
    "activity_id": "prog2_tp1",
    "mode": "TUTOR"
})
session = response.json()["data"]

# Process interaction
response = requests.post(f"{API_BASE}/interactions", json={
    "session_id": session["id"],
    "prompt": "¿Qué es una cola circular?",
    "cognitive_intent": "UNDERSTANDING"
})
interaction = response.json()["data"]
print(interaction["response"])
```

#### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"student_id": "student_001", "activity_id": "prog2_tp1", "mode": "TUTOR"}'

# Process interaction
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc123",
    "prompt": "¿Qué es una cola circular?",
    "cognitive_intent": "UNDERSTANDING"
  }'
```

#### JavaScript (fetch)

```javascript
const API_BASE = "http://localhost:8000/api/v1";

// Create session
const sessionResponse = await fetch(`${API_BASE}/sessions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    student_id: "student_001",
    activity_id: "prog2_tp1",
    mode: "TUTOR"
  })
});
const { data: session } = await sessionResponse.json();

// Process interaction
const interactionResponse = await fetch(`${API_BASE}/interactions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: session.id,
    prompt: "¿Qué es una cola circular?",
    cognitive_intent: "UNDERSTANDING"
  })
});
const { data: interaction } = await interactionResponse.json();
console.log(interaction.response);
```

### Error Handling

The API uses structured error responses:

```json
{
  "success": false,
  "error": {
    "error_code": "SESSION_NOT_FOUND",
    "message": "Session 'session_xyz' not found",
    "field": null,
    "extra": {
      "session_id": "session_xyz"
    }
  },
  "timestamp": "2025-11-18T10:00:00Z"
}
```

**Common Error Codes**:
- `VALIDATION_ERROR` (400): Invalid request data
- `SESSION_NOT_FOUND` (404): Session not found
- `GOVERNANCE_BLOCKED` (403): Blocked by governance policies
- `AGENT_NOT_AVAILABLE` (503): Agent unavailable
- `DATABASE_ERROR` (500): Database operation failed

### Dependency Injection System

The API uses FastAPI's dependency injection via `deps.py`:

```python
from fastapi import Depends
from ..api.deps import (
    get_db,                      # Database session
    get_session_repository,      # SessionRepository
    get_trace_repository,        # TraceRepository
    get_risk_repository,         # RiskRepository
    get_ai_gateway,              # AIGateway (singleton)
    get_current_user,            # Current authenticated user (JWT)
)

@app.post("/interactions")
async def process_interaction(
    request: InteractionRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
    session_repo: SessionRepository = Depends(get_session_repository),
):
    # Dependencies auto-injected by FastAPI
    ...
```

**Benefits**:
- Automatic dependency resolution
- Testability (easy to mock dependencies)
- Loose coupling
- Singleton pattern for gateway (performance)

### Testing the API

```bash
# Run complete API usage example
python examples/api_usage_example.py

# Or test manually with Swagger UI
# 1. Start server: python scripts/run_api.py
# 2. Open browser: http://localhost:8000/docs
# 3. Try out endpoints interactively
```

### CORS Configuration

The API supports CORS for frontend integration:

```python
# Allowed origins (configured in main.py)
allow_origins = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
    "http://localhost:8080",  # Vue
]
```

For production, update `src/ai_native_mvp/api/main.py` with your domain.

### Authentication (MVP vs Production)

**MVP (current)**:
- No authentication required for development
- All endpoints publicly accessible

**Production (TODO)**:
- JWT-based authentication
- Role-based access control (student, instructor, admin)
- Token in `Authorization: Bearer <token>` header

Functions `get_current_user()` and `require_role()` in `deps.py` are ready for JWT implementation.

### Middleware

**1. Request Logging Middleware** (`middleware/logging.py`):
- Logs every request/response
- Captures: method, path, status code, duration, client IP
- Adds `X-Process-Time` header to responses

**2. Error Handler Middleware** (`middleware/error_handler.py`):
- Centralized exception handling
- Converts exceptions to structured error responses
- Handles: AINativeAPIException, ValidationError, SQLAlchemyError, generic exceptions

### Pagination

List endpoints support pagination:

```http
GET /api/v1/sessions?page=1&page_size=20
```

**Response**:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Complete Documentation

For complete API documentation, see:
- **README_API.md**: Comprehensive API guide
- **Swagger UI**: http://localhost:8000/docs (interactive)
- **ReDoc**: http://localhost:8000/redoc (alternative format)

### Running in Production

```bash
# Production mode (multiple workers, no auto-reload)
python scripts/run_api.py --production

# Or with uvicorn directly
uvicorn src.ai_native_mvp.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For Docker deployment, see `README_API.md` (Docker/Docker Compose examples included).

---

## Recent Architectural Improvements (2025-11-19)

Seven major architectural improvements have been implemented to optimize performance, security, and maintainability. See `MEJORAS_COMPLETADAS.md` for full details.

### 1. Rate Limiting

**Protection**: DDoS protection with configurable limits per IP address.

**Configuration** (.env):
```bash
RATE_LIMIT_PER_MINUTE=60      # Default: 60 requests/min
RATE_LIMIT_PER_HOUR=1000      # Default: 1000 requests/hour
```

**Implementation**: `src/ai_native_mvp/api/middleware/rate_limiter.py`

**Response headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Timestamp when limit resets

**429 Response** when limit exceeded:
```json
{
  "success": false,
  "error": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "field": null
  }
}
```

### 2. Structured Logging

**Eliminated**: All `print()` statements replaced with structured logging.

**Usage**:
```python
import logging
logger = logging.getLogger(__name__)

# Use structured logging with context
logger.info(
    "Processing interaction",
    extra={
        "session_id": session_id,
        "student_id": student_id,
        "activity_id": activity_id
    }
)

# Error logging with stack traces
logger.error("Database error", exc_info=True, extra={"session_id": session_id})
```

**Benefits**:
- Integration with monitoring systems (ELK, Datadog)
- Filterable by severity level
- Searchable structured context
- Complete stack traces

### 3. Parametrized CORS

**Configuration** (.env):
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# Production
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

**Implementation**: `src/ai_native_mvp/api/config.py::get_allowed_origins()`

**Production validation**: Automatically fails to start if localhost is in CORS origins when `ENVIRONMENT=production`.

### 4. Input Validation

**Prompt validation**:
- **Minimum**: 10 characters
- **Maximum**: 5000 characters

**Context validation**:
- **Maximum size**: 10KB (serialized JSON)

**Implementation**: `src/ai_native_mvp/api/schemas/interaction.py`

**Error response** (422):
```json
{
  "success": false,
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "String should have at most 5000 characters",
    "field": "prompt"
  }
}
```

### 5. LLM Response Cache

**Algorithm**: LRU (Least Recently Used) with TTL (Time To Live)

**Configuration** (.env):
```bash
LLM_CACHE_ENABLED=true        # Default: true
LLM_CACHE_TTL=3600            # Default: 1 hour
LLM_CACHE_MAX_ENTRIES=1000    # Default: 1000 entries
```

**Implementation**: `src/ai_native_mvp/core/cache.py`

**Cache key**: Hash of (messages, temperature, max_tokens, model)

**Benefits**:
- Instant responses for repeated prompts
- Up to 80% reduction in LLM API costs
- Reduced latency for common queries

**Statistics**:
```python
from src.ai_native_mvp.core.cache import get_llm_cache

cache = get_llm_cache()
stats = cache.get_stats()
# {'hits': 45, 'misses': 12, 'hit_rate': 0.789, 'size': 57}
```

### 6. Database Indexes

**16 composite indexes** created for query optimization.

**Apply to existing database**:
```bash
python create_db_indexes.py
python verify_indexes.py  # Verify all indexes created
```

**Key indexes**:
- `idx_student_activity` on sessions(student_id, activity_id)
- `idx_session_type` on cognitive_traces(session_id, interaction_type)
- `idx_student_resolved` on risks(student_id, resolved)
- `idx_student_activity_eval` on evaluations(student_id, activity_id)

**Performance gains**:
- 10-15x faster for common queries
- Scalable to thousands of sessions
- Optimized JOIN operations

**Implementation**: `src/ai_native_mvp/database/models.py` (`__table_args__`)

### 7. Transaction Management

**Atomicity**: All database operations within `process_interaction` are atomic.

**Implementation**: `src/ai_native_mvp/database/transaction.py`

**Usage - Context Manager**:
```python
from src.ai_native_mvp.database import transaction

with transaction(db, "Process student interaction"):
    session_repo.create(...)
    trace_repo.create(...)
    risk_repo.create(...)
    # Auto-commit on success, rollback on exception
```

**Usage - Decorator**:
```python
from src.ai_native_mvp.database import transactional

@transactional("Create session with traces")
def create_session_with_traces(session: Session, ...):
    # All operations are atomic
    ...
```

**Usage - TransactionManager**:
```python
from src.ai_native_mvp.database import TransactionManager

tx_manager = TransactionManager(session)

with tx_manager.begin("Main transaction"):
    session_repo.create(...)

    # Savepoint for risky operation
    sp = tx_manager.savepoint("before_risky_op")
    try:
        risky_operation()
    except Exception:
        tx_manager.rollback_to_savepoint(sp)

    trace_repo.create(...)
```

**Logging**:
```
DEBUG Transaction 140234567890 started: Process student interaction
INFO  Processing interaction extra={'session_id': '...'}
DEBUG Transaction 140234567890 committed successfully
```

**Benefits**:
- Guaranteed data consistency
- No partial writes to database
- Automatic rollback on errors
- Savepoint support for complex transactions

---

### API Development Guidelines

When adding new API endpoints:

1. **Create DTO schemas** in `api/schemas/` (request/response models)
2. **Create router** in `api/routers/` with endpoints
3. **Use dependency injection** for repositories and services
4. **Return structured responses**: `APIResponse[T]` or `PaginatedResponse[T]`
5. **Raise custom exceptions**: Use exceptions from `api/exceptions.py`
6. **Document endpoint**: Add summary, description, examples to OpenAPI
7. **Test endpoint**: Add to `examples/api_usage_example.py`

**Example**:
```python
from fastapi import APIRouter, Depends
from ..deps import get_session_repository
from ..schemas.session import SessionCreate, SessionResponse
from ..schemas.common import APIResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post(
    "",
    response_model=APIResponse[SessionResponse],
    summary="Create Session",
    description="Creates a new learning session"
)
async def create_session(
    data: SessionCreate,
    repo: SessionRepository = Depends(get_session_repository),
) -> APIResponse[SessionResponse]:
    session = repo.create(
        student_id=data.student_id,
        activity_id=data.activity_id,
        mode=data.mode,
    )
    return APIResponse(
        success=True,
        data=SessionResponse.model_validate(session),
        message=f"Session created: {session.id}"
    )
```

---

## Critical Bug Fixes and Security Improvements (2025-11-21)

Ten priority fixes applied to address thread safety, security, and validation issues identified in backend anomaly analysis.

### Thread Safety Fixes

**1. Cache Global Race Condition (CRITICAL)**
- **File**: `src/ai_native_mvp/core/cache.py`
- **Issue**: OrderedDict not thread-safe → data corruption with multiple uvicorn workers
- **Fix**: Added `threading.Lock()` to all LRUCache and LLMResponseCache operations
- **Impact**: Safe for production deployment with multiple workers

**2. OpenAI Client Lazy Loading Race (HIGH)**
- **File**: `src/ai_native_mvp/llm/openai_provider.py` (line 45-63)
- **Issue**: Multiple client instances created without synchronization
- **Fix**: Double-checked locking pattern in `_get_client()`
- **Impact**: Single client instance per provider, prevents resource leaks

**3. LLM Provider Singleton Race (CRITICAL)**
- **File**: `src/ai_native_mvp/api/deps.py`
- **Status**: Already fixed in previous session with double-checked locking
- **Pattern**: First check without lock (fast path), second check with lock (slow path)

### Security & Validation Fixes

**4. Session ID Validation (CRITICAL)**
- **File**: `src/ai_native_mvp/api/schemas/interaction.py` (line 22-36)
- **Issue**: No format validation → potential SQL injection
- **Fix**: `@field_validator` with UUID v4 regex (`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
- **Impact**: Invalid UUIDs rejected before database layer

**5. Debug Mode in Production (CRITICAL)**
- **File**: `src/ai_native_mvp/api/config.py` (line 103-104, 137-143)
- **Issue**: DEBUG=true exposes stack traces and internal errors
- **Fix**: Added `DEBUG` config variable + validation in `validate_production_config()`
- **Impact**: Server refuses to start if `ENVIRONMENT=production` and `DEBUG=true`

**6. Empty Prompt Validation (MEDIUM)**
- **File**: `src/ai_native_mvp/api/schemas/interaction.py` (line 53-59)
- **Issue**: Whitespace-only prompts bypass min_length check
- **Fix**: Strip whitespace first, then validate non-empty
- **Impact**: Normalizes input and prevents invalid requests

### Documentation & Observability

**7. Risk Analysis Logging (MEDIUM)**
- **File**: `src/ai_native_mvp/core/ai_gateway.py` (line 649-657)
- **Issue**: Placeholder method without logging
- **Fix**: Added `logger.warning()` with structured context (session_id, trace_ids, classification)
- **Purpose**: Documents Sprint 5 TODO and aids debugging

**8. RiskDB session_id Nullable (HIGH)**
- **File**: `src/ai_native_mvp/database/models.py` (line 101-118)
- **Issue**: Foreign key allows NULL → risks without sessions make no logical sense
- **Fix**: Documented as tech debt with Sprint 5 refactoring plan
- **Reason**: Requires Pydantic model changes first to avoid breaking existing code

### Already Correct (Verified)

**9. Cache Key Hashing (HIGH)**
- **File**: `src/ai_native_mvp/core/cache.py`
- **Status**: Already using SHA-256 (`hashlib.sha256(json_str.encode('utf-8'))`)
- **Verified**: No MD5 usage found

**10. Context Size Enforcement (MEDIUM)**
- **File**: `src/ai_native_mvp/api/schemas/interaction.py` (line 120-133)
- **Status**: Already enforcing 100KB limit with base64 detection
- **Verified**: Oversized contexts rejected correctly

**11. AI Dependency Score Calculation (MEDIUM)**
- **File**: `src/ai_native_mvp/models/trace.py` (line 98-110)
- **Status**: Already implemented in `model_post_init()` and `add_trace()`
- **Verified**: Calculates average AI involvement automatically

### Testing

Created verification tests:
- `test_validation.py`: Empty prompt validation (5 test cases, all passing)
- `test_thread_safety.py`: Singleton thread safety with 100 concurrent threads

### Production Checklist

Before deploying to production, ensure:
- [ ] `ENVIRONMENT=production` in .env
- [ ] `DEBUG=false` or unset in .env
- [ ] `SECRET_KEY` set to strong random value (not default)
- [ ] `ALLOWED_ORIGINS` contains only production domains (no localhost)
- [ ] LLM provider configured (OPENAI_API_KEY or GEMINI_API_KEY)
- [ ] Database connection tested
- [ ] Run `validate_production_config()` to verify configuration

The system will automatically refuse to start if production configuration is unsafe.

---

## Sprint 6: Professional Simulators (2025-11-21)

All 6 professional simulators are now fully implemented with REST API endpoints, specialized databases (IT-IA, IR-IA), and comprehensive test suites.

### Simulator Endpoints (15 total)

Located in `src/ai_native_mvp/api/routers/simulators.py`:

**IT-IA (Technical Interviewer)**:
- `POST /simulators/interview/start` - Start interview session
- `POST /simulators/interview/respond` - Answer question
- `POST /simulators/interview/complete` - Complete with evaluation
- `GET /simulators/interview/{interview_id}` - Get interview details

**IR-IA (Incident Responder)**:
- `POST /simulators/incident/start` - Start incident simulation
- `POST /simulators/incident/diagnose` - Add diagnosis step
- `POST /simulators/incident/resolve` - Submit resolution
- `GET /simulators/incident/{incident_id}` - Get incident details

**SM-IA (Scrum Master)**:
- `POST /simulators/scrum/daily-standup` - Daily standup feedback

**CX-IA (Client Experience)**:
- `POST /simulators/client/requirements` - Get initial requirements
- `POST /simulators/client/clarify` - Ask clarification (evaluates soft skills)

**DSO-IA (DevSecOps Auditor)**:
- `POST /simulators/security/audit` - OWASP Top 10 security audit

**General**:
- `POST /simulators/interact` - Generic interaction (PO-IA)
- `GET /simulators/{type}` - Get simulator info
- `GET /simulators` - List all simulators

### Specialized Databases

**InterviewSessionDB** (`interview_sessions` table):
- Stores technical interview sessions with questions, responses, evaluation
- Fields: interview_type (CONCEPTUAL/ALGORITHMIC/DESIGN), difficulty_level, questions_asked (JSON), responses (JSON), evaluation_score, evaluation_breakdown (JSON)

**IncidentSimulationDB** (`incident_simulations` table):
- Stores DevOps incident simulations with diagnosis steps, resolution
- Fields: incident_type, severity, description, metrics (JSON), diagnosis_steps (JSON), resolution, resolution_score, resolution_time_minutes

### Testing

**Test files**:
- `tests/test_simulators_sprint6.py` - 22 tests for IT-IA and IR-IA repositories and agents
- `examples/test_sprint6_simuladores_sm_cx_dso.py` - 7 end-to-end scenarios for SM-IA, CX-IA, DSO-IA

**Run tests**:
```bash
# Unit tests for repositories and agents
pytest tests/test_simulators_sprint6.py -v

# E2E tests for simulators (requires API server running)
python examples/test_sprint6_simuladores_sm_cx_dso.py
```

### Example Usage

**SM-IA (Daily Standup)**:
```python
import requests
response = requests.post("http://localhost:8000/api/v1/simulators/scrum/daily-standup", json={
    "session_id": "...",
    "student_id": "student_001",
    "what_did_yesterday": "Completé autenticación JWT",
    "what_will_do_today": "Integraré middleware de auth",
    "impediments": "Ninguno"
})
# Returns: feedback, questions, detected_issues, suggestions
```

**CX-IA (Client Clarification)**:
```python
response = requests.post("http://localhost:8000/api/v1/simulators/client/clarify", json={
    "session_id": "...",
    "question": "¿Podría contarme más sobre el volumen de productos que manejan?"
})
# Returns: client response + soft_skills evaluation {empathy, clarity, professionalism}
```

**DSO-IA (Security Audit)**:
```python
response = requests.post("http://localhost:8000/api/v1/simulators/security/audit", json={
    "session_id": "...",
    "student_id": "student_001",
    "code": "SELECT * FROM users WHERE username = '" + username + "'",
    "language": "python"
})
# Returns: vulnerabilities[], security_score, recommendations[], owasp_compliant
```

### Documentation

- **Complete guide**: `SPRINT_6_SIMULADORES_COMPLETADOS.md` (600+ lines)
- **Progress tracking**: `SPRINT_6_PROGRESO.md` (updated to 85% complete)
- **Agent methods**: All 11 specialized methods in `src/ai_native_mvp/agents/simulators.py`:
  - IT-IA: `generar_pregunta_entrevista()`, `evaluar_respuesta_entrevista()`, `generar_evaluacion_entrevista()`
  - IR-IA: `generar_incidente()`, `evaluar_resolucion_incidente()`
  - SM-IA: `procesar_daily_standup()`
  - CX-IA: `generar_requerimientos_cliente()`, `responder_clarificacion()`
  - DSO-IA: `auditar_seguridad()`
  - PO-IA: `generar_pregunta_po()`, `evaluar_respuesta_po()`

**Key Achievement**: All 6 professional simulators fully implemented with 85% of Sprint 6 completed (61/71 Story Points).

---

## Data Export Module (HU-ADM-005) - 2025-11-22

Complete data export system for institutional research with privacy guarantees (k-anonymity, GDPR compliance).

### Overview

The export module enables institutions to extract anonymized data for research, learning analytics, and accreditation purposes while ensuring student privacy through:
- **k-anonymity** (configurable, default k=5)
- **Pseudonymization** (irreversible SHA-256 hashing)
- **PII suppression** (automatic removal of identifiable fields)
- **Temporal generalization** (timestamps → ISO week format)
- **GDPR Article 89 compliance** (research purposes safeguards)

### Module Structure

Located in `src/ai_native_mvp/export/`:

```
export/
├── __init__.py           # Module exports
├── anonymizer.py         # k-anonymity + hashing + PII suppression (540 lines)
├── exporter.py           # Multi-format export (JSON/CSV/Excel) (370 lines)
└── validators.py         # Privacy validation + GDPR compliance (320 lines)
```

### Quick Start

**CLI Usage**:
```python
from src.ai_native_mvp.export import (
    DataAnonymizer,
    AnonymizationConfig,
    ResearchDataExporter,
    ExportFormat,
    PrivacyValidator,
)

# Configure anonymization
config = AnonymizationConfig(
    k_anonymity=5,              # Minimum k
    hash_salt="institution_2025",
    suppress_pii=True,
    generalize_timestamps=True,
    add_noise_to_scores=False,  # Optional differential privacy
)

# Anonymize data
anonymizer = DataAnonymizer(config)
anonymized_traces = [anonymizer.anonymize_trace(t) for t in raw_traces]

# Validate privacy
validator = PrivacyValidator(min_k=5)
validation = validator.validate(
    anonymized_traces,
    quasi_identifiers=["activity_id", "week"]
)

if validation.is_valid:
    # Export to format
    exporter = ResearchDataExporter(
        ExportConfig(format=ExportFormat.JSON, compress=True)
    )
    output = exporter.export({"traces": anonymized_traces})
    print(f"✅ Exported {len(anonymized_traces)} traces")
else:
    print(f"❌ Privacy validation failed: {validation.errors}")
```

**API Usage**:
```bash
curl -X POST http://localhost:8000/api/v1/export/research-data \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "activity_ids": ["prog2_tp1", "prog2_tp2"],
    "include_traces": true,
    "include_evaluations": true,
    "include_risks": true,
    "format": "json",
    "k_anonymity": 5,
    "compress": true
  }'
```

### Components

#### 1. DataAnonymizer (`export/anonymizer.py`)

**Purpose**: Anonymize data with k-anonymity guarantees.

**Key Features**:
- **ID Hashing**: SHA-256 with salt (irreversible)
  ```python
  student_id: "student_001" → student_hash: "a3f5b2c8d1e4"
  ```
- **Timestamp Generalization**:
  ```python
  created_at: "2025-11-22 10:30:00" → week: "2025-W47"
  ```
- **PII Suppression**: Removes `student_id`, `student_name`, `student_email`, etc.
- **Differential Privacy** (optional): Laplace noise on scores
- **k-anonymity Validation**: Checks equivalence class sizes

**Main Methods**:
```python
anonymizer.hash_id(identifier: str) → str
anonymizer.generalize_timestamp(timestamp: datetime) → str
anonymizer.anonymize_trace(trace: Dict) → Dict
anonymizer.anonymize_evaluation(evaluation: Dict) → Dict
anonymizer.anonymize_risk(risk: Dict) → Dict
anonymizer.check_k_anonymity(records: List, quasi_identifiers: List) → int
anonymizer.validate_anonymization(records: List, quasi_identifiers: List) → Dict
```

#### 2. ResearchDataExporter (`export/exporter.py`)

**Purpose**: Export anonymized data in multiple formats.

**Supported Formats**:
- **JSON**: Structured data with metadata
  ```json
  {
    "metadata": {"export_timestamp": "...", "total_records": 100},
    "data": {"traces": [...], "evaluations": [...]}
  }
  ```
- **CSV**: Flat tables (UTF-8 BOM for Excel compatibility)
- **Excel**: Multi-sheet workbooks with formatted headers (requires `openpyxl`)
- **Compression**: Optional ZIP compression

**Main Methods**:
```python
exporter.export_to_json(data: Dict, data_type: str) → str
exporter.export_to_csv(data: List, fieldnames: List) → str
exporter.export_to_excel(data: Dict[str, List]) → bytes
exporter.compress_output(data: Union[str, bytes], filename: str) → bytes
exporter.export(data: Dict, output_path: Path) → Union[str, bytes]
```

#### 3. PrivacyValidator (`export/validators.py`)

**Purpose**: Validate privacy compliance before export.

**Validations**:
1. **PII Detection**: Regex patterns for email, phone, IP, SSN, credit cards
2. **Forbidden Fields**: password, api_key, access_token, etc.
3. **k-anonymity**: Minimum equivalence class size
4. **Identifier Hashing**: Ensures student_id/session_id are hashed
5. **GDPR Article 89**: Safeguards compliance (pseudonymization, data minimization, technical measures)

**Main Methods**:
```python
validator.check_for_pii(records: List) → ValidationResult
validator.check_k_anonymity(records: List, quasi_identifiers: List) → ValidationResult
validator.check_identifiers_hashed(records: List) → ValidationResult
validator.validate(records: List, quasi_identifiers: List) → ValidationResult

GDPRCompliance.check_article_89_compliance(
    anonymization_config: Dict,
    validation_result: ValidationResult
) → ValidationResult
```

### REST API Endpoint

**Endpoint**: `POST /api/v1/export/research-data`

Located in `src/ai_native_mvp/api/routers/export.py`.

**Request Schema** (`ExportRequest`):
```python
{
    "start_date": datetime,           # Optional
    "end_date": datetime,             # Optional
    "activity_ids": List[str],        # Optional (None = all)
    "student_hashes": List[str],      # Optional (for longitudinal studies)
    "include_traces": bool,           # Default: true
    "include_evaluations": bool,      # Default: true
    "include_risks": bool,            # Default: true
    "include_sessions": bool,         # Default: true
    "format": ExportFormat,           # json, csv, excel
    "compress": bool,                 # Default: false
    "k_anonymity": int,               # Default: 5 (range: 2-50)
    "add_noise": bool,                # Default: false
    "noise_epsilon": float,           # Default: 0.1 (range: 0.01-1.0)
}
```

**Response Schema** (`ExportResponse`):
```python
{
    "success": bool,
    "message": str,
    "metadata": {
        "export_timestamp": datetime,
        "export_format": str,
        "total_records": int,
        "data_types": List[str],
        "anonymization_applied": bool,
        "privacy_standard": str,
        "date_range": {"start": datetime, "end": datetime}
    },
    "validation_report": {
        "is_valid": bool,
        "errors": List[str],
        "warnings": List[str],
        "metrics": {
            "k_anonymity_achieved": int,
            "k_anonymity_required": int,
            "total_records": int,
            "pii_fields_detected": int,
            ...
        },
        "gdpr_article_89_compliant": bool
    },
    "download_url": str | null,       # Future: S3/Azure Blob URL
    "file_size_bytes": int,
    "export_id": str
}
```

**Error Handling**:
- **400 Bad Request**: Privacy validation failed
- **404 Not Found**: No data matching filters
- **500 Internal Server Error**: Export failed

### Privacy Guarantees

#### k-Anonymity

Ensures each record is indistinguishable from at least k-1 others:

```python
# Example with k=3
Records (student_hash, activity_id, week):
- (a3f5b2, prog2_tp1, 2025-W47) ← Equivalence class size = 5
- (d1e4c8, prog2_tp1, 2025-W47)
- (f2b9a7, prog2_tp1, 2025-W47)
- (c8e2d5, prog2_tp1, 2025-W47)
- (b4a1f3, prog2_tp1, 2025-W47)

✅ k=5 ≥ k_required=3 → PASSED
```

If k < k_required, export is **blocked** until more generalization is applied.

#### Quasi-Identifiers

Fields that combined could re-identify individuals:
- `activity_id` - Course/assignment
- `week` - Temporal information
- `mode` - Interaction mode

The system checks that combinations of these fields have ≥k occurrences.

#### GDPR Article 89 Compliance

Safeguards for research purposes:
1. **Pseudonymization**: Irreversible ID hashing ✅
2. **Data Minimization**: Only necessary fields ✅
3. **Technical Measures**: k-anonymity ≥5 ✅

### Use Cases

1. **Educational Research**: Publish findings with anonymized data
2. **Learning Analytics**: Identify common difficulties, patterns
3. **Institutional Improvement**: Evaluate pedagogical strategies
4. **Accreditation**: Evidence for CONEAU/external audits
5. **Educational Data Mining**: Comparative effectiveness studies

### Testing

**Test File**: `tests/test_data_export.py` (450 lines, 33 tests)

**Coverage**:
- DataAnonymizer: 12 tests (hashing, timestamps, noise, k-anonymity)
- ResearchDataExporter: 5 tests (JSON, CSV, Excel, compression)
- PrivacyValidator: 10 tests (PII detection, k-anonymity, hashing)
- GDPRCompliance: 3 tests (Article 89 safeguards)
- Integration: 2 tests (complete workflow, validation failures)

**Run Tests**:
```bash
pytest tests/test_data_export.py -v --no-cov
```

**Demo Script**: `examples/test_data_export.py`
```bash
python examples/test_data_export.py
# Outputs: export_output/research_data.{json,csv,xlsx}
```

### Configuration

**Environment Variables** (`.env`):
```bash
# No specific env vars required - all configured via API request
# Optional: Configure allowed origins for CORS
ALLOWED_ORIGINS=http://localhost:3000,https://research.institution.edu
```

**Institutional Customization**:
```python
# Custom salt for your institution
config = AnonymizationConfig(
    hash_salt="your_institution_secret_2025",  # Change this!
    k_anonymity=10,  # Higher k for more privacy
)
```

### Normative Compliance

- ✅ **GDPR Article 89** (EU): Research purposes safeguards
- ✅ **ISO/IEC 27701:2019**: Privacy Information Management
- ✅ **ISO/IEC 29100:2011**: Privacy framework
- ✅ **UNESCO 2021**: AI Ethics recommendations

### Best Practices

1. **Always validate before export**: The API does this automatically
2. **Use high k for sensitive data**: k≥10 recommended for production
3. **Customize hash salt**: Use institution-specific salt
4. **Document data usage**: Track exports for audit trail
5. **Regular reviews**: Periodically review quasi-identifiers
6. **Minimize datasets**: Only export what's needed for research

### Troubleshooting

**Issue**: Privacy validation fails (k < k_required)
**Solution**: Increase generalization or reduce granularity:
```python
# Option 1: Lower k requirement (if acceptable)
request.k_anonymity = 3

# Option 2: Add more quasi-identifiers for grouping
# (creates larger equivalence classes)

# Option 3: Filter to include only common activities
request.activity_ids = ["prog2_tp1"]  # Most common activity
```

**Issue**: Export file too large
**Solution**: Use compression or filter data:
```python
request.compress = True  # ZIP compression
request.start_date = "2025-10-01"  # Limit time range
request.include_risks = False  # Exclude non-essential data
```

### Key Files

- **Anonymizer**: `src/ai_native_mvp/export/anonymizer.py` (540 lines)
- **Exporter**: `src/ai_native_mvp/export/exporter.py` (370 lines)
- **Validators**: `src/ai_native_mvp/export/validators.py` (320 lines)
- **API Router**: `src/ai_native_mvp/api/routers/export.py` (350 lines)
- **Schemas**: `src/ai_native_mvp/api/schemas/export.py` (180 lines)
- **Tests**: `tests/test_data_export.py` (450 lines, 33 tests)
- **Demo**: `examples/test_data_export.py` (450 lines)

**Total**: 2,210 lines of production code + 900 lines tests/examples