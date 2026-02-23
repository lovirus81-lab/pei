# PEI Project Context (Knowledge Base)

## What is PEI?

PEI (Plant Engineering IDE) is a web-based platform for chemical/process plant engineers that validates and generates PFD/P&ID diagrams based on international engineering standards (ISA-5.1, ISO 10628, PIP PIC001).

Think of it as "VS Code for P&ID" — just like VS Code uses language grammar rules to lint code, PEI uses engineering standard rules to validate plant diagrams.

## Key Concept: Standards DB

The core differentiator is the **Standards DB** (규격 DB) — a structured database of engineering rules extracted from international standards. This DB powers both validation ("is this correct?") and generation ("create this for me").

### Rule Types
- **Lookup**: Static reference data (ISA letter codes, PIP equipment classes)
- **Validate**: Condition → judgment rules (pump needs check valve downstream)
- **Generate**: Trigger → auto-placement rules (when pump placed, add check valve)

### Rule Layers (Priority)
- L1: International standards (ISA, ISO) — immutable
- L2: Design practices (pump+check valve) — per process type
- L3: Layout rules (symbol placement) — per diagram
- L4: Company/project rules — overridable
- L5: Process-specific (PLA nitrogen blanket) — conditional

## Data Model

### Diagram = Directed Graph
- Nodes: equipment, valves, instruments, nozzles
- Edges: process pipes, utility pipes, signal lines
- Each node/edge has properties (tag, size, material, etc.)

### Two Schema Layers
- **Canonical** (domain): stored in DB, used for validation/generation/export
- **UI** (ReactFlow): used only for rendering, never stored

### Conversion Flow
```
User edits (ReactFlow) → to_canonical() → DB/validate/generate/export
DB load → canonical → to_reactflow() → render on screen
```

## Validation Engine

The validation engine builds an in-memory graph from canonical JSON, then evaluates each validate-type rule against it using pattern matching:

```
For each validate rule:
  1. Find nodes matching rule.where (e.g., type=pump)
  2. For each matched node, check rule.check condition
  3. If check fails → add violation with severity, message, suggestion
```

## MVP Scope

The MVP demonstrates this workflow with a single example:
1. User describes a plant section in natural language
2. System shows concept confirmation (BFD + conditions table)
3. System generates P&ID (nodes + edges + instruments)
4. System validates against 110 rules
5. System auto-repairs violations (adds missing valves)
6. System exports deliverables (equipment list, line list, etc.)

Example scenario: 30,000 TPA PLA Pellet Plant — Polymerization Section

## Domain Glossary

| Term | Meaning |
|---|---|
| PFD | Process Flow Diagram — high-level process overview |
| P&ID | Piping & Instrumentation Diagram — detailed engineering drawing |
| BFD | Block Flow Diagram — simplest process overview |
| ISA-5.1 | Standard for instrument symbols and identification |
| ISO 10628 | Standard for PFD/P&ID classification and symbols |
| PIP PIC001 | Industry standard for P&ID content and format |
| Tag | Equipment identifier (e.g., P-101 = Pump 101) |
| Line Number | Pipe identifier (e.g., 3"-LAC-001-A1A) |
| PSV | Pressure Safety Valve |
| CSO | Car Sealed Open (valve locked in open position) |
| HTM | Heat Transfer Medium |
| H&MB | Heat & Material Balance |
| FEED | Front-End Engineering Design |
| EPC | Engineering, Procurement, Construction |
| SIL | Safety Integrity Level |

## File Structure Overview

```
pei/
├── frontend/          # React + TS + Vite
│   └── src/
│       ├── components/canvas/    # ReactFlow P&ID editor
│       ├── components/panels/    # Property, Problems, Palette
│       ├── stores/               # Zustand (canvas, validation, project, ui)
│       ├── converters/           # Canonical ↔ ReactFlow
│       ├── reference/            # Cached lookup data from backend
│       ├── symbols/              # SVG symbol library
│       └── types/                # canonical.ts, ui.ts
├── backend/           # FastAPI + Python
│   └── app/
│       ├── api/       # HTTP routes only
│       ├── services/  # Business logic (validator, generator, exporter)
│       ├── schemas/   # Pydantic models (canonical, rules, export)
│       ├── models/    # SQLAlchemy ORM (diagram, ruleset, run)
│       └── core/      # config, database
├── db/seeds/          # Initial rule data (110 rules JSON)
├── docs/              # Architecture, API spec, canonical schema
└── ops/               # docker-compose.yml
```
