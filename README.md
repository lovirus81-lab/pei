# PEI — Plant Engineering IDE

규격 기반 PFD/P&ID 검증 및 생성 웹 플랫폼

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Git

### Setup
git clone <repo> && cd pei
cd frontend && npm install
cd ../backend && pip install -e ".[dev]"
make db-reset
make dev

### Architecture
- Frontend: React + TypeScript + ReactFlow (port 5173)
- Backend: FastAPI + SQLAlchemy (port 8000)
- DB: SQLite (backend/data/pei.db)

### Docs
See `docs/` for design specifications.