// stores/canvas-store.ts — ReactFlow 렌더링 상태 어댑터
// 도메인 로직은 canvas-domain-store.ts로 이동.
// 이 스토어는 ReactFlow Node[]/Edge[] 렌더링 상태만 관리한다.

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
import { toReactFlow } from '../rendering/adapters/to-reactflow';
import { toCanonical as convertToCanonical } from '../rendering/adapters/to-canonical';
import { applyElkLayout } from '../layout/elk-layout-engine';

interface CanvasState {
    nodes: Node[];
    edges: Edge[];

    onNodesChange: OnNodesChange;
    onEdgesChange: OnEdgesChange;
    onConnect: OnConnect;

    addNode: (node: CanonicalNode) => void;
    removeNode: (nodeId: string) => void;
    updateNodeData: (id: string, data: Record<string, unknown>) => void;
    loadCanonical: (canonical: DiagramCanonical) => void;
    toCanonical: () => DiagramCanonical;
    /** elkjs로 클라이언트사이드 레이아웃 적용 (백엔드 API 불사용) */
    applyAutoLayout: () => Promise<void>;
    /** 캔버스 명시적 초기화 */
    clearCanvas: () => void;
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
            type: cNode.type === 'equipment' || cNode.type === 'valve' || cNode.type === 'instrument' ? 'pid' : (cNode.type || 'pid'),
            position: cNode.position,
            data: {
                label: cNode.tag || cNode.subtype,
                subtype: cNode.subtype,
                equipmentClass: (cNode as Record<string, unknown>).equipmentClass || cNode.subtype
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

    updateNodeData: (id: string, data: Record<string, unknown>) => {
        set({
            nodes: get().nodes.map(node => {
                if (node.id === id) {
                    return { ...node, data: { ...node.data, ...data } };
                }
                return node;
            })
        });
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
            // elkjs 클라이언트사이드 레이아웃 (백엔드 API 불사용)
            const positioned = await applyElkLayout(currentDiagram);
            get().loadCanonical(positioned);
        } catch (error) {
            console.error("ELK Auto Layout Failed", error);
            throw error;
        }
    },

    clearCanvas: () => {
        set({ nodes: [], edges: [] });
    },
}));
