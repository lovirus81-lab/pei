import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Tooltip, TooltipContent, TooltipTrigger } from '../ui/tooltip';
import { SYMBOL_MAP } from '../../symbols';

export default function SymbolPalette() {
    const [search, setSearch] = useState('');

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

    const filterKeys = (keys: string[]) => keys.filter(k => k.toLowerCase().includes(search.toLowerCase()));

    const renderItems = (items: string[], type: string) => (
        <div className="grid grid-cols-2 gap-2">
            {items.map((key) => (
                <Tooltip key={key} delayDuration={300}>
                    <TooltipTrigger asChild>
                        <div
                            className="p-2 bg-white border border-gray-200 rounded flex flex-col items-center justify-center gap-2 cursor-move hover:shadow-md hover:border-blue-500 transition-all group"
                            onDragStart={(event) => onDragStart(event, type, key, key)}
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
                    </TooltipTrigger>
                    <TooltipContent side="right" className="text-xs bg-gray-800 text-white">
                        <p>Drag to place <b>{key.replace(/_/g, ' ')}</b></p>
                    </TooltipContent>
                </Tooltip>
            ))}
            {items.length === 0 && (
                <div className="col-span-2 text-center text-xs text-gray-400 py-6">
                    No symbols found for "{search}".
                </div>
            )}
        </div>
    );

    return (
        <div className="w-[300px] bg-white border-r border-gray-200 flex flex-col h-full overflow-hidden shrink-0 shadow-sm z-10">
            <div className="p-4 border-b border-gray-100 bg-white flex flex-col gap-3 flex-shrink-0">
                <h3 className="font-semibold text-gray-800 text-sm">Symbol Library</h3>
                <div className="relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
                    <Input
                        placeholder="Search symbols..."
                        className="pl-9 h-9 text-xs"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <div className="flex-1 overflow-hidden flex flex-col">
                <Tabs defaultValue="equipment" className="w-full h-full flex flex-col">
                    <TabsList className="w-full justify-start rounded-none border-b bg-transparent p-0 h-10 px-2 gap-2 flex-shrink-0 hide-scrollbar overflow-x-auto">
                        <TabsTrigger value="equipment" className="text-[11px] h-8 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:shadow-none rounded-none px-2">Equipment</TabsTrigger>
                        <TabsTrigger value="valves" className="text-[11px] h-8 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:shadow-none rounded-none px-2">Valves</TabsTrigger>
                        <TabsTrigger value="instruments" className="text-[11px] h-8 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:shadow-none rounded-none px-2">Instruments</TabsTrigger>
                    </TabsList>

                    <div className="flex-1 overflow-y-auto p-3 bg-gray-50/50">
                        <TabsContent value="equipment" className="m-0 border-none outline-none">
                            {renderItems(filterKeys(equipment), 'equipment')}
                        </TabsContent>
                        <TabsContent value="valves" className="m-0 border-none outline-none">
                            {renderItems(filterKeys(valves), 'valve')}
                        </TabsContent>
                        <TabsContent value="instruments" className="m-0 border-none outline-none">
                            {renderItems(filterKeys(instruments), 'instrument')}
                        </TabsContent>
                    </div>
                </Tabs>
            </div>
        </div>
    );
}
