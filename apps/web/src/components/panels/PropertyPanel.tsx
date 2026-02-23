import { useCanvasStore } from '../../stores/canvas-store';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

export default function PropertyPanel() {
    const { nodes, updateNodeData } = useCanvasStore();
    const selectedNodes = nodes.filter(n => n.selected);
    const selectedNode = selectedNodes.length === 1 ? selectedNodes[0] : null;

    if (!selectedNode) {
        return (
            <div className="h-full flex flex-col bg-white border-b border-gray-100">
                <div className="p-3 bg-gray-50 border-b border-gray-200 font-semibold text-sm text-gray-700">
                    Properties
                </div>
                <div className="flex-1 flex items-center justify-center p-4 text-xs text-gray-400 text-center">
                    Select a single node to edit properties
                </div>
            </div>
        );
    }

    const data = selectedNode.data || {};

    return (
        <div className="h-full flex flex-col bg-white">
            <div className="p-3 bg-gray-50 border-b border-gray-200 font-semibold text-sm text-gray-700 flex justify-between items-center">
                <span>Properties</span>
                <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">{selectedNode.type}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-5">
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tag / Name</Label>
                    <Input
                        value={data.label || ''}
                        onChange={(e) => updateNodeData(selectedNode.id, { label: e.target.value })}
                        className="text-sm h-8"
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Subtype</Label>
                    <Input
                        value={data.subtype || ''}
                        disabled
                        className="text-sm bg-gray-50 text-gray-500 h-8 font-mono select-all"
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</Label>
                    <Input
                        value={data.description || ''}
                        onChange={(e) => updateNodeData(selectedNode.id, { description: e.target.value })}
                        placeholder="Enter description..."
                        className="text-sm h-8"
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Insulation</Label>
                    <Input
                        value={data.insulation || ''}
                        onChange={(e) => updateNodeData(selectedNode.id, { insulation: e.target.value })}
                        placeholder="e.g. Hot, Cold"
                        className="text-sm h-8"
                    />
                </div>

                <div className="pt-2 mt-2 border-t border-gray-100">
                    <div className="text-[10px] text-gray-400 font-mono break-all">
                        ID: {selectedNode.id}
                    </div>
                </div>
            </div>
        </div>
    );
}
