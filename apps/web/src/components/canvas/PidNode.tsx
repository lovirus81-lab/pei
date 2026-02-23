import { Handle, Position } from 'reactflow';
import { SYMBOL_MAP } from '../../symbols';

interface PidNodeProps {
    data: {
        label?: string;
        equipmentClass?: string;
    };
    selected?: boolean;
}

export default function PidNode({ data, selected }: PidNodeProps) {
    const { label, equipmentClass } = data;

    // Get symbol path from the map, default to empty if not found
    const symbolPath = equipmentClass ? SYMBOL_MAP[equipmentClass] : undefined;

    const highlightClass = selected ? 'ring-2 ring-blue-500 rounded' : '';

    return (
        <div className={`relative flex flex-col items-center justify-center p-2 bg-transparent ${highlightClass}`}>
            <Handle
                type="target"
                position={Position.Top}
                id="top-target"
                className="w-2 h-2 bg-blue-400"
                style={{ width: 10, height: 10, background: '#555' }}
            />
            <Handle
                type="source"
                position={Position.Right}
                id="right-source"
                className="w-2 h-2 bg-blue-400"
                style={{ width: 10, height: 10, background: '#555' }}
            />
            <Handle
                type="source"
                position={Position.Bottom}
                id="bottom-source"
                className="w-2 h-2 bg-blue-400"
                style={{ width: 10, height: 10, background: '#555' }}
            />
            <Handle
                type="target"
                position={Position.Left}
                id="left-target"
                className="w-2 h-2 bg-blue-400"
                style={{ width: 10, height: 10, background: '#555' }}
            />

            {symbolPath ? (
                <img
                    src={symbolPath}
                    alt={equipmentClass}
                    className="w-20 h-20 object-contain pointer-events-none"
                />
            ) : (
                <div className="w-20 h-20 border border-dashed border-gray-400 flex items-center justify-center text-xs text-gray-400 bg-white">
                    No Symbol
                </div>
            )}

            <div className="mt-1 text-xs font-semibold px-1 bg-white/80 rounded">
                {label || 'Unknown'}
            </div>
        </div>
    );
}
