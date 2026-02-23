# SKILL.md — PEI Rule DB Management

## Description
Manage the PEI engineering standards database: create, validate, and seed rules for P&ID validation and generation. Use this skill when working with rule CRUD, seed data, or the validation engine.

## Instructions

### Rule Code Convention
- Lookup rules: `LKP-{SOURCE}-{NNN}` (e.g., LKP-ISA-001, LKP-PIP-001)
- Validate rules: `VAL-{CATEGORY}-{NNN}` (e.g., VAL-EQP-001, VAL-PIP-001)
- Generate rules: `GEN-{CATEGORY}-{NNN}` (e.g., GEN-EQP-001, GEN-TAG-001)

### Categories
symbol, tag, instrument, piping, valve, equipment, safety, layout, completeness, process

### Severity Mapping (from standards language)
- "shall", "must", "required" → error
- "should", "recommended" → warning
- "may", "optional" → info

### condition_json Structure

For validate rules:
```json
{
  "match": "node",
  "where": { "type": "equipment", "subtype": "pump" },
  "check": {
    "downstream_edge": {
      "has_node": { "type": "valve", "subtype": "check_valve" },
      "max_distance": 2
    }
  }
}
```

For generate rules:
```json
{
  "trigger": "node_placed",
  "where": { "type": "equipment", "subtype": "pump" },
  "action": {
    "add_node": { "type": "valve", "subtype": "check_valve", "position": "downstream" },
    "add_edge": { "from": "$trigger_node.discharge", "to": "$new_node.inlet" }
  }
}
```

### Seed Data Location
All seed JSON files go in `db/seeds/`:
- isa_letter_codes.json
- isa_function_letters.json
- equipment_classes.json
- validation_rules.json
- generation_rules.json

### Testing Rules
Every new rule must be testable with:
```python
def test_rule_VAL_EQP_001():
    # Create minimal canonical with pump but no check valve
    canonical = make_test_diagram(nodes=[pump_node], edges=[])
    report = validate(canonical, ruleset)
    assert any(v.rule_code == "VAL-EQP-001" for v in report.violations)
```
