# SKILL.md — PEI SVG Symbol Design

## Description
Create and manage SVG symbols for P&ID equipment, valves, and instruments. Use this skill when designing new symbols or modifying existing ones.

## Instructions

### Design Principles
- ISA-5.1 COMPATIBLE but independently designed (copyright safe)
- Monochrome black, stroke-based (no fills except white background)
- Consistent sizing: equipment 60×60px, valves 30×30px, instruments 36×36px
- Stroke width: 2px for outlines, 1px for internal details
- ViewBox: always use viewBox, never fixed width/height

### Symbol Template

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60">
  <!-- Equipment symbol -->
  <g stroke="black" stroke-width="2" fill="none">
    <!-- Main shape here -->
  </g>
  <!-- Connection ports (invisible, for ReactFlow handles) -->
  <!-- Inlet: left center -->
  <!-- Outlet: right center -->
</svg>
```

### Port Positions (for ReactFlow handles)
- Equipment: inlet=left-center, outlet=right-center, top=top-center, bottom=bottom-center
- Valve: inlet=left-center, outlet=right-center
- Instrument: signal_in=bottom-center, signal_out=top-center (or left/right)

### Equipment Symbols (MVP minimum 10)
1. centrifugal-pump.svg — Circle with arrow
2. vessel-vertical.svg — Vertical cylinder with dished heads
3. vessel-horizontal.svg — Horizontal cylinder with dished heads
4. heat-exchanger.svg — Circle with internal lines (TEMA)
5. reactor.svg — Vessel with agitator symbol
6. tank.svg — Open-top rectangle with legs
7. column.svg — Tall vertical vessel with trays
8. compressor.svg — Triangle-like shape
9. filter.svg — Rectangle with internal pattern
10. dryer.svg — Cylinder with heating element

### Valve Symbols (MVP minimum 7)
1. gate-valve.svg — Two triangles meeting at point
2. globe-valve.svg — Two triangles with circle
3. check-valve.svg — Triangle with bar
4. control-valve.svg — Gate valve + actuator circle on top
5. ball-valve.svg — Two triangles with filled circle
6. butterfly-valve.svg — Line with circle
7. safety-valve.svg — Angle valve shape

### Instrument Symbols (MVP minimum 4)
1. field-mounted.svg — Circle (plain)
2. panel-mounted.svg — Circle with horizontal line through middle
3. dcs-shared.svg — Circle inside square
4. plc-mounted.svg — Square (diamond shape is also acceptable)

### Symbol Registry
All symbols must be registered in `frontend/src/symbols/index.ts`:
```typescript
export const SYMBOL_MAP: Record<string, string> = {
  'centrifugal_pump': '/symbols/equipment/centrifugal-pump.svg',
  'gate_valve': '/symbols/valves/gate-valve.svg',
  // ...
};
```
