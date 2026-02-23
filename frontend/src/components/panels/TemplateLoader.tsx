import React, { useState } from 'react';
import { useCanvasStore } from '../../stores/canvas-store';
import { useToast } from '../ui/Toast';
import { diagramApi } from '../../services/diagram-api';
import { toReactFlow } from '../../converters/to-reactflow';

const TEMPLATES = [
    { id: "simple_pump_loop", label: "Simple Pump Loop" },
    { id: "heat_exchange_unit", label: "Heat Exchange Unit" },
    { id: "reactor_system", label: "Reactor System" },
    { id: "distillation_basic", label: "Distillation Basic" }
];

export default function TemplateLoader() {
    const { addToast } = useToast();
    const [isLoading, setIsLoading] = useState(false);

    const handleSelectTemplate = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const templateId = e.target.value;
        if (!templateId) return;

        // Reset selection immediately so the same template can be loaded multiple times
        e.target.value = "";

        setIsLoading(true);

        try {
            const data = await diagramApi.generateTemplate(templateId);
            const canonical = data.diagram;

            // convert CanonicalDiagram to ReactFlow Nodes and Edges
            const { nodes, edges } = toReactFlow(canonical);

            // Overwrite existing canvas completely
            useCanvasStore.setState({ nodes, edges });

            const templateLabel = TEMPLATES.find(t => t.id === templateId)?.label || templateId;
            addToast(`${templateLabel} 템플릿이 로드되었습니다`, "success");
        } catch (error: any) {
            console.error(error);
            const msg = error.response?.data?.detail || "템플릿을 불러오는 데 실패했습니다.";
            addToast(`Error: ${msg}`, "error");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center gap-2">
            <select
                onChange={handleSelectTemplate}
                disabled={isLoading}
                className="px-2 py-1 bg-gray-700 text-white rounded text-sm outline-none border border-gray-600 disabled:opacity-50"
            >
                <option value="">{isLoading ? "Loading..." : "Load Template..."}</option>
                {TEMPLATES.map(t => (
                    <option key={t.id} value={t.id}>
                        {t.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
