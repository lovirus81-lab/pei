import { Handle, Position, type NodeProps } from 'reactflow';

export default function InstrumentNode({ data, selected }: NodeProps) {
    const borderStyle = selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-transparent';
    const validationStyle = data.validationStatus === 'error' ? 'ring-2 ring-red-500' : '';

    return (
        <div className={`relative ${borderStyle} ${validationStyle} rounded-full`}>
            <div className="w-10 h-10 bg-white border-2 border-gray-800 rounded-full flex items-center justify-center shadow-sm">
                <div className="text-xs font-bold text-center leading-tight">
                    {data.subtype?.substring(0, 2).toUpperCase()}
                    <br />
                    {data.label?.split('-')[1] || '001'}
                </div>
            </div>

            {/* Omnidirectional handles usually, but let's stick to simple vertical/horizontal for now */}
            <Handle type="target" position={Position.Bottom} className="w-2 h-2 !bg-gray-400 opacity-0 hover:opacity-100" />
            <Handle type="source" position={Position.Top} className="w-2 h-2 !bg-gray-400 opacity-0 hover:opacity-100" />
        </div>
    );
}
