# SKILL.md — PEI Canonical Schema

## Description
Work with the PEI Canonical Diagram schema — the domain data model for P&ID diagrams. Use this skill when creating/modifying diagram types, node types, edge types, or the Canonical ↔ ReactFlow conversion.

## Instructions

### Canonical Schema Version
Current version: 1. Always include `canonical_schema_version: 1` in diagram JSON.

### Node Types and Subtypes

| type | subtypes |
|---|---|
| equipment | tank, centrifugal_pump, reciprocating_pump, metering_pump, reactor, heat_exchanger, vessel, column, compressor, blower, filter, dryer, mixer, conveyor |
| valve | gate_valve, globe_valve, ball_valve, butterfly_valve, check_valve, control_valve, safety_valve, three_way_valve, needle_valve |
| instrument | transmitter, indicator, indicator_controller, alarm_high, alarm_low, switch, element, relay |
| fitting | reducer, tee, blind_flange, expansion_joint |

### Edge Types

| edge type | line style | description |
|---|---|---|
| process | solid 2px black | Main process piping |
| utility | dashed 1.5px black | Utility piping (steam, CW, N2) |
| signal_electrical | dotted 1px black | 4-20mA, HART |
| signal_pneumatic | dotted 1px + X marks | Pneumatic signal |

### Required Node Fields
```typescript
interface CanonicalNode {
  id: string;              // Required, UUID
  type: NodeType;          // Required
  subtype: string;         // Required
  tag: string;             // Required for equipment/instrument
  name?: string;           // Optional
  position: { x: number; y: number }; // Required
  properties: Record<string, any>;     // Flexible
  nozzles?: Nozzle[];      // Equipment only
}
```

### Required Edge Fields
```typescript
interface CanonicalEdge {
  id: string;
  from_node: string;       // Node ID
  from_port?: string;      // Nozzle ID
  to_node: string;
  to_port?: string;
  line_number?: string;    // Required for P&ID, optional for PFD
  properties: {
    size?: string;         // e.g., "6\""
    spec?: string;         // Pipe class e.g., "A1A"
    insulation?: string;
    fluid?: string;
  };
  waypoints?: { x: number; y: number }[];
}
```

### Tag Naming Convention
- Equipment: `{ClassLetter}-{AreaNumber}{SeqNumber}` → P-101, R-201
- Instrument: `{ISALetters}-{LoopNumber}` → TIC-1001, FT-1001
- Valve (hand): `HV-{Number}` → HV-1001
- Valve (control): `{MeasuredVar}V-{LoopNumber}` → FV-1001, TV-1001
- Line: `{Size}"-{FluidCode}-{SeqNumber}-{PipeClass}` → 6"-PLA-001-A2A

### Conversion Rules
- to_canonical(): Strip ReactFlow-specific fields (selected, dragging, measured)
- to_reactflow(): Add ReactFlow handles from nozzles, map edge types to styles
- NEVER lose domain data during round-trip conversion
