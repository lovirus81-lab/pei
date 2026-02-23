import json
import re
from typing import Any, List

from app.schemas.canonical import DiagramCanonical, CanonicalNode, CanonicalEdge
from app.schemas.rules import ValidationReport, Violation

def _get_downstream_nodes(canonical: DiagramCanonical, node_id: str, max_distance: int) -> List[CanonicalNode]:
    visited = set()
    queue = [(node_id, 0)]
    found = []
    
    while queue:
        curr, dist = queue.pop(0)
        if dist >= max_distance:
            continue
            
        for edge in canonical.edges_from(curr):
            to_node = canonical.node_by_id(edge.to_node)
            if to_node and to_node.id not in visited:
                visited.add(to_node.id)
                found.append(to_node)
                queue.append((to_node.id, dist + 1))
                
    return found

def _get_upstream_nodes(canonical: DiagramCanonical, node_id: str, max_distance: int = 1) -> List[CanonicalNode]:
    visited = set()
    queue = [(node_id, 0)]
    found = []
    
    while queue:
        curr, dist = queue.pop(0)
        if dist >= max_distance:
            continue
            
        for edge in canonical.edges_to(curr):
            from_node = canonical.node_by_id(edge.from_node)
            if from_node and from_node.id not in visited:
                visited.add(from_node.id)
                found.append(from_node)
                queue.append((from_node.id, dist + 1))
                
    return found


def validate(canonical: DiagramCanonical, rules: List[Any]) -> ValidationReport:
    violations: List[Violation] = []
    
    for rule in rules:
        condition_json = rule.condition_json
        if isinstance(condition_json, str):
            try:
                condition = json.loads(condition_json)
            except json.JSONDecodeError:
                continue
        elif isinstance(condition_json, dict):
            condition = condition_json
        else:
            continue
            
        match = condition.get("match")
        if not match:
            continue
            
        severity = getattr(rule, "severity", "error") or "error"
        message_template = getattr(rule, "message_template", f"Rule {rule.code} failed") or f"Rule {rule.code} failed"
        
        if rule.code == "VAL-CMP-002":
            for node in canonical.nodes:
                if node.type.value == "equipment":
                    if not node.description or node.description.strip() == "":
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
            continue
            
        if rule.code == "VAL-PIP-007":
            for edge in canonical.edges:
                if not edge.insulation or edge.insulation.strip() == "":
                    msg = message_template.replace("{edge_id}", edge.id).replace("{line_number}", str(edge.line_number or "Unknown"))
                    violations.append(Violation(
                        rule_code=rule.code,
                        severity=severity,
                        message=msg,
                        node_id=None,
                        edge_id=edge.id
                    ))
            continue
            
        if rule.code == "VAL-INS-007":
            for node in canonical.nodes:
                if node.type.value == "instrument":
                    if getattr(node, "location", None) is None or str(node.location).strip() == "":
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
            continue
        
        where_dict = condition.get("where", {})
        check_dict = condition.get("check", {})
        
        if match == "node":
            # 12. diagram_type_not (Apply to diagram scope before nodes)
            diagram_type_not = check_dict.get("diagram_type_not")
            if diagram_type_not and canonical.diagram_type == diagram_type_not:
                continue

            for node in canonical.nodes:
                # Type / Subtype filters
                node_type = where_dict.get("type")
                if node_type:
                    if isinstance(node_type, list) and node.type.value not in node_type:
                        continue
                    elif isinstance(node_type, str) and node.type.value != node_type:
                        continue
                        
                node_subtype = where_dict.get("subtype")
                if node_subtype:
                    if isinstance(node_subtype, list) and node.subtype not in node_subtype:
                        continue
                    elif isinstance(node_subtype, str) and node.subtype != node_subtype:
                        continue
                
                # property filters
                where_props = where_dict.get("properties")
                if where_props:
                    skip = False
                    for pk, pv in where_props.items():
                        if isinstance(pv, dict) and pv.get("not_null"):
                            if pk not in node.properties or node.properties[pk] is None:
                                skip = True
                                break
                        elif node.properties.get(pk) != pv:
                            skip = True
                            break
                    if skip:
                        continue
                        
                # 1. has_field
                if "has_field" in check_dict:
                    field_name = check_dict["has_field"]
                    val = getattr(node, field_name, None)
                    if not val or str(val).strip() == "":
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{field}", field_name).replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
                
                # 2. has_property
                if "has_property" in check_dict:
                    prop_name = list(check_dict["has_property"].keys())[0] if isinstance(check_dict["has_property"], dict) else check_dict["has_property"]
                    if prop_name not in node.properties or node.properties[prop_name] is None:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{property}", prop_name).replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))

                # 3. tag_matches_pattern
                if "tag_matches_pattern" in check_dict:
                    pattern = check_dict["tag_matches_pattern"]
                    if node.tag and not re.match(pattern, node.tag):
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))

                # 4. downstream_node
                if "downstream_node" in check_dict:
                    req_type = check_dict["downstream_node"].get("type")
                    req_subtype = check_dict["downstream_node"].get("subtype")
                    max_dist = check_dict["downstream_node"].get("max_distance", 1)
                    
                    found = False
                    for d_node in _get_downstream_nodes(canonical, node.id, max_dist):
                        match_type = True
                        if req_type and d_node.type.value != req_type:
                            match_type = False
                        if req_subtype:
                            if isinstance(req_subtype, list) and d_node.subtype not in req_subtype:
                                match_type = False
                            elif isinstance(req_subtype, str) and d_node.subtype != req_subtype:
                                match_type = False
                                
                        if match_type:
                            found = True
                            break
                            
                    if not found:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))

                # 5. upstream_node
                if "upstream_node" in check_dict:
                    req_type = check_dict["upstream_node"].get("type")
                    req_subtype = check_dict["upstream_node"].get("subtype")
                    max_dist = check_dict["upstream_node"].get("max_distance", 1)
                    
                    found = False
                    for u_node in _get_upstream_nodes(canonical, node.id, max_dist):
                        match_type = True
                        if req_type and u_node.type.value != req_type:
                            match_type = False
                        if req_subtype:
                            if isinstance(req_subtype, list) and u_node.subtype not in req_subtype:
                                match_type = False
                            elif isinstance(req_subtype, str) and u_node.subtype != req_subtype:
                                match_type = False
                                
                        if match_type:
                            found = True
                            break
                            
                    if not found:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))

                # 6. has_at_least_one_edge
                if check_dict.get("has_at_least_one_edge"):
                    edges_count = len(canonical.edges_from(node.id)) + len(canonical.edges_to(node.id))
                    if edges_count == 0:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
                
                # 7. has_bypass
                if check_dict.get("has_bypass"):
                    # Check if there is a path from upstream to downstream bypassing this node
                    upstream = _get_upstream_nodes(canonical, node.id, 1)
                    downstream = _get_downstream_nodes(canonical, node.id, 1)
                    bypass_found = False
                    for u in upstream:
                        # Find downstream nodes of u ignoring this node
                        u_downstreams = []
                        for edge in canonical.edges_from(u.id):
                            if edge.to_node != node.id:
                                u_downstreams.extend(_get_downstream_nodes(canonical, edge.to_node, 3))
                                u_downstreams.append(canonical.node_by_id(edge.to_node))
                        u_down_ids = {n.id for n in u_downstreams if n}
                        if any(d.id in u_down_ids for d in downstream):
                            bypass_found = True
                            break
                    
                    if not bypass_found:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
                
                # 8. connected_instrument
                if check_dict.get("connected_instrument"):
                    instrument_found = False
                    for edge in canonical.edges_from(node.id) + canonical.edges_to(node.id):
                        if edge.type in [EdgeType.SIGNAL_ELECTRICAL, EdgeType.SIGNAL_PNEUMATIC]:
                            target_id = edge.to_node if edge.from_node == node.id else edge.from_node
                            target_node = canonical.node_by_id(target_id)
                            if target_node and target_node.type == NodeType.INSTRUMENT:
                                instrument_found = True
                                break
                    
                    if not instrument_found:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))
                        
                # 9. connected_node (for VAL-EQP-003)
                if check_dict.get("connected_node"):
                    req_type = check_dict["connected_node"].get("type")
                    req_subtype = check_dict["connected_node"].get("subtype")
                    found = False
                    for edge in canonical.edges_from(node.id) + canonical.edges_to(node.id):
                        target_id = edge.to_node if edge.from_node == node.id else edge.from_node
                        target_node = canonical.node_by_id(target_id)
                        if target_node:
                            if req_type and target_node.type.value != req_type: continue
                            if req_subtype and target_node.subtype != req_subtype: continue
                            found = True
                            break
                    if not found:
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=message_template.replace("{tag}", node.tag or "Unknown"),
                            node_id=node.id,
                            edge_id=None
                        ))

        elif match == "edge":
            for edge in canonical.edges:
                edge_type = where_dict.get("type")
                if edge_type and edge.type.value != edge_type:
                    continue
                
                # 7. has_field
                if "has_field" in check_dict:
                    field_name = check_dict["has_field"]
                    val = getattr(edge, field_name, None)
                    if not val or str(val).strip() == "":
                        msg = message_template.replace("{field}", str(field_name)).replace("{edge_id}", edge.id).replace("{line_number}", str(edge.line_number or "Unknown"))
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=msg,
                            node_id=None,
                            edge_id=edge.id
                        ))

                # 8. has_property
                if "has_property" in check_dict:
                    prop_name = list(check_dict["has_property"].keys())[0] if isinstance(check_dict["has_property"], dict) else check_dict["has_property"]
                    val = getattr(edge.properties, prop_name, None)
                    
                    # Fallback to parse from line_number if missing
                    if (val is None or val == "") and edge.line_number:
                        parts = str(edge.line_number).split("-")
                        if len(parts) >= 3:
                            if prop_name == "size":
                                val = parts[0]
                            elif prop_name == "spec":
                                val = parts[-1]
                    
                    if val in (None, "", " "):
                        msg = message_template.replace("{property}", str(prop_name)).replace("{edge_id}", edge.id).replace("{line_number}", str(edge.line_number or "Unknown"))
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=msg,
                            node_id=None,
                            edge_id=edge.id
                        ))

                # 9. line_number_matches_pattern
                if "line_number_matches_pattern" in check_dict:
                    pattern = check_dict["line_number_matches_pattern"]
                    print(f"[{rule.code}] pattern={pattern}, line_number={edge.line_number}")
                    if edge.line_number and not re.match(pattern, edge.line_number):
                        msg = message_template.replace("{edge_id}", edge.id).replace("{line_number}", str(edge.line_number or "Unknown"))
                        violations.append(Violation(
                            rule_code=rule.code,
                            severity=severity,
                            message=msg,
                            node_id=None,
                            edge_id=edge.id
                        ))

        elif match == "diagram":
            # 10. equipment_tags_unique
            if check_dict.get("equipment_tags_unique"):
                tags = set()
                for node in canonical.nodes:
                    if node.type.value == "equipment" and node.tag:
                        if node.tag in tags:
                            violations.append(Violation(
                                rule_code=rule.code,
                                severity=severity,
                                message=message_template.replace("{tag}", node.tag),
                                node_id=node.id,
                                edge_id=None
                            ))
                        tags.add(node.tag)

            # 11. line_numbers_unique
            if check_dict.get("line_numbers_unique"):
                line_nums = set()
                for edge in canonical.edges:
                    if edge.line_number:
                        if edge.line_number in line_nums:
                            violations.append(Violation(
                                rule_code=rule.code,
                                severity=severity,
                                message=message_template.replace("{line_number}", edge.line_number),
                                node_id=None,
                                edge_id=edge.id
                            ))
                        line_nums.add(edge.line_number)

            # TEST RULE: node_count_min
            if "node_count_min" in check_dict:
                min_count = check_dict["node_count_min"]
                if len(canonical.nodes) < min_count:
                    violations.append(Violation(
                        rule_code=rule.code,
                        severity=severity,
                        message=message_template,
                        node_id=None,
                        edge_id=None
                    ))

    error_count = sum(1 for v in violations if v.severity == "error")
    warning_count = sum(1 for v in violations if v.severity == "warning")
    passed = error_count == 0
    
    return ValidationReport(
        passed=passed,
        error_count=error_count,
        warning_count=warning_count,
        violations=violations
    )
