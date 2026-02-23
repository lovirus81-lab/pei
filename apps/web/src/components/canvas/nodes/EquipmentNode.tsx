import { Handle, Position, type NodeProps } from 'reactflow';

export default function EquipmentNode({ data, selected }: NodeProps) {
    // Simple styling based on validation status (not implemented yet)
    const borderStyle = selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-800';

    return (
        <div className={`px-4 py-2 shadow-md rounded-md bg-white border-2 ${borderStyle} min-w-[100px]`}>
            <div className="flex flex-col items-center">
                <div className="text-lg font-bold">□</div>
                <div className="text-xs text-gray-500 uppercase">{data.subtype}</div>
                <div className="font-bold text-sm">{data.label}</div>
            </div>

            {/* Inlet */}
            <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-gray-400" />
            {/* Outlet */}
            <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-gray-400" />
        </div>
    );
}
