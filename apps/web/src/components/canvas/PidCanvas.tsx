import React, { useCallback, useEffect, useRef } from 'react';
import ReactFlow, { Background, Controls, MiniMap, Panel, ReactFlowProvider, useReactFlow, BackgroundVariant } from 'reactflow';
import { useCanvasStore } from '../../stores/canvas-store';
import "reactflow/dist/style.css";

import PidNode from "./PidNode";
import { generateTag } from "../../utils/tagGenerator";

const nodeTypes = {
    pid: PidNode
};

const defaultEdgeOptions = {
    type: 'smoothstep',
    style: {
        stroke: '#374151',
        strokeWidth: 2,
    },
};

function Flow() {
    const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode, removeNode, applyAutoLayout } = useCanvasStore();
    const { screenToFlowPosition, fitView } = useReactFlow();
    const [isLayingOut, setIsLayingOut] = React.useState(false);
    const prevNodeCount = useRef(0);

    useEffect(() => {
        if (nodes.length > 0 && prevNodeCount.current === 0) {
            setTimeout(() => fitView({ padding: 0.2, duration: 400 }), 50);
        }
        prevNodeCount.current = nodes.length;
    }, [nodes.length, fitView]);

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();

            const type = event.dataTransfer.getData('application/reactflow/type');
            const subtype = event.dataTransfer.getData('application/reactflow/subtype');
            // We now pass the exact equipmentClass to look up SYMBOL_MAP 
            const equipmentClass = event.dataTransfer.getData('application/reactflow/equipmentClass');

            if (!type || !subtype || !equipmentClass) {
                return;
            }

            const position = screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            });

            // Map type 'equipment' -> node tag prefix 'P-', 'T-', 'V-', etc. and sequentially number
            const newTag = generateTag(equipmentClass, nodes);

            // Create node passing custom requirements
            addNode({
                id: crypto.randomUUID(),
                type: 'pid', // our custom ReactFlow node type
                subtype: subtype,
                tag: newTag,
                position: position,
                equipmentClass: equipmentClass // Pass custom property
            } as any);
        },
        [screenToFlowPosition, addNode, nodes]
    );

    const onNodesDelete = useCallback((deleted: any[]) => {
        deleted.forEach(node => removeNode(node.id));
    }, [removeNode]);

    return (
        <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodesDelete={onNodesDelete}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            connectOnClick={true}
            deleteKeyCode={['Delete', 'Backspace']}
            fitView
            snapToGrid={true}
            snapGrid={[15, 15]}
        >
            <Background variant={BackgroundVariant.Dots} gap={15} size={1} color="#cbd5e1" />
            <Panel position="top-right" className="flex gap-2 z-10">
                <button
                    onClick={async () => {
                        try {
                            setIsLayingOut(true);
                            await applyAutoLayout();
                            setTimeout(() => fitView({ padding: 0.2, duration: 400 }), 100);
                        } finally {
                            setIsLayingOut(false);
                        }
                    }}
                    disabled={nodes.length === 0 || isLayingOut}
                    className="bg-white border border-gray-300 rounded px-2 py-1 text-xs text-blue-600 font-medium hover:bg-gray-50 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Auto Layout"
                >
                    {isLayingOut ? '...' : '✨ Auto Layout'}
                </button>
                <button
                    onClick={() => fitView({ padding: 0.2, duration: 400 })}
                    className="bg-white border border-gray-300 rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-50 shadow-sm"
                    title="Fit View"
                >
                    ⊡ Fit
                </button>
            </Panel>
            <Controls className="bg-white shadow-md rounded border border-gray-200" />
            <MiniMap
                nodeStrokeColor="#94a3b8"
                nodeColor="#f1f5f9"
                maskColor="rgba(248, 250, 252, 0.7)"
                className="bg-white shadow-md rounded overflow-hidden border border-gray-200"
            />
        </ReactFlow>
    );
}

export default function PidCanvas() {
    return (
        <div className="w-full h-full" style={{ width: '100%', height: '100%' }}>
            <ReactFlowProvider>
                <Flow />
            </ReactFlowProvider>
        </div>
    );
}
