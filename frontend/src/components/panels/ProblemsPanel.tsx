import { useValidationStore } from '../../stores/useValidationStore';

export default function ProblemsPanel() {
    const { report, isValidating } = useValidationStore();

    if (!report && !isValidating) return null;

    if (isValidating) {
        return (
            <div className="h-48 bg-white border-t border-gray-200 p-4">
                Validating...
            </div>
        );
    }

    const { violations, error_count, warning_count } = report!;

    return (
        <div className="h-48 bg-white border-t border-gray-200 flex flex-col">
            <div className="p-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center text-sm">
                <span className="font-bold">Problems</span>
                <div className="flex gap-2">
                    <span className="text-red-500">{error_count} Errors</span>
                    <span className="text-yellow-600">{warning_count} Warnings</span>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
                {violations.length === 0 ? (
                    <div className="text-green-600 text-sm">No problems found.</div>
                ) : (
                    <table className="w-full text-sm text-left">
                        <thead>
                            <tr className="text-gray-500 border-b">
                                <th className="py-1">Code</th>
                                <th>Message</th>
                                <th>Node / Edge</th>
                            </tr>
                        </thead>
                        <tbody>
                            {violations.map((v, idx) => (
                                <tr key={idx} className="border-b hover:bg-gray-50 group cursor-pointer transition-colors">
                                    <td className="py-1 font-mono text-xs text-gray-500">{v.rule_code}</td>
                                    <td>
                                        <div className="flex items-center gap-2">
                                            {v.severity === 'error' ? '🔴' : (v.severity === 'warning' ? '⚠️' : 'ℹ️')}
                                            {v.message}
                                        </div>
                                    </td>
                                    <td className="text-gray-500">{v.node_id || v.edge_id || '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
