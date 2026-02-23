import { create } from 'zustand';
import {
    type Connection,
    type Edge,
    type EdgeChange,
    type Node,
    type NodeChange,
    addEdge,
    type OnNodesChange,
    type OnEdgesChange,
    type OnConnect,
    applyNodeChanges,
    applyEdgeChanges,
} from 'reactflow';
import { type DiagramCanonical, type CanonicalNode } from '../types/canonical';
import { toReactFlow } from '../converters/to-reactflow';
import { toCanonical as convertToCanonical } from '../converters/to-canonical';

interface CanvasState {
    nodes: Node[];
    edges: Edge[];

    onNodesChange: OnNodesChange;
    onEdgesChange: OnEdgesChange;
    onConnect: OnConnect;

    addNode: (node: CanonicalNode) => void;
    removeNode: (nodeId: string) => void;
    loadCanonical: (canonical: DiagramCanonical) => void;
    toCanonical: () => DiagramCanonical;
    applyAutoLayout: () => Promise<void>;
}

export const useCanvasStore = create<CanvasState>((set, get) => ({
    nodes: [],
    edges: [],

    onNodesChange: (changes: NodeChange[]) => {
        set({
            nodes: applyNodeChanges(changes, get().nodes),
        });
    },

    onEdgesChange: (changes: EdgeChange[]) => {
        set({
            edges: applyEdgeChanges(changes, get().edges),
        });
    },

    onConnect: (connection: Connection) => {
        set({
            edges: addEdge({
                ...connection,
                id: crypto.randomUUID(),
                type: 'smoothstep',
                style: { stroke: '#374151', strokeWidth: 2 }
            }, get().edges),
        });
    },

    addNode: (cNode: CanonicalNode) => {
        const newNode: Node = {
            id: cNode.id,
            // Allow override of type, default 'pid' if unhandled
            type: cNode.type === 'equipment' || cNode.type === 'valve' || cNode.type === 'instrument' ? 'pid' : (cNode.type || 'pid'),
            position: cNode.position,
            data: {
                label: cNode.tag || cNode.subtype,
                subtype: cNode.subtype,
                equipmentClass: (cNode as any).equipmentClass || cNode.subtype
            },
        };

        set({ nodes: [...get().nodes, newNode] });
    },

    removeNode: (nodeId: string) => {
        set((state) => ({
            nodes: state.nodes.filter(n => n.id !== nodeId),
            edges: state.edges.filter(e => e.source !== nodeId && e.target !== nodeId)
        }));
    },

    loadCanonical: (canonical: DiagramCanonical) => {
        if (!canonical || !canonical.nodes) {
            console.error("loadCanonical: invalid canonical diagram", canonical);
            return;
        }
        const { nodes, edges } = toReactFlow(canonical);
        set({ nodes, edges });
    },

    toCanonical: (): DiagramCanonical => {
        const { nodes, edges } = get();

        // delegate to unified converter logic which preserves description/insulation
        return convertToCanonical(nodes, edges, {
            id: "temp",
            name: "Current Diagram",
            diagram_type: "pid"
        });
    },

    applyAutoLayout: async () => {
        const currentDiagram = get().toCanonical();
        if (currentDiagram.nodes.length === 0) return;

        try {
            // we dynamically import to prevent cyclic deps or use injected api since we own services/diagram-api.ts here:
            const { diagramApi } = await import('../services/diagram-api');
            const data = await diagramApi.autoLayout(currentDiagram);
            if (data && data.diagram) {
                get().loadCanonical(data.diagram);
            }
        } catch (error) {
            console.error("Auto Layout Failed", error);
            throw error;
        }
    }
}));
