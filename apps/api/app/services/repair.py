from typing import List, Dict, Any, Optional
import uuid
import copy
from app.schemas.project import DiagramCanonical, CanonicalNode, CanonicalEdge

def generate_uuid():
    return str(uuid.uuid4())

def apply_repairs(
    canonical: DiagramCanonical, 
    repairs: List[Dict[str, Any]]
) -> DiagramCanonical:
    
    # Deep copy to avoid mutating original if passed by ref
    new_canonical = max_model_copy(canonical)
    
    # Creating lookups
    node_map = {n['id']: n for n in new_canonical.nodes}
    edge_map = {e['id']: e for e in new_canonical.edges}
    
    for repair in repairs:
        action = repair.get("action")
        target_id = repair.get("target_id")
        payload = repair.get("payload", {})
        
        if action == "insert_node_on_edge":
            # 1. Find the edge
            if target_id not in edge_map:
                continue
            
            old_edge = edge_map[target_id]
            src_node = node_map.get(old_edge['from_node'])
            dst_node = node_map.get(old_edge['to_node'])
            
            if not src_node or not dst_node:
                continue
                
            # 2. Create new Node
            new_node_id = f"node-{generate_uuid()}"
            new_node_type = payload.get("type", "valve")
            new_node_subtype = payload.get("subtype", "check_valve")
            
            # Calculate midpoint
            src_pos = src_node.get("position", {"x": 0, "y": 0})
            dst_pos = dst_node.get("position", {"x": 0, "y": 0})
            mid_x = (src_pos["x"] + dst_pos["x"]) / 2
            mid_y = (src_pos["y"] + dst_pos["y"]) / 2
            
            new_node: CanonicalNode = {
                "id": new_node_id,
                "type": new_node_type,
                "subtype": new_node_subtype,
                "tag": f"{new_node_subtype[:2].upper()}-{str(uuid.uuid4())[:4]}",
                "position": {"x": mid_x, "y": mid_y}
            }
            
            # 3. Create two new edges
            edge1: CanonicalEdge = {
                "id": f"edge-{generate_uuid()}",
                "from_node": old_edge['from_node'],
                "to_node": new_node_id,
                "type": old_edge.get("type", "process")
            }
            
            edge2: CanonicalEdge = {
                "id": f"edge-{generate_uuid()}",
                "from_node": new_node_id,
                "to_node": old_edge['to_node'],
                "type": old_edge.get("type", "process")
            }
            
            # 4. Update canonical
            new_canonical.nodes.append(new_node)
            new_canonical.edges.append(edge1)
            new_canonical.edges.append(edge2)
            
            # Remove old edge
            # Note: We need to filter it out from the list later or mark for deletion
            if old_edge in new_canonical.edges:
                new_canonical.edges.remove(old_edge)
                
            # Update maps for subsequent repairs
            node_map[new_node_id] = new_node
            edge_map[edge1['id']] = edge1
            edge_map[edge2['id']] = edge2
            del edge_map[target_id]

    return new_canonical

def max_model_copy(canonical: DiagramCanonical):
    # Pydantic copy or dict deep copy
    if hasattr(canonical, "model_dump"):
        return DiagramCanonical(**canonical.model_dump())
    return DiagramCanonical(**canonical.dict())
