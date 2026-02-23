import React from 'react';
import { SYMBOL_MAP } from '../../symbols';

export default function SymbolPalette() {
    const onDragStart = (
        event: React.DragEvent,
        nodeType: string,
        subtype: string,
        equipmentClass: string
    ) => {
        event.dataTransfer.setData('application/reactflow/type', nodeType);
        event.dataTransfer.setData('application/reactflow/subtype', subtype);
        event.dataTransfer.setData('application/reactflow/equipmentClass', equipmentClass);
        event.dataTransfer.effectAllowed = 'move';
    };

    // Helper functions to categorize symbols from our map
    const instruments = Object.keys(SYMBOL_MAP).filter((k) => k.includes('mounted') || k.includes('shared'));
    const valves = Object.keys(SYMBOL_MAP).filter((k) => k.includes('valve') && !instruments.includes(k));
    const equipment = Object.keys(SYMBOL_MAP).filter((k) => !instruments.includes(k) && !valves.includes(k));

    return (
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full overflow-hidden shrink-0">
            <div className="p-4 border-b border-gray-200 font-bold bg-gray-50 flex-shrink-0">
                Symbols
            </div>

            <div className="p-3 overflow-y-auto flex-1 text-sm bg-gray-50/50">

                {/* Equipment Section */}
                <div className="mb-6">
                    <div className="text-xs font-bold text-gray-500 mb-3 sticky top-0 bg-gray-50/90 py-1 z-10 border-b">
                        EQUIPMENT ({equipment.length})
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        {equipment.map((key) => (
                            <div
                                key={key}
                                className="p-2 bg-white border border-gray-200 rounded flex flex-col items-center justify-center gap-2 cursor-move hover:shadow-md hover:border-blue-400 transition-all group"
                                onDragStart={(event) => onDragStart(event, 'equipment', key, key)}
                                draggable
                            >
                                <img
                                    src={SYMBOL_MAP[key]}
                                    alt={key}
                                    className="w-8 h-8 object-contain pointer-events-none group-hover:scale-110 transition-transform"
                                />
                                <span className="text-[10px] text-center font-medium text-gray-600 leading-tight">
                                    {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Valves Section */}
                <div className="mb-6">
                    <div className="text-xs font-bold text-gray-500 mb-3 sticky top-0 bg-gray-50/90 py-1 z-10 border-b">
                        VALVES ({valves.length})
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        {valves.map((key) => (
                            <div
                                key={key}
                                className="p-2 bg-white border border-gray-200 rounded flex flex-col items-center justify-center gap-2 cursor-move hover:shadow-md hover:border-blue-400 transition-all group"
                                onDragStart={(event) => onDragStart(event, 'valve', key, key)}
                                draggable
                            >
                                <img
                                    src={SYMBOL_MAP[key]}
                                    alt={key}
                                    className="w-8 h-8 object-contain pointer-events-none group-hover:scale-110 transition-transform"
                                />
                                <span className="text-[10px] text-center font-medium text-gray-600 leading-tight">
                                    {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Instruments Section */}
                <div className="mb-2">
                    <div className="text-xs font-bold text-gray-500 mb-3 sticky top-0 bg-gray-50/90 py-1 z-10 border-b">
                        INSTRUMENTS ({instruments.length})
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        {instruments.map((key) => (
                            <div
                                key={key}
                                className="p-2 bg-white border border-gray-200 rounded flex flex-col items-center justify-center gap-2 cursor-move hover:shadow-md hover:border-blue-400 transition-all group"
                                onDragStart={(event) => onDragStart(event, 'instrument', key, key)}
                                draggable
                            >
                                <img
                                    src={SYMBOL_MAP[key]}
                                    alt={key}
                                    className="w-8 h-8 object-contain pointer-events-none group-hover:scale-110 transition-transform"
                                />
                                <span className="text-[10px] text-center font-medium text-gray-600 leading-tight">
                                    {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
