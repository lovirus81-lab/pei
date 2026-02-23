import { useState } from 'react';
import toast from 'react-hot-toast';
import { useValidationStore } from '../../stores/useValidationStore';
import { useCanvasStore } from '../../stores/canvas-store';
import { diagramApi } from '../../services/diagram-api';

export default function ValidationPanel() {
    const { report, isValidating, lastValidatedAt, runValidation } = useValidationStore();
    const { toCanonical, loadCanonical } = useCanvasStore();
    const [isFixing, setIsFixing] = useState(false);

    if (!report && !isValidating) {
        return (
            <div className="h-full flex flex-col bg-white">
                <div className="p-3 bg-gray-100 border-b border-gray-200 font-bold text-sm text-gray-700">
                    Validation Report
                </div>
                <div className="flex-1 flex items-center justify-center p-4 text-sm text-gray-400 text-center">
                    Validation not run yet.<br />Click "Validate" in the header to check diagram rules.
                </div>
            </div>
        );
    }

    if (isValidating) {
        return (
            <div className="h-full flex flex-col bg-white">
                <div className="p-3 bg-gray-100 border-b border-gray-200 font-bold text-sm text-gray-700">
                    Validation Report
                </div>
                <div className="flex-1 flex items-center justify-center p-4 text-sm text-gray-500 gap-2">
                    <svg className="animate-spin h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running verification checks...
                </div>
            </div>
        );
    }

    if (!report) return null;

    const handleViolationClick = (nodeId?: string | null, edgeId?: string | null) => {
        console.log("Clicked violation for: ", { nodeId, edgeId });
    };

    const handleAutoFix = async () => {
        if (!report || report.violations.length === 0) return;

        setIsFixing(true);
        try {
            const currentCanonical = toCanonical();
            const responseData = await diagramApi.autoRepair(currentCanonical, report.violations);
            console.log("[autofix] repair response:", responseData);

            const repairedDiagram = responseData?.diagram ?? (responseData as any)?.repaired_diagram ?? responseData;
            const changes = responseData?.repairs ?? (responseData as any)?.changes ?? [];

            if (!repairedDiagram?.nodes) {
                toast.error("Auto Fix 응답 구조 오류");
                return;
            }

            // Re-apply to canvas preserving rendering mappings via loadCanonical (which uses toReactFlow)
            loadCanonical(repairedDiagram);

            if (changes && changes.length > 0) {
                toast.success(`Applied ${changes.length} automated fixes!`);
            } else {
                toast('No automated fixes available for these violations.', { icon: 'ℹ️' });
            }

            // Re-run validation on the newly repaired diagram
            await runValidation(repairedDiagram);

        } catch (error) {
            console.error("Auto Fix Error:", error);
            toast.error("Auto Fix failed - please correct violations manually.");
        } finally {
            setIsFixing(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-white border-t border-gray-200">
            {/* Header */}
            <div className="p-3 bg-gray-100 border-b border-gray-200 flex justify-between items-center sticky top-0">
                <div className="font-bold text-sm text-gray-700 flex items-center gap-2">
                    Validation Report
                    {report.passed && <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">Passed</span>}
                    {!report.passed && <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs">Failed</span>}
                </div>
                <div className="text-xs text-gray-500">
                    {report.error_count} Errors / {report.warning_count} Warnings
                </div>
            </div>

            {/* Results Area */}
            <div className="flex-1 overflow-y-auto p-2">
                {report.passed ? (
                    <div className="flex items-center justify-center h-full text-green-600 font-medium py-8 gap-2">
                        <span>✅</span> All checks passed successfully
                    </div>
                ) : (
                    <div className="flex flex-col gap-2">
                        {report.violations.map((v, i) => {
                            const isError = v.severity === 'error';
                            const isWarning = v.severity === 'warning';

                            let bgColor = "bg-blue-50 border-blue-200";
                            let iconColor = "text-blue-500";
                            let icon = "ℹ️";

                            if (isError) {
                                bgColor = "bg-red-50 border-red-200";
                                iconColor = "text-red-500";
                                icon = "🚨";
                            } else if (isWarning) {
                                bgColor = "bg-yellow-50 border-yellow-200";
                                iconColor = "text-yellow-500";
                                icon = "⚠️";
                            }

                            return (
                                <div
                                    key={i}
                                    className={`p-3 border rounded text-sm cursor-pointer hover:shadow-md transition-shadow ${bgColor}`}
                                    onClick={() => handleViolationClick(v.node_id, v.edge_id)}
                                >
                                    <div className="flex justify-between mb-1 items-start">
                                        <div className={`font-semibold ${iconColor} flex items-center gap-1`}>
                                            <span className="text-xs">{icon}</span>
                                            {v.rule_code}
                                        </div>
                                        <div className="text-[10px] text-gray-500 bg-white px-1.5 py-0.5 rounded border border-gray-200">
                                            {v.node_id ? 'Node' : (v.edge_id ? 'Edge' : 'Diagram')}
                                        </div>
                                    </div>
                                    <div className="text-gray-700 text-xs">
                                        {v.message}
                                    </div>
                                </div>
                            );
                        })}

                        {/* Auto Fix Button Container */}
                        <div className="mt-4 pb-2">
                            <button
                                onClick={handleAutoFix}
                                disabled={isFixing}
                                className={`w-full py-2 px-4 rounded font-medium text-sm flex items-center justify-center gap-2 transition-colors ${isFixing
                                    ? "bg-blue-300 text-white cursor-not-allowed"
                                    : "bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                                    }`}
                            >
                                {isFixing ? (
                                    <>
                                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Fixing...
                                    </>
                                ) : (
                                    <>
                                        <span>✨</span> Auto Fix
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>
            {/* Footer timestamp */}
            {lastValidatedAt && (
                <div className="p-2 border-t border-gray-200 text-[10px] text-gray-400 text-right bg-gray-50">
                    Last validated: {lastValidatedAt.toLocaleTimeString()}
                </div>
            )}
        </div>
    );
}
