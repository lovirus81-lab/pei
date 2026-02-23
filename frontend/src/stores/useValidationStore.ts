import { create } from 'zustand';
import { diagramApi } from '../services/diagram-api';
import type { DiagramCanonical } from '../types/canonical';

export interface Violation {
    rule_code: string;
    severity: string;
    message: string;
    node_id?: string | null;
    edge_id?: string | null;
}

export interface ValidationReport {
    passed: boolean;
    error_count: number;
    warning_count: number;
    violations: Violation[];
}

interface ValidationState {
    report: ValidationReport | null;
    isValidating: boolean;
    lastValidatedAt: Date | null;
    runValidation: (canonical: DiagramCanonical, rulesetId?: string) => Promise<void>;
    clearReport: () => void;
}

export const useValidationStore = create<ValidationState>((set) => ({
    report: null,
    isValidating: false,
    lastValidatedAt: null,

    runValidation: async (canonical: DiagramCanonical, rulesetId?: string) => {
        set({ isValidating: true });
        try {
            const result = await diagramApi.validateDiagram(canonical, rulesetId);
            set({
                report: result,
                isValidating: false,
                lastValidatedAt: new Date()
            });
        } catch (error: any) {
            console.error('Validation failed:', error.response?.data || error);
            set({ isValidating: false });
        }
    },

    clearReport: () => {
        set({ report: null, lastValidatedAt: null });
    }
}));
