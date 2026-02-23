import { Handle, Position, type NodeProps } from 'reactflow';

export default function ValveNode({ data, selected }: NodeProps) {
    const borderStyle = selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent';
    const validationStyle = data.validationStatus === 'error' ? 'ring-2 ring-red-500' :
        data.validationStatus === 'warning' ? 'ring-2 ring-yellow-500' : '';

    // Render different valve types
    const renderIcon = () => {
        switch (data.subtype) {
            case 'check_valve':
                return (
                    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M10 30 L30 10 L30 30 L10 10 Z" fill="white" /> {/* Bowtie with slash? No, check valve is usually an arrow or Z */}
                        {/* Simple Check Valve: >| */}
                        <path d="M5 20 L35 20 M25 10 L25 30 M15 10 L25 20 L15 30 Z" fill="white" />
                    </svg>
                );
            case 'gate_valve':
            default:
                return (
                    <svg width="40" height="20" viewBox="0 0 40 20" fill="none" stroke="currentColor" strokeWidth="2">
                        {/* Bowtie */}
                        <path d="M5 5 L35 15 L35 5 L5 15 Z" fill="white" />
                    </svg>
                );
        }
    };

    return (
        <div className={`relative ${borderStyle} ${validationStyle} rounded-sm`}>
            <div className="flex flex-col items-center">
                {renderIcon()}
                <div className="text-[10px] text-gray-500 font-mono mt-1">{data.label}</div>
            </div>

            {/* Horizontal handles */}
            <Handle type="target" position={Position.Left} className="w-2 h-2 !bg-gray-400 opacity-0 hover:opacity-100" />
            <Handle type="source" position={Position.Right} className="w-2 h-2 !bg-gray-400 opacity-0 hover:opacity-100" />
        </div>
    );
}
